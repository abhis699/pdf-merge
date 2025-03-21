#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import warnings

# Filter out PyQt5 deprecation warnings about sipPyTypeDict
warnings.filterwarnings("ignore", category=DeprecationWarning, message="sipPyTypeDict\(\) is deprecated")

from PyQt5.QtWidgets import (QApplication, QMainWindow, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QLabel, 
                            QWidget, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QFont, QCursor

# Import the modules for PDF merging and splitting
from pdf_merger import PDFMergerWindow
from pdf_splitter import PDFSplitterWindow
from pdf_viewer import PDFViewerWindow

# Define color constants
PRIMARY_COLOR = "#1976D2"
SECONDARY_COLOR = "#3F51B5"
SUCCESS_COLOR = "#4CAF50"
LIGHT_BG_COLOR = "#F5F7FA"
DARK_TEXT_COLOR = "#263238"
LIGHT_TEXT_COLOR = "#FFFFFF"
SHADOW_COLOR = "#B0BEC5"
HOVER_COLOR = "#2196F3"
BORDER_COLOR = "#E0E0E0"

class HeaderFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setStyleSheet(f"""
            HeaderFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                        stop:0 {PRIMARY_COLOR}, stop:1 {SECONDARY_COLOR});
                border-radius: 10px;
                padding: 20px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

class FeatureButton(QPushButton):
    def __init__(self, text, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(120)
        self.setMinimumWidth(250)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: #FFFFFF;
                color: {DARK_TEXT_COLOR};
                border: 1px solid {BORDER_COLOR};
                border-radius: 10px;
                padding: 20px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            }}
            QPushButton:hover {{
                background-color: #F5F5F5;
                border: 1px solid {PRIMARY_COLOR};
            }}
            QPushButton:pressed {{
                background-color: #E3F2FD;
            }}
        """)
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(48, 48))
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.merger_window = None
        self.splitter_window = None
        self.viewer_window = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Ultimate PDF Tools')
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {LIGHT_BG_COLOR};
            }}
            QLabel {{
                font-size: 14px;
                color: {DARK_TEXT_COLOR};
            }}
            QWidget {{
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(30)
        
        # Header
        header = HeaderFrame()
        header_layout = QHBoxLayout(header)
        
        title_label = QLabel('Ultimate PDF Tools')
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)
        subtitle_label = QLabel('Merge, split, view, and present PDF files with ease')
        subtitle_label.setStyleSheet("""
            font-size: 15px;
            color: rgba(255, 255, 255, 0.9);
            font-weight: normal;
        """)
        
        header_text_layout = QVBoxLayout()
        header_text_layout.addWidget(title_label)
        header_text_layout.addWidget(subtitle_label)
        
        header_layout.addLayout(header_text_layout)
        header_layout.addStretch()
        
        main_layout.addWidget(header)

        # Instructions
        instructions = QLabel("Select a tool to get started:")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #455A64;
            margin: 20px 0;
        """)
        main_layout.addWidget(instructions)
        
        # Feature buttons container
        buttons_container = QFrame()
        buttons_container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 30px;
            }
        """)
        
        # Add shadow to buttons container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 2)
        buttons_container.setGraphicsEffect(shadow)
        
        buttons_layout = QVBoxLayout(buttons_container)
        buttons_layout.setSpacing(20)
        buttons_layout.setContentsMargins(20, 20, 20, 20)
        
        # Create two rows of buttons
        top_row_layout = QHBoxLayout()
        top_row_layout.setSpacing(40)
        
        # PDF Merger Button
        self.merger_button = FeatureButton("Merge PDF Files")
        self.merger_button.clicked.connect(self.open_merger)
        
        # PDF Splitter Button
        self.splitter_button = FeatureButton("Split PDF Files")
        self.splitter_button.clicked.connect(self.open_splitter)
        
        top_row_layout.addStretch()
        top_row_layout.addWidget(self.merger_button)
        top_row_layout.addWidget(self.splitter_button)
        top_row_layout.addStretch()
        
        # Second row layout
        bottom_row_layout = QHBoxLayout()
        bottom_row_layout.setSpacing(40)
        
        # PDF Viewer Button (new)
        self.viewer_button = FeatureButton("View & Present PDF Files")
        self.viewer_button.clicked.connect(self.open_viewer)
        
        bottom_row_layout.addStretch()
        bottom_row_layout.addWidget(self.viewer_button)
        bottom_row_layout.addStretch()
        
        # Add both rows to the buttons container
        buttons_layout.addLayout(top_row_layout)
        buttons_layout.addLayout(bottom_row_layout)
        
        main_layout.addWidget(buttons_container)
        main_layout.addStretch()
        
        # Footer with creator info
        creator_frame = QFrame()
        creator_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        
        creator_layout = QHBoxLayout(creator_frame)
        creator_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add shadow to creator frame
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 2)
        creator_frame.setGraphicsEffect(shadow)
        
        # Create clickable label with creator info
        creator_label = QLabel("Created by Abhishek Shukla")
        creator_label.setStyleSheet("""
            color: #455A64;
            font-size: 12px;
            text-decoration: none;
            padding: 5px;
        """)
        creator_label.setCursor(QCursor(Qt.PointingHandCursor))
        
        # Add GitHub link
        github_url = "https://github.com/abhis699/pdf-tools"
        
        # Make the label clickable
        creator_label.mousePressEvent = lambda event: self.open_url(github_url)
        
        # Add hover effect
        creator_label.enterEvent = lambda event: creator_label.setStyleSheet("""
            color: #1976D2;
            font-size: 12px;
            text-decoration: underline;
            padding: 5px;
        """)
        
        creator_label.leaveEvent = lambda event: creator_label.setStyleSheet("""
            color: #455A64;
            font-size: 12px;
            text-decoration: none;
            padding: 5px;
        """)
        
        creator_layout.addStretch()
        creator_layout.addWidget(creator_label)
        creator_layout.addStretch()
        
        main_layout.addWidget(creator_frame)

    def open_merger(self):
        if not self.merger_window:
            self.merger_window = PDFMergerWindow(self)
        self.merger_window.show()
        self.hide()

    def open_splitter(self):
        if not self.splitter_window:
            self.splitter_window = PDFSplitterWindow(self)
        self.splitter_window.show()
        self.hide()
        
    def open_viewer(self):
        if not self.viewer_window:
            self.viewer_window = PDFViewerWindow(self)
        self.viewer_window.show()
        self.hide()

    def open_url(self, url):
        """Open the URL in the default web browser"""
        import webbrowser
        webbrowser.open(url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_()) 