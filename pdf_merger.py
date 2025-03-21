#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, 
                            QWidget, QMessageBox, QListWidgetItem, QAbstractItemView,
                            QGridLayout, QProgressBar, QFrame, QSplitter, QGraphicsDropShadowEffect)
from PyQt5.QtCore import Qt, QUrl, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QDrag, QPixmap, QPainter, QColor, QFont, QCursor, QLinearGradient, QPalette
import PyPDF2

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

class PDFListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QListWidget {
                background-color: #FFFFFF;
                border-radius: 10px;
                border: 1px solid #E0E0E0;
                padding: 15px;
                outline: none;
            }
            QListWidget::item {
                background-color: #F8F9FA;
                border-radius: 6px;
                border: 1px solid #EEEEEE;
                padding: 12px;
                margin: 4px 2px;
            }
            QListWidget::item:alternate {
                background-color: #FFFFFF;
            }
            QListWidget::item:selected {
                background-color: #E3F2FD;
                color: #1976D2;
                border: 1px solid #1976D2;
            }
            QListWidget::item:hover {
                background-color: #F5F5F5;
                border: 1px solid #2196F3;
            }
            QScrollBar:vertical {
                border: none;
                background: #F5F5F5;
                width: 8px;
                border-radius: 4px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #BDBDBD;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #9E9E9E;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
                height: 0px;
                width: 0px;
            }
        """)
        
        # Add drop shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            
            pdf_files = []
            for url in event.mimeData().urls():
                file_path = url.toLocalFile()
                if file_path.lower().endswith('.pdf'):
                    pdf_files.append(file_path)
            
            if pdf_files:
                self.parent().add_pdf_files(pdf_files)
        else:
            super().dropEvent(event)


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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Merger')
        self.setGeometry(100, 100, 900, 700)
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {LIGHT_BG_COLOR};
            }}
            QLabel {{
                font-size: 14px;
                font-weight: bold;
                color: {DARK_TEXT_COLOR};
            }}
            QWidget {{
                font-family: 'Segoe UI', 'Arial', sans-serif;
            }}
            QStatusBar {{
                background-color: #FFFFFF;
                color: {DARK_TEXT_COLOR};
                border-top: 1px solid {BORDER_COLOR};
                padding: 5px;
                font-size: 13px;
            }}
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Header
        header = HeaderFrame()
        header_layout = QHBoxLayout(header)
        
        title_label = QLabel('PDF Merger')
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)
        subtitle_label = QLabel('Drag & Drop PDF files to merge them')
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

        # Instructions with cleaner styling
        instructions_frame = QFrame()
        instructions_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        instructions_layout = QVBoxLayout(instructions_frame)
        instructions = QLabel("Add PDF files by dragging and dropping them below or use the 'Add Files' button")
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("""
            color: #455A64;
            font-size: 15px;
            font-weight: normal;
            margin: 5px 0;
        """)
        instructions_layout.addWidget(instructions)
        
        # Add shadow to instructions
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 2)
        instructions_frame.setGraphicsEffect(shadow)
        
        main_layout.addWidget(instructions_frame)

        # PDF List
        self.pdf_list = PDFListWidget(self)
        self.pdf_list.setMinimumHeight(350)
        main_layout.addWidget(self.pdf_list)

        # Progress bar with modern styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: #EEEEEE;
                text-align: center;
                height: 15px;
                font-size: 12px;
                font-weight: bold;
                color: {DARK_TEXT_COLOR};
            }}
            QProgressBar::chunk {{
                background-color: {PRIMARY_COLOR};
                border-radius: 5px;
            }}
        """)
        self.progress_bar.setVisible(False)
        
        progress_container = QFrame()
        progress_container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        progress_layout = QVBoxLayout(progress_container)
        progress_layout.addWidget(self.progress_bar)
        
        # Add shadow to progress container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 2)
        progress_container.setGraphicsEffect(shadow)
        
        main_layout.addWidget(progress_container)

        # Buttons layout
        buttons_container = QFrame()
        buttons_container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        buttons_layout = QHBoxLayout(buttons_container)
        buttons_layout.setSpacing(15)
        
        # Add shadow to buttons container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 2)
        buttons_container.setGraphicsEffect(shadow)
        
        # File operations buttons
        file_buttons_layout = QVBoxLayout()
        file_buttons_layout.setSpacing(10)
        
        # Add files button
        self.add_button = StyledButton('Add Files', PRIMARY_COLOR)
        self.add_button.clicked.connect(self.browse_files)
        file_buttons_layout.addWidget(self.add_button)
        
        # Remove selected button
        self.remove_button = StyledButton('Remove Selected', DANGER_COLOR)
        self.remove_button.clicked.connect(self.remove_selected)
        file_buttons_layout.addWidget(self.remove_button)
        
        buttons_layout.addLayout(file_buttons_layout)
        
        # Reorder buttons
        reorder_buttons_layout = QVBoxLayout()
        reorder_buttons_layout.setSpacing(10)
        
        # Move up button
        self.up_button = StyledButton('Move Up', WARNING_COLOR)
        self.up_button.clicked.connect(self.move_up)
        reorder_buttons_layout.addWidget(self.up_button)
        
        # Move down button
        self.down_button = StyledButton('Move Down', WARNING_COLOR)
        self.down_button.clicked.connect(self.move_down)
        reorder_buttons_layout.addWidget(self.down_button)
        
        buttons_layout.addLayout(reorder_buttons_layout)
        
        # Add stretch to push merge button to the right
        buttons_layout.addStretch()
        
        # Merge button
        self.merge_button = StyledButton('Merge PDFs', SUCCESS_COLOR)
        self.merge_button.clicked.connect(self.merge_pdfs)
        self.merge_button.setMinimumWidth(180)
        self.merge_button.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 {SUCCESS_COLOR}, stop:1 {self._darken_color(SUCCESS_COLOR, 20)});
                color: {LIGHT_TEXT_COLOR};
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 16px;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 {self._lighten_color(SUCCESS_COLOR, 10)}, stop:1 {SUCCESS_COLOR});
            }}
            QPushButton:pressed {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                        stop:0 {self._darken_color(SUCCESS_COLOR, 30)}, stop:1 {self._darken_color(SUCCESS_COLOR, 20)});
                padding-top: 14px;
                padding-bottom: 10px;
            }}
            QPushButton:disabled {{
                background: #BDBDBD;
                color: #757575;
            }}
        """)
        buttons_layout.addWidget(self.merge_button)
        
        main_layout.addWidget(buttons_container)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
        # Add creator info at bottom
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
        
        # Add small shadow to creator frame
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
        github_url = "https://github.com/abhis699"
        
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
        
        self.update_buttons_state()

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

    def browse_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, "Select PDF Files", "", "PDF Files (*.pdf)")
        if files:
            self.add_pdf_files(files)

    def add_pdf_files(self, file_paths):
        for file_path in file_paths:
            if os.path.isfile(file_path) and file_path.lower().endswith('.pdf'):
                try:
                    # Try to open the PDF to validate it
                    with open(file_path, 'rb') as f:
                        PyPDF2.PdfReader(f)
                    
                    # Create a nice-looking item for the list
                    item = QListWidgetItem()
                    file_name = os.path.basename(file_path)
                    file_size = self.get_file_size_str(file_path)
                    
                    # Format the text with file name and size
                    item.setText(f"{file_name}")
                    item.setToolTip(f"Path: {file_path}\nSize: {file_size}")
                    item.setData(Qt.UserRole, file_path)
                    
                    # Add a small description below the file name
                    item.setData(Qt.DisplayRole + 1, f"Size: {file_size}")
                    
                    self.pdf_list.addItem(item)
                    
                    self.statusBar().showMessage(f'Added: {file_name}', 3000)
                except Exception as e:
                    QMessageBox.warning(self, "Invalid PDF", f"Could not add {os.path.basename(file_path)}: {str(e)}")
        
        self.update_buttons_state()

    def get_file_size_str(self, file_path):
        size_bytes = os.path.getsize(file_path)
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024*1024):.1f} MB"

    def remove_selected(self):
        selected_items = self.pdf_list.selectedItems()
        if not selected_items:
            return
        
        # Create confirmation dialog with modern styling
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Confirm Removal")
        msg_box.setText(f"Are you sure you want to remove {len(selected_items)} file(s)?")
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg_box.setDefaultButton(QMessageBox.No)
        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #FFFFFF;
            }
            QLabel {
                color: #455A64;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1976D2;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1565C0;
            }
            QPushButton:pressed {
                background-color: #0D47A1;
            }
        """)
        
        if msg_box.exec_() == QMessageBox.Yes:
            for item in selected_items:
                row = self.pdf_list.row(item)
                self.pdf_list.takeItem(row)
            
            self.statusBar().showMessage(f'Removed {len(selected_items)} file(s)', 3000)
            self.update_buttons_state()

    def move_up(self):
        current_row = self.pdf_list.currentRow()
        if current_row > 0:
            item = self.pdf_list.takeItem(current_row)
            self.pdf_list.insertItem(current_row - 1, item)
            self.pdf_list.setCurrentRow(current_row - 1)
            self.statusBar().showMessage('Moved file up', 2000)

    def move_down(self):
        current_row = self.pdf_list.currentRow()
        if current_row < self.pdf_list.count() - 1:
            item = self.pdf_list.takeItem(current_row)
            self.pdf_list.insertItem(current_row + 1, item)
            self.pdf_list.setCurrentRow(current_row + 1)
            self.statusBar().showMessage('Moved file down', 2000)

    def update_buttons_state(self):
        has_items = self.pdf_list.count() > 0
        self.merge_button.setEnabled(has_items)
        self.remove_button.setEnabled(has_items)
        
        has_selection = len(self.pdf_list.selectedItems()) > 0
        current_row = self.pdf_list.currentRow()
        
        self.up_button.setEnabled(current_row > 0)
        self.down_button.setEnabled(current_row >= 0 and current_row < self.pdf_list.count() - 1)

    def merge_pdfs(self):
        if self.pdf_list.count() == 0:
            return
        
        # Ask user where to save the merged PDF
        output_path, _ = QFileDialog.getSaveFileName(self, "Save Merged PDF", "", "PDF Files (*.pdf)")
        if not output_path:
            return
        
        if not output_path.lower().endswith('.pdf'):
            output_path += '.pdf'
        
        # Setup progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, self.pdf_list.count())
        self.progress_bar.setValue(0)
        
        try:
            # Create PDF merger
            pdf_merger = PyPDF2.PdfMerger()
            
            # Add each PDF to the merger
            for i in range(self.pdf_list.count()):
                item = self.pdf_list.item(i)
                pdf_path = item.data(Qt.UserRole)
                self.statusBar().showMessage(f'Processing: {os.path.basename(pdf_path)}')
                
                with open(pdf_path, 'rb') as pdf_file:
                    pdf_merger.append(pdf_file)
                
                self.progress_bar.setValue(i + 1)
                QApplication.processEvents()  # Keep UI responsive
            
            # Write merged PDF to file
            self.statusBar().showMessage(f'Saving merged PDF to {output_path}')
            with open(output_path, 'wb') as output_file:
                pdf_merger.write(output_file)
            
            self.statusBar().showMessage('PDF files merged successfully!', 5000)
            
            # Create a more modern success dialog
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Success")
            msg_box.setText("PDF files merged successfully!")
            msg_box.setInformativeText("Do you want to open the merged file?")
            msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg_box.setDefaultButton(QMessageBox.Yes)
            msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #FFFFFF;
                }
                QLabel {
                    color: #455A64;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #43A047;
                }
                QPushButton:pressed {
                    background-color: #388E3C;
                }
            """)
            
            if msg_box.exec_() == QMessageBox.Yes:
                self.open_file(output_path)
        
        except Exception as e:
            # Create a better error dialog
            error_box = QMessageBox(self)
            error_box.setWindowTitle("Error")
            error_box.setText("Failed to merge PDFs")
            error_box.setInformativeText(str(e))
            error_box.setIcon(QMessageBox.Critical)
            error_box.setStandardButtons(QMessageBox.Ok)
            error_box.setStyleSheet("""
                QMessageBox {
                    background-color: #FFFFFF;
                }
                QLabel {
                    color: #455A64;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #F44336;
                    color: white;
                    border-radius: 4px;
                    padding: 6px 12px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #E53935;
                }
                QPushButton:pressed {
                    background-color: #D32F2F;
                }
            """)
            error_box.exec_()
            
            self.statusBar().showMessage('Error: Failed to merge PDFs', 5000)
        
        finally:
            self.progress_bar.setVisible(False)

    def open_file(self, file_path):
        """Open the file using the default system application"""
        if sys.platform == 'win32':
            os.startfile(file_path)
        elif sys.platform == 'darwin':  # macOS
            import subprocess
            subprocess.call(('open', file_path))
        else:  # Linux and other Unix-like
            import subprocess
            subprocess.call(('xdg-open', file_path))

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