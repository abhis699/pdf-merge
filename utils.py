#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtWidgets import (QPushButton, QFrame, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon, QColor, QCursor, QLinearGradient

# Define color constants
PRIMARY_COLOR = "#1976D2"
SECONDARY_COLOR = "#3F51B5"
SUCCESS_COLOR = "#4CAF50"
DANGER_COLOR = "#F44336"
WARNING_COLOR = "#FF9800"
LIGHT_BG_COLOR = "#F5F7FA"
DARK_TEXT_COLOR = "#263238"
LIGHT_TEXT_COLOR = "#FFFFFF"
SHADOW_COLOR = "#B0BEC5"
HOVER_COLOR = "#2196F3"
BORDER_COLOR = "#E0E0E0"

class HeaderFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create gradient background
        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor(PRIMARY_COLOR))
        gradient.setColorAt(1, QColor(SECONDARY_COLOR))
        
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


class StyledButton(QPushButton):
    def __init__(self, text, color, icon_path=None, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(45)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(20, 20))
        
        # Set up background gradient
        self.normal_gradient = f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 {color}, stop:1 {self._darken_color(color, 20)});
                color: {LIGHT_TEXT_COLOR};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 {self._lighten_color(color, 10)}, stop:1 {color});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 {self._darken_color(color, 30)}, stop:1 {self._darken_color(color, 20)});
                padding-top: 10px;
                padding-bottom: 6px;
            }}
            QPushButton:disabled {{
                background: #BDBDBD;
                color: #757575;
            }}
        """
        self.setStyleSheet(self.normal_gradient)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
    
    def _lighten_color(self, color, amount=20):
        # Simple color lightening function
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = min(255, r + amount)
        g = min(255, g + amount)
        b = min(255, b + amount)
        return f"#{r:02x}{g:02x}{b:02x}"
    
    def _darken_color(self, color, amount=20):
        # Simple color darkening function
        color = color.lstrip('#')
        r, g, b = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, r - amount)
        g = max(0, g - amount)
        b = max(0, b - amount)
        return f"#{r:02x}{g:02x}{b:02x}"


def get_file_size_str(file_path):
    """Get a human-readable file size string."""
    try:
        size_bytes = os.path.getsize(file_path)
        
        # Convert to appropriate unit
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024 * 1024 * 1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.1f} GB"
    except Exception:
        return "Unknown size"


def open_file(file_path):
    """Open the file using the default system application"""
    if sys.platform == 'win32':
        os.startfile(file_path)
    elif sys.platform == 'darwin':  # macOS
        import subprocess
        subprocess.call(('open', file_path))
    else:  # Linux and other Unix-like
        import subprocess
        subprocess.call(('xdg-open', file_path))


def open_url(url):
    """Open the URL in the default web browser"""
    import webbrowser
    webbrowser.open(url) 