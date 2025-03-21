#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tempfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QListWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, 
                            QWidget, QMessageBox, QListWidgetItem, QAbstractItemView,
                            QGridLayout, QProgressBar, QFrame, QSplitter, QGraphicsDropShadowEffect,
                            QCheckBox, QComboBox, QGroupBox, QFormLayout)
from PyQt5.QtCore import Qt, QUrl, QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QDrag, QPixmap, QPainter, QColor, QFont, QCursor, QLinearGradient, QPalette
import PyPDF2
import pikepdf
from pikepdf import Pdf

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

# Import common utilities
from utils import (HeaderFrame, StyledButton, get_file_size_str, open_file)

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


class PDFMergerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Merger - Ultimate PDF Tools')
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
        
        # Add back button to return to main menu
        back_button = StyledButton("Back to Main Menu", PRIMARY_COLOR)
        back_button.clicked.connect(self.go_back)
        header_layout.addWidget(back_button)
        
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
        buttons_layout.addWidget(self.merge_button)
        
        main_layout.addWidget(buttons_container)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
        self.update_buttons_state()

    def go_back(self):
        """Return to the main menu"""
        if self.parent_window:
            self.parent_window.show()
        self.hide()

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
                    file_size = get_file_size_str(file_path)
                    
                    # Format the text with file name and size
                    item.setText(f"{file_name} ({file_size})")
                    item.setToolTip(f"Path: {file_path}\nSize: {file_size}")
                    item.setData(Qt.UserRole, file_path)
                    
                    # Add a small description below the file name
                    item.setData(Qt.DisplayRole + 1, f"Size: {file_size}")
                    
                    self.pdf_list.addItem(item)
                    
                    self.statusBar().showMessage(f'Added: {file_name}', 3000)
                except Exception as e:
                    QMessageBox.warning(self, "Invalid PDF", f"Could not add {os.path.basename(file_path)}: {str(e)}")
        
        self.update_buttons_state()

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
            file_size = get_file_size_str(output_path)
            
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Success")
            msg_box.setText("PDF files merged successfully!")
            msg_box.setInformativeText(f"Output file size: {file_size}\nDo you want to open the merged file?")
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
                open_file(output_path)
        
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = PDFMergerWindow()
    window.show()
    
    sys.exit(app.exec_()) 