import sys
import os
import json
import random
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTextEdit, QScrollArea, QLineEdit, QComboBox, QSpinBox,
    QSlider, QCheckBox, QTabWidget, QGroupBox, QFontComboBox, QGridLayout,
    QFrame, QSizePolicy
)
from PyQt5.QtGui import QFont, QColor, QPalette, QTextOption
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QEvent, QTimer
from PyQt5.QtWidgets import QGraphicsDropShadowEffect
import google.generativeai as genai

# Bennett Foddy quotes for response generation
BENNETT_QUOTES = [
    "It's a game about climbing a mountain, and the only way to climb it is to get over it.",
    "The controls are very simple, but the game is very difficult.",
    "You have to be patient, but you also have to be determined.",
    "It's not about winning, it's about the experience.",
    "You can't skip the hard parts, that's the whole point.",
    "The game is meant to be frustrating, but also rewarding.",
    "There's no tutorial, you just have to figure it out.",
    "It's a metaphor for life's challenges.",
    "Every stumble is a lesson; maybe learn something this time.",
    "Keep trying, even if it feels like you're never going to get it.",
    "Only the persistent can overcome this mountain.",
    "Maybe you'll master it—if you're brave enough to face the challenge.",
    "It’s not luck, it’s sheer determination… or maybe just frustration.",
    "Each fall is a step closer to eventually rising up.",
    "Think of it as a test of your endurance and willpower.",
    "Not everyone is meant to conquer the impossible.",
    "Maybe try harder next time... if you dare.",
    "The more you struggle, the sweeter the victory could be.",
    "This isn’t for quitters—are you in or out?",
    "If you think it's easy, you're in for a rude awakening.",
    "Tough times build strong players; prove your mettle.",
    "You might fail a hundred times, but each failure is a stepping stone.",
    "This challenge separates the dreamers from the doers.",
    "Only the relentless get to the top.",
    "Keep going—you might surprise yourself someday.",
]

CONFIG_FILE = "config.json"
CHAT_DIR = "chat_sessions"

if not os.path.exists(CHAT_DIR):
    os.makedirs(CHAT_DIR)

# Gruvbox Theme Definitions
class GruvboxTheme:
    DARK_SOFT = {
        "name": "Gruvbox Dark Soft",
        "window_bg": "#282828",
        "text": "#ebdbb2",
        "user_bubble": "#458588",  # User bubble background
        "ai_bubble": "#3c3836",    # Gemini bubble background
        "button_bg": "#3c3836",
        "button_hover": "#504945",
        "accent": "#8ec07c",
        "delete": "#fb4934",
        "markdown": "#fe8019",
        "code_bg": "#282828"
    }
    LIGHT_SOFT = {
        "name": "Gruvbox Light Soft",
        "window_bg": "#f2e5bc",
        "text": "#282828",
        "user_bubble": "#d5c4a1",
        "ai_bubble": "#ebdbb2",
        "button_bg": "#ebdbb2",
        "button_hover": "#d5c4a1",
        "accent": "#427b58",
        "delete": "#9d0006",
        "markdown": "#d75f00",
        "code_bg": "#f2e5bc"
    }

# ChatBubble: A bubble that fits the text size.
class ChatBubble(QFrame):
    def __init__(self, text, is_user, theme):
        super().__init__()
        self.is_user = is_user
        self.theme = theme
        self.text = text
        self.init_ui()
        self.apply_style()

    def init_ui(self):
        self.setFrameShape(QFrame.NoFrame)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(12, 8, 12, 8)
        self.label = QLabel(self.text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.layout.addWidget(self.label)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred)
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(15)
        shadow.setOffset(2, 2)
        shadow.setColor(QColor(0, 0, 0, 120))
        self.setGraphicsEffect(shadow)

    def apply_style(self):
        colors = GruvboxTheme.DARK_SOFT if "Dark" in self.theme else GruvboxTheme.LIGHT_SOFT
        bg_color = colors["user_bubble"] if self.is_user else colors["ai_bubble"]
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_color};
                border-radius: 12px;
            }}
            QLabel {{
                color: {colors['text']};
                font-size: 14px;
            }}
        """)

# AIWorker: Handles API requests asynchronously.
class AIWorker(QThread):
    response_stream = pyqtSignal(str)
    
    def __init__(self, prompt, api_key):
        super().__init__()
        self.prompt = prompt
        self.api_key = api_key
        self.model_name = "gemini-2.5-pro-exp-03-25"

    def run(self):
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)
            response = model.generate_content(self.prompt)
            self.response_stream.emit(response.text)
        except Exception as e:
            self.response_stream.emit(f"API Error: {str(e)}")

# HistoryItem: Represents a chat session in history.
class HistoryItem(QWidget):
    deleteClicked = pyqtSignal(str)
    
    def __init__(self, filename, theme):
        super().__init__()
        self.filename = filename
        self.theme = theme
        self.setObjectName("historyItem")
        colors = GruvboxTheme.DARK_SOFT if "Dark" in theme else GruvboxTheme.LIGHT_SOFT
        border_color = colors.get("border", "#665c54")
        text_color = colors["text"]

        layout = QHBoxLayout()
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(12)
        
        text_layout = QVBoxLayout()
        self.title = QLabel(filename.split('.')[0])
        self.title.setStyleSheet(f"font-size: 15px; font-weight: bold; color: {text_color};")
        self.preview = QLabel("Last message preview...")
        self.preview.setStyleSheet(f"font-size: 12px; color: {text_color};")
        self.preview.setWordWrap(True)
        self.preview.setMaximumHeight(40)
        text_layout.addWidget(self.title)
        text_layout.addWidget(self.preview)
        
        delete_btn = QPushButton("🗑")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setCursor(Qt.PointingHandCursor)
        delete_btn.setStyleSheet(f"""
            QPushButton {{
                border: none;
                background-color: transparent;
                color: {colors.get("delete", "#fb4934")};
                font-size: 16px;
            }}
            QPushButton:hover {{
                background-color: {border_color};
                border-radius: 5px;
            }}
        """)
        delete_btn.clicked.connect(lambda: self.deleteClicked.emit(self.filename))
        
        layout.addLayout(text_layout)
        layout.addStretch()
        layout.addWidget(delete_btn)
        self.setLayout(layout)
        self.setStyleSheet(f"""
            QWidget#historyItem {{
                background-color: {colors.get("window_bg", "#282828")};
                border: 1px solid {border_color};
                border-radius: 12px;
            }}
            QWidget#historyItem:hover {{
                background-color: {colors.get("alt_background", "#3c3836")};
            }}
        """)

# ChatClient: Main window with a sticky input box and message bubbles aligned by sender.
class ChatClient(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AUI")
        self.setGeometry(100, 100, 1200, 800)
        os.makedirs(CHAT_DIR, exist_ok=True)
        
        self.current_session_file = None
        self.pending_response = None
        self.config = self.load_config()
        self.theme = self.config.get("theme", "Gruvbox Dark Soft")
        self.font_family = self.config.get("font_family", "JetBrains Mono")
        self.font_size = self.config.get("font_size", 14)
        self.bubble_radius = self.config.get("bubble_radius", 12)
        self.show_timestamps = self.config.get("show_timestamps", False)
        
        # Start a new chat session if none exists
        self.init_ui()
        self.apply_theme()
        if not self.current_session_file:
            self.new_chat()
            

    def init_ui(self):
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.West)
        self.setCentralWidget(self.tabs)
        self.init_chat_tab()
        self.init_history_tab()
        self.init_settings_tab()
        self.init_info_tab()  # New Info tab
        self.refresh_sessions()
        # Install event filter on input field for Ctrl+Enter
        self.input_field.installEventFilter(self)

    # Chat Tab with a sticky input box.
    def init_chat_tab(self):
        self.chat_widget = QWidget()
        main_layout = QVBoxLayout(self.chat_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Scrollable chat area (expands to fill space)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.chat_area = QWidget()
        self.chat_area_layout = QVBoxLayout(self.chat_area)
        self.chat_area_layout.setSpacing(12)
        self.chat_area_layout.addStretch(1)
        self.scroll.setWidget(self.chat_area)
        main_layout.addWidget(self.scroll, 1)
        
        # Input container: fixed at bottom
        self.input_container = QWidget()
        input_layout = QHBoxLayout(self.input_container)
        input_layout.setContentsMargins(10, 5, 10, 5)
        input_layout.setSpacing(10)
        
        self.input_field = QTextEdit()
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setFixedHeight(60)
        self.input_field.setStyleSheet("""
            QTextEdit {
                background-color: #1d2021;
                color: #ebdbb2;
                border: 2px solid #665c54;
                border-radius: 8px;
                padding: 8px;
            }
        """)
        
        send_btn = QPushButton("Send")
        send_btn.setFixedWidth(100)
        send_btn.setStyleSheet("""
            QPushButton {
                background-color: #8ec07c;
                color: #282828;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #a9d18e;
            }
        """)
        send_btn.clicked.connect(lambda: self.button_feedback(send_btn, self.send_message))
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(send_btn)
        main_layout.addWidget(self.input_container, 0)
        self.tabs.addTab(self.chat_widget, "Chat")

    def init_history_tab(self):
        history_tab = QWidget()
        layout = QVBoxLayout(history_tab)
        
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search chats...")
        self.search_bar.textChanged.connect(self.filter_sessions)
        
        self.history_scroll = QScrollArea()
        self.history_scroll.setWidgetResizable(True)
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_scroll.setWidget(self.history_container)
        
        new_chat_btn = QPushButton("➕ New Chat")
        new_chat_btn.clicked.connect(lambda: self.button_feedback(new_chat_btn, self.new_chat))
        
        layout.addWidget(self.search_bar)
        layout.addWidget(self.history_scroll)
        layout.addWidget(new_chat_btn)
        self.tabs.addTab(history_tab, "History")
        self.history_items = []

    def init_settings_tab(self):
        settings_tab = QWidget()
        layout = QVBoxLayout(settings_tab)
        
        # Theme settings
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([GruvboxTheme.DARK_SOFT["name"], GruvboxTheme.LIGHT_SOFT["name"]])
        self.theme_combo.setCurrentText(self.theme)
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        theme_layout.addWidget(self.theme_combo)
        theme_group.setLayout(theme_layout)
        
        # Font settings
        font_group = QGroupBox("Font Settings")
        font_layout = QGridLayout()
        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setCurrentFont(QFont(self.font_family))
        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(8, 24)
        self.font_size_input.setValue(self.font_size)
        font_layout.addWidget(QLabel("Font Family"), 0, 0)
        font_layout.addWidget(self.font_family_combo, 0, 1)
        font_layout.addWidget(QLabel("Font Size"), 1, 0)
        font_layout.addWidget(self.font_size_input, 1, 1)
        font_group.setLayout(font_layout)
        self.font_size_input.valueChanged.connect(self.update_font)
        
        # Bubble settings
        bubble_group = QGroupBox("Chat Appearance")
        bubble_layout = QVBoxLayout()
        self.radius_slider = QSlider(Qt.Horizontal)
        self.radius_slider.setRange(4, 24)
        self.radius_slider.setValue(self.bubble_radius)
        self.radius_slider.valueChanged.connect(self.update_bubble_radius)
        self.timestamp_check = QCheckBox("Show Timestamps")
        self.timestamp_check.setChecked(self.show_timestamps)
        self.timestamp_check.stateChanged.connect(self.toggle_timestamps)
        bubble_layout.addWidget(QLabel("Bubble Radius"))
        bubble_layout.addWidget(self.radius_slider)
        bubble_layout.addWidget(self.timestamp_check)
        bubble_group.setLayout(bubble_layout)
        
        # API settings
        api_group = QGroupBox("API Configuration")
        api_layout = QVBoxLayout()
        self.key_input = QLineEdit()
        self.key_input.setText(self.config.get("api_key", ""))
        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(lambda: self.button_feedback(save_btn, self.save_config))
        api_layout.addWidget(QLabel("API Key"))
        api_layout.addWidget(self.key_input)
        api_layout.addWidget(save_btn)
        api_group.setLayout(api_layout)
        
        layout.addWidget(theme_group)
        layout.addWidget(font_group)
        layout.addWidget(bubble_group)
        layout.addWidget(api_group)
        layout.addStretch()
        self.tabs.addTab(settings_tab, "Settings")

    def init_info_tab(self):
        info_tab = QWidget()
        layout = QVBoxLayout(info_tab)
        info_text = (
            "<h2>Welcome to AUI</h2>"
            "<p>This application allows you to chat with the Gemini AI. "
            "Your messages are saved automatically into individual chat sessions.</p>"
            "<p><b>How to Use:</b></p>"
            "<ul>"
            "<li>Type your message in the input box at the bottom.</li>"
            "<li>Press the <b>Send</b> button or use <b>Ctrl+Enter</b> to send your message.</li>"
            "<li>Your messages will appear as bubbles on the right; responses from Gemini will appear on the left.</li>"
            "<li>Use the <b>History</b> tab to review past chat sessions.</li>"
            "<li>In the <b>Settings</b> tab, you can customize the theme, font, and other appearance settings.</li>"
            "</ul>"
            "<p>Enjoy your chat experience!</p>"
        )
        label = QLabel(info_text)
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignTop)
        layout.addWidget(label)
        layout.addStretch()
        self.tabs.addTab(info_tab, "Info")

    def apply_theme(self):
        self.theme = self.theme_combo.currentText()
        colors = GruvboxTheme.DARK_SOFT if "Dark" in self.theme else GruvboxTheme.LIGHT_SOFT
        style = f"""
            QMainWindow {{ background-color: {colors['window_bg']}; }}
            QWidget {{ background-color: {colors['window_bg']}; color: {colors['text']}; }}
            QPushButton {{ 
                background-color: {colors['button_bg']}; 
                color: {colors['text']}; 
                border-radius: 8px; 
                padding: 8px;
            }}
            QPushButton:hover {{ background-color: {colors['button_hover']}; }}
            QLineEdit, QComboBox, QSpinBox {{ 
                background-color: {colors['button_bg']}; 
                color: {colors['text']}; 
                border-radius: 5px; 
                padding: 6px;
            }}
            QTabBar::tab {{ 
                background: {colors['button_bg']}; 
                color: {colors['accent']}; 
                padding: 15px;
            }}
            QTabBar::tab:selected {{ 
                background: {colors['button_hover']}; 
                border-left: 3px solid {colors['accent']};
            }}
            QScrollArea, QScrollArea > QWidget {{
                background-color: {colors['window_bg']}; 
                color: {colors['text']};
            }}
            QScrollBar:vertical {{
                background: {colors['button_bg']};
                width: 12px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: {colors['button_hover']};
                min-height: 20px;
            }}
        """
        self.setStyleSheet(style)
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(colors['window_bg']))
        palette.setColor(QPalette.WindowText, QColor(colors['text']))
        palette.setColor(QPalette.Base, QColor(colors['button_bg']))
        palette.setColor(QPalette.Text, QColor(colors['text']))
        palette.setColor(QPalette.Button, QColor(colors['button_bg']))
        palette.setColor(QPalette.ButtonText, QColor(colors['text']))
        self.setPalette(palette)
        self.refresh_sessions()
        self.update_font()
        self.update_bubble_radius(self.radius_slider.value())

    def update_font(self):
        self.font_family = self.font_family_combo.currentFont().family()
        self.font_size = self.font_size_input.value()
        self.config.update({
            "font_family": self.font_family,
            "font_size": self.font_size
        })
        self.input_field.setFont(QFont(self.font_family, self.font_size))
        for i in range(self.chat_area_layout.count()):
            container = self.chat_area_layout.itemAt(i).widget()
            if container:
                bubble = container.findChild(ChatBubble)
                if bubble:
                    bubble.label.setFont(QFont(self.font_family, self.font_size))
                    bubble.apply_style()

    def update_bubble_radius(self, value):
        self.bubble_radius = value
        self.config["bubble_radius"] = value
        for i in range(self.chat_area_layout.count()):
            container = self.chat_area_layout.itemAt(i).widget()
            if container:
                bubble = container.findChild(ChatBubble)
                if bubble:
                    bubble.setStyleSheet(bubble.styleSheet() + f"border-radius: {value}px;")

    def toggle_timestamps(self, state):
        self.show_timestamps = bool(state)
        self.config["show_timestamps"] = self.show_timestamps

    def save_config(self):
        self.config.update({
            "api_key": self.key_input.text(),
            "theme": self.theme,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "bubble_radius": self.bubble_radius,
            "show_timestamps": self.show_timestamps
        })
        with open(CONFIG_FILE, "w") as f:
            json.dump(self.config, f)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        return {
            "api_key": "",
            "theme": "Gruvbox Dark Soft",
            "font_family": "JetBrains Mono",
            "font_size": 14,
            "bubble_radius": 12,
            "show_timestamps": False
        }

    def new_chat(self):
        filename = f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        self.current_session_file = os.path.join(CHAT_DIR, filename)
        self.clear_chat_area()

    def clear_chat_area(self):
        for i in reversed(range(self.chat_area_layout.count())):
            widget = self.chat_area_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.pending_response = None

    def load_session(self, item):
        path = os.path.join(CHAT_DIR, item.text())
        self.current_session_file = path
        self.clear_chat_area()
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith("[") and "]:" in line:
                    sender_part, message = line.split("]:", 1)
                    sender = sender_part.strip("[").strip()
                    self.append_message(sender, message.strip(), save=False)

    def refresh_sessions(self):
        for i in reversed(range(self.history_layout.count())):
            widget = self.history_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        self.history_items.clear()
        for file in sorted(os.listdir(CHAT_DIR), reverse=True):
            item = HistoryItem(file, self.theme)
            item.deleteClicked.connect(self.delete_session)
            self.history_layout.addWidget(item)
            self.history_items.append(item)

    def filter_sessions(self):
        query = self.search_bar.text().lower()
        for item in self.history_items:
            visible = query in item.filename.lower()
            item.setVisible(visible)

    def delete_session(self, filename):
        path = os.path.join(CHAT_DIR, filename)
        if os.path.exists(path):
            os.remove(path)
            self.refresh_sessions()

    # append_message wraps each ChatBubble in a horizontal container for alignment.
    def append_message(self, sender, message, save=True):
        timestamp = datetime.now().strftime("%H:%M") if self.show_timestamps else ""
        formatted_msg = f"[{sender} at {timestamp}]\n{message}" if timestamp else f"[{sender}]\n{message}"
        is_user = (sender == "You")
        bubble = ChatBubble(formatted_msg, is_user, self.theme)
        bubble.setFont(QFont(self.font_family, self.font_size))
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        if is_user:
            h_layout.addStretch(1)
            h_layout.addWidget(bubble)
        else:
            h_layout.addWidget(bubble)
            h_layout.addStretch(1)
        self.chat_area_layout.insertWidget(self.chat_area_layout.count()-1, container)
        if save and self.current_session_file:
            with open(self.current_session_file, "a", encoding='utf-8') as f:
                f.write(f"{formatted_msg}\n")

    def show_generating(self):
        quote = random.choice(BENNETT_QUOTES)
        self.pending_response = ChatBubble(
            f"Generating response......\n\"{quote}\" ~ Bennet Foddy",
            False,
            self.theme
        )
        container = QWidget()
        h_layout = QHBoxLayout(container)
        h_layout.setContentsMargins(0, 0, 0, 0)
        h_layout.addWidget(self.pending_response)
        h_layout.addStretch(1)
        self.chat_area_layout.insertWidget(self.chat_area_layout.count()-1, container)

    def send_message(self):
        text = self.input_field.toPlainText().strip()
        if not text:
            return
        self.append_message("You", text)
        self.input_field.clear()
        self.show_generating()
        self.worker = AIWorker(text, self.key_input.text())
        self.worker.response_stream.connect(self.handle_response)
        self.worker.start()

    @pyqtSlot(str)
    def handle_response(self, response):
        if self.pending_response:
            self.pending_response.parent().deleteLater()
            self.pending_response = None
        self.append_message("Gemini", response)
        self.scroll.ensureVisible(0, self.chat_area.height())

    # Event filter to capture Ctrl+Enter key press on input_field.
    def eventFilter(self, source, event):
        if source == self.input_field and event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
                self.send_message()
                return True
        return super().eventFilter(source, event)

    # Button feedback: changes style briefly when clicked.
    def button_feedback(self, button, func):
        original_style = button.styleSheet()
        button.setStyleSheet(original_style + "background-color: #a9d18e;")
        QTimer.singleShot(200, lambda: button.setStyleSheet(original_style))
        func()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = ChatClient()
    win.show()
    sys.exit(app.exec())
