#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tempfile
from PyQt5.QtWidgets import (QMainWindow, QListWidget, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QFileDialog, QLabel, 
                            QWidget, QMessageBox, QListWidgetItem, QAbstractItemView,
                            QProgressBar, QFrame, QGraphicsDropShadowEffect,
                            QCheckBox, QComboBox, QFormLayout, QGroupBox, QApplication,
                            QSpinBox, QRadioButton, QButtonGroup, QLineEdit, QInputDialog)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QCursor
import PyPDF2

# Import common utilities
from utils import (HeaderFrame, StyledButton, get_file_size_str, open_file,
                  PRIMARY_COLOR, SECONDARY_COLOR, SUCCESS_COLOR, DANGER_COLOR, 
                  WARNING_COLOR, LIGHT_BG_COLOR, DARK_TEXT_COLOR, LIGHT_TEXT_COLOR,
                  SHADOW_COLOR, BORDER_COLOR)


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


class PDFSplitterWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Splitter - Ultimate PDF Tools')
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
        
        title_label = QLabel('PDF Splitter')
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)
        subtitle_label = QLabel('Split PDF files into smaller documents')
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
        instructions = QLabel("Add PDF files to split. You can split by page ranges, extract specific pages, or split into individual pages.")
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
        main_layout.addWidget(self.pdf_list)
        
        # Options container
        options_container = QFrame()
        options_container.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
            }
            QCheckBox, QRadioButton {
                color: #455A64;
                font-size: 14px;
                font-weight: normal;
                spacing: 5px;
            }
            QCheckBox::indicator, QRadioButton::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked, QRadioButton::indicator:unchecked {
                border: 2px solid #BDBDBD;
                border-radius: 4px;
                background-color: #FFFFFF;
            }
            QRadioButton::indicator:unchecked {
                border-radius: 9px;
            }
            QCheckBox::indicator:checked, QRadioButton::indicator:checked {
                border: 2px solid #1976D2;
                border-radius: 4px;
                background-color: #1976D2;
            }
            QRadioButton::indicator:checked {
                border-radius: 9px;
            }
            QSpinBox {
                border: 1px solid #E0E0E0;
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
                min-width: 70px;
            }
            QSpinBox:hover {
                border: 1px solid #1976D2;
            }
        """)
        
        options_layout = QVBoxLayout(options_container)
        
        # Split options
        split_group = QGroupBox("Split Options")
        split_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                color: #455A64;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        split_layout = QVBoxLayout(split_group)
        
        # Radio buttons for split mode
        self.split_mode_group = QButtonGroup(self)
        
        # Split by ranges
        self.radio_ranges = QRadioButton("Split by page ranges (e.g., 1-3,5,7-9)")
        self.radio_ranges.setChecked(True)
        self.split_mode_group.addButton(self.radio_ranges, 1)
        
        # Split by every N pages
        self.radio_every_n = QRadioButton("Split by every N pages")
        self.split_mode_group.addButton(self.radio_every_n, 2)
        
        # Split into individual pages
        self.radio_individual = QRadioButton("Split into individual pages")
        self.split_mode_group.addButton(self.radio_individual, 3)
        
        split_layout.addWidget(self.radio_ranges)
        
        # Range input
        range_input_layout = QHBoxLayout()
        self.range_label = QLabel("Page ranges:")
        self.range_label.setStyleSheet("font-weight: normal;")
        self.range_input = QLineEdit()
        self.range_input.setPlaceholderText("e.g., 1-3,5,7-9")
        self.range_input.setStyleSheet("""
            border: 1px solid #E0E0E0;
            border-radius: 4px;
            padding: 5px;
            min-height: 25px;
        """)
        range_input_layout.addWidget(self.range_label)
        range_input_layout.addWidget(self.range_input)
        split_layout.addLayout(range_input_layout)
        
        split_layout.addWidget(self.radio_every_n)
        
        # Every N pages input
        n_pages_layout = QHBoxLayout()
        self.n_pages_label = QLabel("Number of pages per file:")
        self.n_pages_label.setStyleSheet("font-weight: normal;")
        self.n_pages_input = QSpinBox()
        self.n_pages_input.setMinimum(1)
        self.n_pages_input.setMaximum(100)
        self.n_pages_input.setValue(1)
        n_pages_layout.addWidget(self.n_pages_label)
        n_pages_layout.addWidget(self.n_pages_input)
        n_pages_layout.addStretch()
        split_layout.addLayout(n_pages_layout)
        
        split_layout.addWidget(self.radio_individual)
        
        # Connect radio buttons to enable/disable relevant inputs
        self.radio_ranges.toggled.connect(self.update_input_states)
        self.radio_every_n.toggled.connect(self.update_input_states)
        self.radio_individual.toggled.connect(self.update_input_states)
        
        options_layout.addWidget(split_group)
        
        # Add shadow to options container
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 2)
        options_container.setGraphicsEffect(shadow)
        
        main_layout.addWidget(options_container)

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
        
        # Add stretch to push split button to the right
        buttons_layout.addStretch()
        
        # Split button
        self.split_button = StyledButton('Split PDF', SUCCESS_COLOR)
        self.split_button.clicked.connect(self.split_pdfs)
        self.split_button.setMinimumWidth(180)
        buttons_layout.addWidget(self.split_button)
        
        main_layout.addWidget(buttons_container)
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
        self.update_buttons_state()
        self.update_input_states()

    def update_input_states(self):
        """Enable/disable inputs based on selected split mode"""
        # Range input enabled only when radio_ranges is checked
        self.range_label.setEnabled(self.radio_ranges.isChecked())
        self.range_input.setEnabled(self.radio_ranges.isChecked())
        
        # N pages input enabled only when radio_every_n is checked
        self.n_pages_label.setEnabled(self.radio_every_n.isChecked())
        self.n_pages_input.setEnabled(self.radio_every_n.isChecked())

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
                    # Try to open the PDF to validate it and get page count
                    with open(file_path, 'rb') as f:
                        pdf = PyPDF2.PdfReader(f)
                        page_count = len(pdf.pages)
                    
                    # Create a nice-looking item for the list
                    item = QListWidgetItem()
                    file_name = os.path.basename(file_path)
                    file_size = get_file_size_str(file_path)
                    
                    # Format the text with file name, size, and page count
                    item.setText(f"{file_name} ({file_size}, {page_count} pages)")
                    item.setToolTip(f"Path: {file_path}\nSize: {file_size}\nPages: {page_count}")
                    item.setData(Qt.UserRole, file_path)
                    item.setData(Qt.UserRole + 1, page_count)
                    
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

    def update_buttons_state(self):
        has_items = self.pdf_list.count() > 0
        self.split_button.setEnabled(has_items)
        self.remove_button.setEnabled(has_items and len(self.pdf_list.selectedItems()) > 0)

    def parse_page_ranges(self, range_str, max_pages):
        """Parse a string of page ranges into a list of page numbers"""
        pages = []
        ranges = range_str.split(',')
        
        for r in ranges:
            r = r.strip()
            if '-' in r:
                try:
                    start, end = map(int, r.split('-'))
                    if start < 1 or end > max_pages or start > end:
                        continue
                    pages.extend(range(start, end + 1))
                except ValueError:
                    continue
            else:
                try:
                    page = int(r)
                    if 1 <= page <= max_pages:
                        pages.append(page)
                except ValueError:
                    continue
        
        # Remove duplicates and sort
        return sorted(list(set(pages)))

    def split_pdfs(self):
        if self.pdf_list.count() == 0:
            return
        
        # Get output directory and base filename
        if self.radio_ranges.isChecked():
            # For range mode, get a specific output filename
            output_path, _ = QFileDialog.getSaveFileName(
                self, 
                "Save Split PDF", 
                "", 
                "PDF Files (*.pdf)"
            )
            if not output_path:
                return
                
            # Extract directory and base filename
            output_dir = os.path.dirname(output_path)
            output_filename = os.path.basename(output_path)
            base_name = os.path.splitext(output_filename)[0]
        else:
            # For other modes (multiple files will be created), get output directory and base name
            output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory", "")
            if not output_dir:
                return
                
            # Get base name for files
            base_name, ok = QInputDialog.getText(
                self,
                "Output File Name",
                "Enter base name for output files (without extension):",
                text="split_output"
            )
            if not ok or not base_name:
                base_name = "split_output"  # Default name if user cancels or enters empty string
        
        # Setup progress
        self.progress_bar.setVisible(True)
        total_files = self.pdf_list.count()
        self.progress_bar.setRange(0, total_files)
        self.progress_bar.setValue(0)
        
        self.statusBar().showMessage('Splitting PDFs...')
        
        success_count = 0
        error_messages = []
        generated_files = []
        
        try:
            for i in range(total_files):
                item = self.pdf_list.item(i)
                input_path = item.data(Qt.UserRole)
                page_count = item.data(Qt.UserRole + 1)
                file_name = os.path.basename(input_path)
                file_base_name = os.path.splitext(file_name)[0]
                
                # If processing multiple files, use the original filename as part of output
                if total_files > 1:
                    current_base_name = f"{base_name}_{file_base_name}"
                else:
                    current_base_name = base_name
                
                self.statusBar().showMessage(f'Processing: {file_name}')
                
                try:
                    # Open the PDF file
                    with open(input_path, 'rb') as f:
                        pdf = PyPDF2.PdfReader(f)
                        
                        # Get pages based on split mode
                        if self.radio_ranges.isChecked():
                            # Split by ranges
                            range_text = self.range_input.text().strip()
                            if not range_text:
                                range_text = f"1-{page_count}"  # Default to all pages
                            
                            pages = self.parse_page_ranges(range_text, page_count)
                            
                            if not pages:
                                error_messages.append(f"Invalid page range for {file_name}")
                                continue
                            
                            # Create a single PDF with the selected pages
                            output_path = os.path.join(output_dir, f"{current_base_name}.pdf")
                            writer = PyPDF2.PdfWriter()
                            
                            for page_num in pages:
                                writer.add_page(pdf.pages[page_num - 1])  # PyPDF2 uses 0-based indexing
                            
                            with open(output_path, 'wb') as output_file:
                                writer.write(output_file)
                            
                            generated_files.append(output_path)
                            success_count += 1
                            
                        elif self.radio_every_n.isChecked():
                            # Split by every N pages
                            n_pages = self.n_pages_input.value()
                            
                            file_count = 0
                            for start_page in range(0, page_count, n_pages):
                                end_page = min(start_page + n_pages, page_count)
                                file_count += 1
                                
                                # Format part number with leading zeros based on total parts
                                total_parts = (page_count + n_pages - 1) // n_pages
                                part_format = f"{{:0{len(str(total_parts))}d}}"
                                part_num = part_format.format(file_count)
                                
                                output_path = os.path.join(output_dir, f"{current_base_name}_part{part_num}.pdf")
                                writer = PyPDF2.PdfWriter()
                                
                                for page_num in range(start_page, end_page):
                                    writer.add_page(pdf.pages[page_num])
                                
                                with open(output_path, 'wb') as output_file:
                                    writer.write(output_file)
                                
                                generated_files.append(output_path)
                            
                            success_count += 1
                                
                        else:  # self.radio_individual.isChecked()
                            # Split into individual pages
                            page_format = f"{{:0{len(str(page_count))}d}}"  # Format with leading zeros
                            
                            for page_num in range(page_count):
                                page_str = page_format.format(page_num + 1)
                                output_path = os.path.join(output_dir, f"{current_base_name}_page{page_str}.pdf")
                                writer = PyPDF2.PdfWriter()
                                writer.add_page(pdf.pages[page_num])
                                
                                with open(output_path, 'wb') as output_file:
                                    writer.write(output_file)
                                
                                generated_files.append(output_path)
                            
                            success_count += 1
                    
                except Exception as e:
                    error_messages.append(f"Error processing {file_name}: {str(e)}")
                
                self.progress_bar.setValue(i + 1)
                QApplication.processEvents()  # Keep UI responsive
            
            # Show success message
            msg_box = QMessageBox(self)
            msg_box.setWindowTitle("Split Complete")
            
            if success_count > 0:
                num_files_generated = len(generated_files)
                msg_box.setText(f"Successfully split {success_count} PDFs into {num_files_generated} files!")
                if error_messages:
                    msg_box.setInformativeText(f"There were {len(error_messages)} errors. See details for more information.\n\nWould you like to open the output folder?")
                else:
                    msg_box.setInformativeText(f"Files saved to: {output_dir}\n\nWould you like to open the output folder?")
            else:
                msg_box.setText("Failed to split any files.")
                msg_box.setInformativeText("Check the details for error information.")
                
            if error_messages:
                msg_box.setDetailedText("\n".join(error_messages))
                
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
            
            if msg_box.exec_() == QMessageBox.Yes and success_count > 0:
                open_file(output_dir)
                
            self.statusBar().showMessage(f'Split complete: {success_count} PDFs into {num_files_generated} files', 5000)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"An error occurred while splitting PDFs: {str(e)}")
            self.statusBar().showMessage('Error: Failed to split PDFs', 5000)
            
        finally:
            self.progress_bar.setVisible(False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = PDFSplitterWindow()
    window.show()
    
    sys.exit(app.exec_()) 