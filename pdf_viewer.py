#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import tempfile
import shutil
import io
from PyQt5.QtWidgets import (QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, 
                            QLabel, QWidget, QFileDialog, QScrollArea, QFrame, 
                            QGraphicsDropShadowEffect, QToolBar, QAction, QSpinBox,
                            QComboBox, QMessageBox, QSplitter, QApplication, QSizePolicy, QShortcut)
from PyQt5.QtCore import Qt, QUrl, QSize, QBuffer, QTimer
from PyQt5.QtGui import QColor, QFont, QCursor, QPixmap, QImage
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import fitz  # PyMuPDF

# Import common utilities
from utils import (HeaderFrame, StyledButton, open_file, 
                  PRIMARY_COLOR, SECONDARY_COLOR, SUCCESS_COLOR, DANGER_COLOR,
                  WARNING_COLOR, LIGHT_BG_COLOR, DARK_TEXT_COLOR, LIGHT_TEXT_COLOR,
                  SHADOW_COLOR, BORDER_COLOR)

# Import the full-screen viewer
from pdf_fullscreen_viewer import FullScreenPDFViewer

class PDFImageView(QScrollArea):
    """Custom widget to display PDF pages as images with scrolling"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up the scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setAlignment(Qt.AlignCenter)
        
        # Create a label to display the PDF page
        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Enable mouse tracking for double-click events
        self.image_label.setMouseTracking(True)
        
        # Set the label as the widget in the scroll area
        self.setWidget(self.image_label)
        
        # Apply styling
        self.setStyleSheet("""
            QScrollArea {
                background-color: #525659;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #525659;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #888888;
                min-height: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar:horizontal {
                border: none;
                background: #525659;
                height: 10px;
                margin: 0px;
            }
            QScrollBar::handle:horizontal {
                background: #888888;
                min-width: 20px;
                border-radius: 5px;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                border: none;
                background: none;
            }
        """)
    
    def display_pdf_page(self, pixmap):
        """Display a PDF page using a QPixmap"""
        self.image_label.setPixmap(pixmap)
        self.image_label.adjustSize()

    def set_placeholder(self, message="No PDF file loaded"):
        """Show a placeholder message when no PDF is loaded"""
        self.image_label.clear()
        self.image_label.setText(message)
        self.image_label.setStyleSheet("""
            QLabel {
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 18px;
                color: #CCCCCC;
                background-color: #525659;
                padding: 50px;
            }
        """)
        self.image_label.adjustSize()

    def mouseDoubleClickEvent(self, event):
        """Handle double click events to toggle fullscreen mode"""
        # Find parent PDFViewerWindow to toggle fullscreen
        parent = self.parent()
        while parent and not isinstance(parent, QMainWindow):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'enter_fullscreen'):
            parent.enter_fullscreen()
        else:
            super().mouseDoubleClickEvent(event)

class PDFViewerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.current_pdf_path = None
        self.current_page = 0
        self.zoom_level = 1.0
        self.temp_dir = None
        self.total_pages = 0
        self.doc = None
        self.fullscreen_viewer = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle('PDF Viewer - Ultimate PDF Tools')
        self.setGeometry(100, 100, 1000, 800)
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
            QToolBar {{
                background-color: white;
                border-bottom: 1px solid {BORDER_COLOR};
                spacing: 5px;
                padding: 2px;
            }}
            QAction {{
                padding: 5px;
                margin: 2px;
            }}
            QToolButton {{
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }}
            QToolButton:hover {{
                background-color: #F5F5F5;
                border: 1px solid {PRIMARY_COLOR};
            }}
            QToolButton:pressed {{
                background-color: #E3F2FD;
            }}
            QSpinBox, QComboBox {{
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
                min-width: 70px;
            }}
            QSpinBox:hover, QComboBox:hover {{
                border: 1px solid {PRIMARY_COLOR};
            }}
        """)

        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(25, 25, 25, 25)
        main_layout.setSpacing(20)
        
        # Header with back button
        header = HeaderFrame()
        header_layout = QHBoxLayout(header)
        
        title_label = QLabel('PDF Viewer')
        title_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: white;
        """)
        subtitle_label = QLabel('View PDF files with ease')
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
        
        # Instructions Frame
        instructions_frame = QFrame()
        instructions_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        instructions_layout = QVBoxLayout(instructions_frame)
        
        self.file_info_label = QLabel("No file opened. Click 'Open PDF' to get started.")
        self.file_info_label.setAlignment(Qt.AlignCenter)
        self.file_info_label.setStyleSheet("""
            color: #455A64;
            font-size: 15px;
            font-weight: normal;
            margin: 5px 0;
        """)
        instructions_layout.addWidget(self.file_info_label)
        
        # Add shadow to instructions
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(SHADOW_COLOR))
        shadow.setOffset(0, 2)
        instructions_frame.setGraphicsEffect(shadow)
        
        main_layout.addWidget(instructions_frame)
        
        # Create toolbar for PDF viewing controls
        toolbar = QToolBar("PDF Controls")
        toolbar.setIconSize(QSize(24, 24))
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: white;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        
        # Toolbar shadow
        toolbar_shadow = QGraphicsDropShadowEffect()
        toolbar_shadow.setBlurRadius(15)
        toolbar_shadow.setColor(QColor(SHADOW_COLOR))
        toolbar_shadow.setOffset(0, 2)
        toolbar.setGraphicsEffect(toolbar_shadow)
        
        # Open PDF action
        self.open_action = QAction("Open PDF", self)
        self.open_action.triggered.connect(self.open_pdf)
        toolbar.addAction(self.open_action)
        
        toolbar.addSeparator()
        
        # Previous page action
        self.prev_action = QAction("Previous", self)
        self.prev_action.triggered.connect(self.prev_page)
        self.prev_action.setEnabled(False)
        toolbar.addAction(self.prev_action)
        
        # Page number spinbox
        self.page_spinbox = QSpinBox()
        self.page_spinbox.setMinimum(1)
        self.page_spinbox.setMaximum(1)
        self.page_spinbox.valueChanged.connect(self.go_to_page)
        self.page_spinbox.setEnabled(False)
        toolbar.addWidget(self.page_spinbox)
        
        # Page count label
        self.page_count_label = QLabel(" / 0")
        toolbar.addWidget(self.page_count_label)
        
        # Next page action
        self.next_action = QAction("Next", self)
        self.next_action.triggered.connect(self.next_page)
        self.next_action.setEnabled(False)
        toolbar.addAction(self.next_action)
        
        toolbar.addSeparator()
        
        # Zoom controls
        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.zoom_out_action.setEnabled(False)
        toolbar.addAction(self.zoom_out_action)
        
        # Zoom level combo box
        self.zoom_combo = QComboBox()
        zoom_levels = ["50%", "70%", "75%", "80%", "85%", "90%", "100%", "125%", "150%", "175%", "200%", "250%", "300%"]
        self.zoom_combo.addItems(zoom_levels)
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.currentTextChanged.connect(self.zoom_level_changed)
        self.zoom_combo.setEnabled(False)
        toolbar.addWidget(self.zoom_combo)
        
        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.zoom_in_action.setEnabled(False)
        toolbar.addAction(self.zoom_in_action)
        
        # Add fit width action
        toolbar.addSeparator()
        self.fit_action = QAction("Fit Screen", self)
        self.fit_action.triggered.connect(self.fit_to_screen)
        self.fit_action.setEnabled(False)
        toolbar.addAction(self.fit_action)
        
        # Add fullscreen action
        toolbar.addSeparator()
        self.fullscreen_action = QAction("Full Screen", self)
        self.fullscreen_action.triggered.connect(self.enter_fullscreen)
        self.fullscreen_action.setEnabled(False)
        toolbar.addAction(self.fullscreen_action)
        
        # Add print action
        toolbar.addSeparator()
        self.print_action = QAction("Print", self)
        self.print_action.triggered.connect(self.print_pdf)
        self.print_action.setEnabled(False)
        toolbar.addAction(self.print_action)
        
        # Add toolbar to layout
        toolbar_frame = QFrame()
        toolbar_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
                padding: 5px;
            }
        """)
        toolbar_layout = QVBoxLayout(toolbar_frame)
        toolbar_layout.addWidget(toolbar)
        
        main_layout.addWidget(toolbar_frame)
        
        # PDF viewer frame
        viewer_frame = QFrame()
        viewer_frame.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border-radius: 10px;
            }
        """)
        viewer_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add shadow to viewer frame
        viewer_shadow = QGraphicsDropShadowEffect()
        viewer_shadow.setBlurRadius(15)
        viewer_shadow.setColor(QColor(SHADOW_COLOR))
        viewer_shadow.setOffset(0, 2)
        viewer_frame.setGraphicsEffect(viewer_shadow)
        
        viewer_layout = QVBoxLayout(viewer_frame)
        
        # Create custom PDF viewer widget
        self.pdf_view = PDFImageView()
        self.pdf_view.set_placeholder("Open a PDF file to view its contents.\nClick the 'Open PDF' button to get started.")
        
        viewer_layout.addWidget(self.pdf_view)
        main_layout.addWidget(viewer_frame, 1)  # Give the viewer more stretching space
        
        # Status bar
        self.statusBar().showMessage('Ready')
        
        # Add keyboard shortcut for fullscreen (F11)
        self.fullscreen_shortcut = QShortcut(Qt.Key_F11, self)
        self.fullscreen_shortcut.activated.connect(self.enter_fullscreen)

    def go_back(self):
        """Return to the main menu"""
        # Clean up any open document
        self.close_current_document()
        if self.parent_window:
            self.parent_window.show()
        self.hide()

    def close_current_document(self):
        """Close the current document and clean up resources"""
        if self.doc:
            self.doc.close()
            self.doc = None
        
        if self.temp_dir and os.path.exists(self.temp_dir):
            try:
                shutil.rmtree(self.temp_dir)
                self.temp_dir = None
            except Exception as e:
                print(f"Error cleaning up temporary files: {e}")
    
    def open_pdf(self):
        """Open a PDF file for viewing"""
        # Close any currently open document first
        self.close_current_document()
        
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open PDF File", "", "PDF Files (*.pdf)"
        )
        
        if not file_path:
            return
        
        try:
            # Create a temporary directory for our files
            self.temp_dir = tempfile.mkdtemp(prefix="pdf_viewer_")
            
            # Open the PDF with PyMuPDF
            self.doc = fitz.open(file_path)
            self.total_pages = len(self.doc)
            
            if self.total_pages == 0:
                QMessageBox.warning(self, "Empty PDF", "The selected PDF file has no pages.")
                self.close_current_document()
                return
            
            # Update UI controls
            self.current_page = 0
            self.page_spinbox.setEnabled(True)
            self.page_spinbox.setMinimum(1)
            self.page_spinbox.setMaximum(self.total_pages)
            self.page_spinbox.setValue(1)  # This will trigger page rendering via valueChanged
            self.page_count_label.setText(f" / {self.total_pages}")
            
            # Enable navigation buttons
            self.prev_action.setEnabled(True)
            self.next_action.setEnabled(True)
            self.zoom_in_action.setEnabled(True)
            self.zoom_out_action.setEnabled(True)
            self.zoom_combo.setEnabled(True)
            self.print_action.setEnabled(True)
            self.fullscreen_action.setEnabled(True)
            self.fit_action.setEnabled(True)
            
            # Display file information
            file_name = os.path.basename(file_path)
            file_size = os.path.getsize(file_path) / (1024 * 1024)  # Convert to MB
            self.file_info_label.setText(
                f"File: {file_name} | Size: {file_size:.2f} MB | Pages: {self.total_pages}"
            )
            
            # Store current file path
            self.current_pdf_path = file_path
            
            # Set zoom level to 100%
            self.zoom_level = 1.0
            self.zoom_combo.setCurrentText("100%")
            
            # Render the first page
            self.render_current_page()
            
            self.statusBar().showMessage(f'Opened: {file_name}')
            
        except Exception as e:
            QMessageBox.critical(self, "Error Opening PDF", f"Could not open the PDF file: {str(e)}")
            self.close_current_document()

    def render_current_page(self):
        """Render the current page of the PDF"""
        if not self.doc or self.current_page < 0 or self.current_page >= self.total_pages:
            return
        
        try:
            # Get the current page
            page = self.doc[self.current_page]
            
            # Render page to an image with zoom factor
            matrix = fitz.Matrix(2 * self.zoom_level, 2 * self.zoom_level)  # Scale factor for better quality
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Convert PyMuPDF pixmap to QImage
            img_data = pix.samples
            qimg = QImage(img_data, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            
            # Convert QImage to QPixmap for display
            pixmap = QPixmap.fromImage(qimg)
            
            # Display the pixmap in our custom viewer
            self.pdf_view.display_pdf_page(pixmap)
            
            # Update page navigation controls
            self.prev_action.setEnabled(self.current_page > 0)
            self.next_action.setEnabled(self.current_page < self.total_pages - 1)
            
            # Update status bar
            self.statusBar().showMessage(f'Page {self.current_page + 1} of {self.total_pages}')
            
        except Exception as e:
            QMessageBox.warning(self, "Rendering Error", f"Error rendering page: {str(e)}")

    def prev_page(self):
        """Go to the previous page"""
        if self.doc and self.current_page > 0:
            self.current_page -= 1
            self.page_spinbox.setValue(self.current_page + 1)  # This will trigger rendering

    def next_page(self):
        """Go to the next page"""
        if self.doc and self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.page_spinbox.setValue(self.current_page + 1)  # This will trigger rendering

    def go_to_page(self, page_num):
        """Go to a specific page"""
        if not self.doc:
            return
        
        # Convert from 1-based UI to 0-based index
        self.current_page = page_num - 1
        
        # Ensure it's within valid range
        if self.current_page < 0:
            self.current_page = 0
        elif self.current_page >= self.total_pages:
            self.current_page = self.total_pages - 1
        
        self.render_current_page()

    def zoom_in(self):
        """Increase zoom level"""
        if not self.doc:
            return
            
        # Find the next zoom level in the combo box
        current_idx = self.zoom_combo.currentIndex()
        if current_idx < self.zoom_combo.count() - 1:
            self.zoom_combo.setCurrentIndex(current_idx + 1)
        
    def zoom_out(self):
        """Decrease zoom level"""
        if not self.doc:
            return
            
        # Find the previous zoom level in the combo box
        current_idx = self.zoom_combo.currentIndex()
        if current_idx > 0:
            self.zoom_combo.setCurrentIndex(current_idx - 1)

    def zoom_level_changed(self, zoom_text):
        """Handle zoom level changes from the combo box"""
        if not self.doc:
            return
            
        # Parse the percentage value
        try:
            zoom_text = zoom_text.replace("%", "")
            zoom_percent = float(zoom_text)
            self.zoom_level = zoom_percent / 100.0
            self.render_current_page()
        except ValueError:
            pass
            
    def print_pdf(self):
        """Print the current PDF document"""
        if not self.doc or not self.current_pdf_path:
            return
            
        try:
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            
            if dialog.exec_() == QPrintDialog.Accepted:
                # Use the original PDF file directly for printing
                printer.setOutputFileName("")  # Direct to physical printer, not a file
                
                # Use an external command to print the PDF
                # We could implement a more sophisticated printing system if needed
                if sys.platform == 'win32':
                    os.startfile(self.current_pdf_path, 'print')
                else:
                    QMessageBox.information(self, "Print", "Please use your system's PDF viewer to print this document.")
                
                self.statusBar().showMessage('Print job sent to printer')
        except Exception as e:
            QMessageBox.critical(self, "Print Error", f"Error printing document: {str(e)}")

    def enter_fullscreen(self):
        """Enter full-screen viewing mode with continuous scrolling"""
        if not self.doc:
            return
        
        try:
            # Prepare the document before showing the fullscreen viewer
            # to reduce transition lag
            self.statusBar().showMessage('Preparing fullscreen mode...')
            
            # Use QApplication.processEvents() to keep UI responsive
            QApplication.processEvents()
            
            # Create a full-screen viewer with current document
            self.fullscreen_viewer = FullScreenPDFViewer(
                parent=self,
                pdf_document=self.doc,
                current_page=self.current_page,
                zoom_level=self.zoom_level
            )
            
            # First hide the main window to improve perception of speed
            self.hide()
            
            # Process events before showing the fullscreen viewer
            QApplication.processEvents()
            
            # Show the fullscreen viewer
            self.fullscreen_viewer.show()
            
        except Exception as e:
            QMessageBox.critical(self, "Fullscreen Error", f"Error entering fullscreen mode: {str(e)}")
            if self.fullscreen_viewer:
                self.fullscreen_viewer.close()
                self.fullscreen_viewer = None
            self.show()
    
    def return_from_fullscreen(self, page_idx, zoom_level):
        """Handle the return from full-screen viewing mode"""
        self.show()  # Show the main window again
        
        # Update the current page and zoom level if they changed
        if page_idx != self.current_page:
            self.current_page = page_idx
            self.page_spinbox.setValue(page_idx + 1)  # Will trigger page rendering
        
        if zoom_level != self.zoom_level:
            self.zoom_level = zoom_level
            # Set zoom combo box text
            zoom_text = f"{int(zoom_level * 100)}%"
            self.zoom_combo.setCurrentText(zoom_text)  # Will trigger rendering
        
        # Clean up the fullscreen viewer
        if self.fullscreen_viewer:
            self.fullscreen_viewer = None
            
        # Ensure the current page is properly rendered
        QTimer.singleShot(50, self.render_current_page)
        
        # Update status bar
        self.statusBar().showMessage(f'Page {self.current_page + 1} of {self.total_pages}')

    def closeEvent(self, event):
        """Handle window close event to clean up resources"""
        # Close any fullscreen viewer first
        if self.fullscreen_viewer:
            self.fullscreen_viewer.close()
            self.fullscreen_viewer = None
            
        self.close_current_document()
        event.accept()

    def fit_to_screen(self):
        """Adjust zoom level to fit the page width to the screen width including corners"""
        if not self.doc or self.current_page >= self.total_pages:
            return
        
        try:
            # Get the current page
            page = self.doc[self.current_page]
            
            # Get the page dimensions
            page_width = page.rect.width
            
            # Calculate the ideal zoom factor to fit the screen
            # Use a slightly smaller width to ensure both corners are visible
            view_width = self.pdf_view.viewport().width() - 60  # Increased padding for corners
            
            # Calculate the zoom needed for the page to fit the view width
            if page_width > 0:
                # Apply a small reduction factor (0.95) to ensure both corners are visible
                new_zoom = (view_width / page_width) * 0.95
                # Limit zoom to reasonable bounds
                new_zoom = max(0.5, min(3.0, new_zoom))
                
                # Apply the new zoom level
                self.zoom_level = new_zoom
                
                # Update zoom combo box
                zoom_text = f"{int(new_zoom * 100)}%"
                closest_idx = 0
                closest_diff = float('inf')
                
                # Find the closest predefined zoom level
                for i in range(self.zoom_combo.count()):
                    level_text = self.zoom_combo.itemText(i).replace('%', '')
                    try:
                        level = float(level_text)
                        diff = abs(level - int(new_zoom * 100))
                        if diff < closest_diff:
                            closest_diff = diff
                            closest_idx = i
                    except ValueError:
                        continue
                
                # If an exact match exists in predefined levels, select it
                exact_idx = self.zoom_combo.findText(zoom_text)
                if exact_idx >= 0:
                    self.zoom_combo.setCurrentIndex(exact_idx)
                # If within 5% of a predefined level, use that
                elif closest_diff <= 5:
                    self.zoom_combo.setCurrentIndex(closest_idx)
                # Otherwise use custom text
                else:
                    self.zoom_combo.setEditText(zoom_text)
                
                # Render with new zoom level
                self.render_current_page()
                
                # Center horizontally
                QTimer.singleShot(50, lambda: self.pdf_view.horizontalScrollBar().setValue(0))
                
                self.statusBar().showMessage(f'Fitted to screen at {zoom_text} zoom')
                
        except Exception as e:
            QMessageBox.warning(self, "Fit Error", f"Error fitting to screen: {str(e)}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Set application font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    window = PDFViewerWindow()
    window.show()
    
    sys.exit(app.exec_()) 