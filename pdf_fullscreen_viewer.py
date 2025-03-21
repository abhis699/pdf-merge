#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
                           QScrollArea, QFrame, QToolBar, QAction, QGraphicsOpacityEffect,
                           QToolButton, QPushButton, QSpinBox, QComboBox, QSizePolicy,
                           QApplication, QShortcut, QStyle)
from PyQt5.QtCore import Qt, QSize, QTimer, QPropertyAnimation, QRect, QEasingCurve
from PyQt5.QtGui import QPixmap, QImage, QColor, QFont, QKeySequence, QIcon
import fitz  # PyMuPDF

# Import common utilities
from utils import PRIMARY_COLOR, BORDER_COLOR

class FloatingNavBar(QFrame):
    """Floating navigation bar for full-screen mode"""
    def __init__(self, parent=None):
        super().__init__(parent)
        # Initialize timer and animation before setup_ui
        self.is_visible = True
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.start_fade_out)
        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        # Then call setup_ui
        self.setup_ui()
        
    def setup_ui(self):
        # Set up the frame style
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            FloatingNavBar {{
                background-color: rgba(60, 60, 60, 220);
                border-radius: 10px;
                padding: 0px;
                margin: 0px;
            }}
            QToolButton {{
                background-color: transparent;
                color: white;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 4px 8px;
                margin: 2px;
                min-height: 26px;
                min-width: 70px;
                font-size: 13px;
            }}
            QToolButton:hover {{
                background-color: rgba(100, 100, 100, 200);
                border: 1px solid {PRIMARY_COLOR};
            }}
            QSpinBox, QComboBox {{
                background-color: rgba(80, 80, 80, 220);
                color: white;
                border: 1px solid {BORDER_COLOR};
                border-radius: 4px;
                padding: 2px 4px;
                min-height: 26px;
                min-width: 70px;
                font-size: 13px;
            }}
            QLabel {{
                color: white;
                font-size: 13px;
                margin: 0px;
                padding: 0px;
            }}
        """)
        
        # Create a widget container to host the layout
        container = QWidget(self)
        container.setContentsMargins(10, 5, 10, 5)
        
        # Create layout with proper vertical alignment
        layout = QHBoxLayout(container)
        layout.setContentsMargins(10, 5, 10, 5)  # Minimal margins
        layout.setSpacing(10)  # Reduced spacing
        
        # Exit full screen button
        self.exit_btn = QToolButton()
        self.exit_btn.setText("Exit")
        layout.addWidget(self.exit_btn)
        
        layout.addSpacing(10)
        
        # Navigation controls in a group
        nav_container = QWidget()
        nav_layout = QHBoxLayout(nav_container)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        nav_layout.setSpacing(5)
        
        # Previous button
        self.prev_btn = QToolButton()
        self.prev_btn.setText("Prev")
        nav_layout.addWidget(self.prev_btn)
        
        # Page navigation
        page_widget = QWidget()
        page_layout = QHBoxLayout(page_widget)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(2)
        
        self.page_spin = QSpinBox()
        self.page_spin.setMinimum(1)
        self.page_spin.setMaximum(1)
        self.page_spin.setFixedWidth(50)
        page_layout.addWidget(self.page_spin)
        
        self.page_count = QLabel(" / 1")
        self.page_count.setAlignment(Qt.AlignCenter)
        page_layout.addWidget(self.page_count)
        
        nav_layout.addWidget(page_widget)
        
        # Next button
        self.next_btn = QToolButton()
        self.next_btn.setText("Next")
        nav_layout.addWidget(self.next_btn)
        
        layout.addWidget(nav_container)
        
        layout.addSpacing(10)
        
        # Zoom controls
        zoom_widget = QWidget()
        zoom_layout = QHBoxLayout(zoom_widget)
        zoom_layout.setContentsMargins(0, 0, 0, 0)
        zoom_layout.setSpacing(5)
        
        zoom_label = QLabel("Zoom:")
        zoom_layout.addWidget(zoom_label)
        
        self.zoom_combo = QComboBox()
        custom_zoom_levels = ["50%", "70%", "75%", "80%", "85%", "90%", "100%", "110%", "125%", "150%", "175%", "200%", "250%", "300%"]
        self.zoom_combo.addItems(custom_zoom_levels)
        self.zoom_combo.setCurrentText("100%")
        self.zoom_combo.setFixedWidth(70)
        self.zoom_combo.setEditable(True)
        zoom_layout.addWidget(self.zoom_combo)
        
        layout.addWidget(zoom_widget)
        
        # Set size of container to match parent
        container.setGeometry(0, 0, self.width(), self.height())
        
        # Start the timer
        self.reset_timeout()
    
    def reset_timeout(self):
        """Reset the auto-hide timer"""
        if hasattr(self, 'timer') and self.timer is not None:
            self.timer.stop()
            self.timer.start(3000)  # 3-second timeout
        
        if not self.is_visible and hasattr(self, 'fade_animation'):
            self.is_visible = True
            self.fade_animation.stop()
            self.setWindowOpacity(1.0)
    
    def start_fade_out(self):
        """Begin fading out the navigation bar"""
        if not hasattr(self, 'fade_animation') or self.fade_animation is None:
            return
            
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.fade_animation.start()
        self.is_visible = False
    
    def enterEvent(self, event):
        """Reset timeout when mouse enters the widget"""
        self.reset_timeout()
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Reset timeout when mouse leaves the widget"""
        super().leaveEvent(event)
    
    def show_bar(self):
        """Force-show the navigation bar"""
        if hasattr(self, 'fade_animation') and self.fade_animation is not None:
            self.fade_animation.stop()
        self.setWindowOpacity(1.0)
        self.is_visible = True
        self.reset_timeout()
    
    def resizeEvent(self, event):
        """Handle resize to make sure the inner container fills the frame"""
        super().resizeEvent(event)
        # Make sure any child widgets resize with the parent
        for child in self.children():
            if isinstance(child, QWidget) and child is not self:
                child.setGeometry(0, 0, self.width(), self.height())

class ContinuousScrollViewer(QScrollArea):
    """Custom widget for continuous scrolling through PDF pages"""
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set up scroll area
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for all pages
        self.container = QWidget()
        self.container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(20)  # Space between pages
        self.container_layout.setAlignment(Qt.AlignHCenter)
        
        # Set the container as the widget in the scroll area
        self.setWidget(self.container)
        
        # Apply styling
        self.setStyleSheet("""
            QScrollArea {
                background-color: #333333;
                border: none;
            }
            QScrollBar:vertical {
                border: none;
                background: #444444;
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
                height: 0px;
            }
            QScrollBar:horizontal {
                border: none;
                background: #444444;
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
                width: 0px;
            }
        """)
        
        # List to keep track of page labels
        self.page_labels = []
        self.current_page_idx = 0
        
        # Track which pages are visible
        self.visible_pages = set()
        
        # Connect scrollbar signals for more responsive page detection
        self.verticalScrollBar().valueChanged.connect(self.check_visible_pages)
        
    def clear_pages(self):
        """Clear all pages from the viewer"""
        # Remove all pages
        for label in self.page_labels:
            self.container_layout.removeWidget(label)
            label.deleteLater()
        
        self.page_labels = []
        self.visible_pages = set()
        
    def add_page(self, pixmap, page_idx):
        """Add a page to the viewer"""
        # Create a QLabel to display the page
        page_label = QLabel()
        page_label.setAlignment(Qt.AlignCenter)
        page_label.setPixmap(pixmap)
        page_label.setProperty("page_idx", page_idx)
        
        # Add shadow effect to make the page look like it's floating
        page_frame = QFrame()
        page_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        page_layout = QVBoxLayout(page_frame)
        page_layout.setContentsMargins(10, 10, 10, 10)
        page_layout.addWidget(page_label)
        
        # Add to container layout
        self.container_layout.addWidget(page_frame)
        self.page_labels.append(page_frame)
    
    def scroll_to_page(self, page_idx):
        """Scroll to make the specified page visible"""
        if 0 <= page_idx < len(self.page_labels):
            page_frame = self.page_labels[page_idx]
            self.ensureWidgetVisible(page_frame, 50, 50)
            self.current_page_idx = page_idx
    
    def get_visible_pages(self):
        """Determine which pages are currently visible in the viewport"""
        visible_pages = set()
        viewport_rect = self.viewport().rect()
        viewport_rect.translate(self.horizontalScrollBar().value(), self.verticalScrollBar().value())
        
        for i, frame in enumerate(self.page_labels):
            frame_rect = frame.frameGeometry()
            # Check if the page is at least partially visible
            if viewport_rect.intersects(frame_rect):
                visible_pages.add(i)
        
        return visible_pages
    
    def check_visible_pages(self):
        """Check which pages are visible when scroll position changes"""
        current_visible = self.get_visible_pages()
        
        # If the set of visible pages changed, update
        if current_visible != self.visible_pages:
            self.visible_pages = current_visible
            self.update_visible_page()
    
    def wheelEvent(self, event):
        """Handle mouse wheel events to detect page changes"""
        super().wheelEvent(event)
        
        # Let the scrollbar signal handle the rest - no need to duplicate
        # check here as it will be triggered by scrollbar valueChanged
    
    def update_visible_page(self):
        """Update the current page based on visibility"""
        # If we have visible pages, find the most prominent one
        if self.visible_pages:
            # For simplicity, take the first visible page
            # A more sophisticated approach would be to check which page takes
            # up the most space in the viewport
            current = min(self.visible_pages)
            if current != self.current_page_idx:
                self.current_page_idx = current
                # Call parent's method to update page number in UI
                if hasattr(self.parent(), 'on_page_visible_changed'):
                    self.parent().on_page_visible_changed(current)
    
    def mouseDoubleClickEvent(self, event):
        """Handle double click events to exit fullscreen"""
        # Find parent FullScreenPDFViewer to exit fullscreen
        parent = self.parent()
        while parent and not hasattr(parent, 'exit_fullscreen'):
            parent = parent.parent()
        
        if parent:
            # Store the current page before exiting fullscreen
            current_page = self.current_page_idx
            parent.exit_fullscreen(current_page)
        else:
            super().mouseDoubleClickEvent(event)

class FullScreenPDFViewer(QMainWindow):
    """Full screen PDF viewer with continuous scrolling and floating controls"""
    def __init__(self, parent=None, pdf_document=None, current_page=0, zoom_level=1.0):
        super().__init__(parent)
        self.parent_window = parent
        self.doc = pdf_document
        self.current_page = current_page
        self.zoom_level = zoom_level
        self.total_pages = len(pdf_document) if pdf_document else 0
        self.nav_bar = None  # Initialize nav_bar attribute
        self.screen_size = QApplication.desktop().screenGeometry()
        
        # Pre-calculate rendering dimensions to reduce lag
        if pdf_document:
            self.page_sizes = []
            for i in range(self.total_pages):
                self.page_sizes.append(pdf_document[i].rect.width)
        
        # Initialize UI
        self.setup_ui()
        
        # Load pages if document is provided - use QTimer to improve responsiveness
        if self.doc and self.total_pages > 0:
            self.update_ui_for_document()
            QTimer.singleShot(100, self.render_all_pages)
            self.scroll_viewer.scroll_to_page(self.current_page)
            
    def setup_ui(self):
        """Set up the UI for full-screen viewing"""
        # Set window properties
        self.setWindowTitle("PDF Full Screen Viewer")
        self.setWindowFlags(Qt.Window | Qt.FramelessWindowHint)
        self.showFullScreen()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create continuous scroll viewer
        self.scroll_viewer = ContinuousScrollViewer()
        main_layout.addWidget(self.scroll_viewer)
        
        # Create floating navigation bar
        self.nav_bar = FloatingNavBar()
        self.nav_bar.setMaximumHeight(55)  # Increased height for a better navbar
        self.nav_bar.exit_btn.clicked.connect(self.exit_fullscreen)
        self.nav_bar.prev_btn.clicked.connect(self.go_previous_page)
        self.nav_bar.next_btn.clicked.connect(self.go_next_page)
        self.nav_bar.page_spin.valueChanged.connect(self.go_to_page)
        self.nav_bar.zoom_combo.currentTextChanged.connect(self.zoom_level_changed)
        
        # Position the navigation bar at the bottom
        self.nav_bar.setParent(self)
        self.nav_bar.show()
        
        # Add keyboard shortcuts
        self.esc_shortcut = QShortcut(QKeySequence("Esc"), self)
        self.esc_shortcut.activated.connect(self.exit_fullscreen)
        
        self.left_shortcut = QShortcut(QKeySequence("Left"), self)
        self.left_shortcut.activated.connect(self.go_previous_page)
        
        self.right_shortcut = QShortcut(QKeySequence("Right"), self)
        self.right_shortcut.activated.connect(self.go_next_page)
        
        # Add zoom shortcuts
        self.zoom_in_shortcut = QShortcut(QKeySequence("+"), self)
        self.zoom_in_shortcut.activated.connect(self.zoom_in)
        
        self.zoom_out_shortcut = QShortcut(QKeySequence("-"), self)
        self.zoom_out_shortcut.activated.connect(self.zoom_out)
        
        # Also support Ctrl++ and Ctrl+- for zoom
        self.zoom_in_ctrl_shortcut = QShortcut(QKeySequence("Ctrl++"), self)
        self.zoom_in_ctrl_shortcut.activated.connect(self.zoom_in)
        
        self.zoom_out_ctrl_shortcut = QShortcut(QKeySequence("Ctrl+-"), self)
        self.zoom_out_ctrl_shortcut.activated.connect(self.zoom_out)
        
        # Add fit screen shortcut (F for fit)
        self.fit_shortcut = QShortcut(QKeySequence("F"), self)
        self.fit_shortcut.activated.connect(self.fit_to_screen)
        
        # Mouse move event for the whole window
        self.setMouseTracking(True)
        central_widget.setMouseTracking(True)
        self.scroll_viewer.setMouseTracking(True)
        self.scroll_viewer.viewport().setMouseTracking(True)
        
        # Position navbar after a short delay to ensure window is fully set up
        QTimer.singleShot(50, self.reposition_navbar)
    
    def update_ui_for_document(self):
        """Update UI controls with document information"""
        if not hasattr(self, 'nav_bar') or self.nav_bar is None:
            return
            
        self.nav_bar.page_spin.setMinimum(1)
        self.nav_bar.page_spin.setMaximum(self.total_pages)
        self.nav_bar.page_spin.setValue(self.current_page + 1)  # 1-based indexing for UI
        self.nav_bar.page_count.setText(f" / {self.total_pages}")
        
        # Set current zoom level
        zoom_text = f"{int(self.zoom_level * 100)}%"
        index = self.nav_bar.zoom_combo.findText(zoom_text)
        if index >= 0:
            self.nav_bar.zoom_combo.setCurrentIndex(index)
        else:
            self.nav_bar.zoom_combo.setCurrentText("100%")
    
    def render_all_pages(self):
        """Render all pages for continuous scrolling"""
        if not self.doc:
            return
        
        # Clear existing pages
        self.scroll_viewer.clear_pages()
        
        # Use progressive rendering to minimize lag
        self.current_render_page = 0
        self.render_next_page_batch()
    
    def render_next_page_batch(self):
        """Render a small batch of pages to keep UI responsive"""
        if not self.doc or self.current_render_page >= self.total_pages:
            return
        
        # Render a small batch of pages (3 pages at a time)
        batch_size = 3
        end_page = min(self.current_render_page + batch_size, self.total_pages)
        
        for page_idx in range(self.current_render_page, end_page):
            # Get the page
            page = self.doc[page_idx]
            
            # Render with appropriate zoom
            matrix = fitz.Matrix(2 * self.zoom_level, 2 * self.zoom_level)
            pix = page.get_pixmap(matrix=matrix, alpha=False)
            
            # Convert to QImage and QPixmap
            img_data = pix.samples
            qimg = QImage(img_data, pix.width, pix.height, pix.stride, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(qimg)
            
            # Add to scroll viewer
            self.scroll_viewer.add_page(pixmap, page_idx)
        
        # Update for next batch
        self.current_render_page = end_page
        
        # If more pages to render, schedule next batch
        if self.current_render_page < self.total_pages:
            QTimer.singleShot(10, self.render_next_page_batch)  # Small delay for UI responsiveness
        else:
            # All pages rendered, ensure we're at the correct position
            self.scroll_viewer.scroll_to_page(self.current_page)
            
            # Force an update of visible pages after rendering completes
            QTimer.singleShot(100, self.scroll_viewer.check_visible_pages)
    
    def reposition_navbar(self):
        """Position the navbar at the bottom center of the screen"""
        if not hasattr(self, 'nav_bar') or self.nav_bar is None:
            return
            
        # Make sure navbar width adapts to screen size but stays within reasonable bounds
        screen_width = self.width()
        # Make navbar wider to ensure all elements fit
        navbar_width = min(screen_width - 60, 700)  # Give 30px padding on each side, reduced max width
        
        # Set fixed size to ensure proper positioning
        self.nav_bar.setFixedWidth(navbar_width)
        
        # Center horizontally and position at bottom with padding
        x = (screen_width - navbar_width) // 2
        y = self.height() - self.nav_bar.height() - 40  # More bottom padding
        
        # Make sure navbar is fully visible
        if y < 0:
            y = 20  # If screen too small, position near top
        
        self.nav_bar.move(x, y)
        
        # Ensure navbar is visible on top of other content
        self.nav_bar.raise_()
    
    def on_page_visible_changed(self, page_idx):
        """Called when the most visible page changes during scrolling"""
        if not hasattr(self, 'nav_bar') or self.nav_bar is None:
            return
            
        # Update UI to reflect the current page
        # Add 1 because UI uses 1-based indexing
        self.current_page = page_idx
        
        # Block signals to prevent recursion
        self.nav_bar.page_spin.blockSignals(True)
        self.nav_bar.page_spin.setValue(page_idx + 1)
        self.nav_bar.page_spin.blockSignals(False)
        
        # Force update of the page count label
        self.nav_bar.page_count.setText(f" / {self.total_pages}")
    
    def go_to_page(self, page_num):
        """Go to specific page number (1-based UI to 0-based index)"""
        page_idx = page_num - 1
        if 0 <= page_idx < self.total_pages:
            self.current_page = page_idx
            self.scroll_viewer.scroll_to_page(page_idx)
    
    def go_previous_page(self):
        """Go to the previous page"""
        if self.current_page > 0:
            # Directly use 1-based numbering for clarity
            # We're on current_page (0-based), so page number is current_page + 1
            # To go to previous page, we use (current_page + 1) - 1 = current_page
            target_page_number = self.current_page  # This is current_page + 1 - 1
            self.nav_bar.page_spin.setValue(target_page_number)  # This will trigger go_to_page
    
    def go_next_page(self):
        """Go to the next page"""
        if self.current_page < self.total_pages - 1:
            # Directly use 1-based numbering for clarity
            # We're on current_page (0-based), so page number is current_page + 1
            # To go to next page, we use (current_page + 1) + 1 = current_page + 2
            target_page_number = self.current_page + 2
            self.nav_bar.page_spin.setValue(target_page_number)  # This will trigger go_to_page
    
    def zoom_in_one_percent(self):
        """Increase zoom level by 1%"""
        if not self.doc:
            return
            
        new_zoom = self.zoom_level + 0.01
        # Apply the new zoom and update the display
        self.apply_zoom(new_zoom)
    
    def zoom_out_one_percent(self):
        """Decrease zoom level by 1%"""
        if not self.doc:
            return
            
        new_zoom = max(0.1, self.zoom_level - 0.01)  # Don't go below 10%
        # Apply the new zoom and update the display
        self.apply_zoom(new_zoom)
    
    def apply_zoom(self, new_zoom):
        """Apply a specific zoom level and update UI"""
        if new_zoom != self.zoom_level:
            self.zoom_level = new_zoom
            
            # Update zoom combo box
            zoom_text = f"{int(new_zoom * 100)}%"
            # Block signals to prevent recursive calls
            if hasattr(self, 'nav_bar') and self.nav_bar is not None:
                self.nav_bar.zoom_combo.blockSignals(True)
                index = self.nav_bar.zoom_combo.findText(zoom_text)
                if index >= 0:
                    self.nav_bar.zoom_combo.setCurrentIndex(index)
                else:
                    self.nav_bar.zoom_combo.setEditText(zoom_text)
                self.nav_bar.zoom_combo.blockSignals(False)
            
            # Re-render pages with new zoom
            self.render_all_pages()
            # Maintain scroll position
            self.scroll_viewer.scroll_to_page(self.current_page)
    
    def zoom_level_changed(self, zoom_text):
        """Handle zoom level changes from combo box"""
        try:
            zoom_text = zoom_text.replace("%", "").strip()
            zoom_percent = float(zoom_text)
            new_zoom = zoom_percent / 100.0
            
            # Don't allow zooming below 10% or above 500%
            new_zoom = max(0.1, min(5.0, new_zoom))
            
            if new_zoom != self.zoom_level:
                self.zoom_level = new_zoom
                # Re-render all pages with new zoom level
                self.render_all_pages()
                # Scroll back to current page
                self.scroll_viewer.scroll_to_page(self.current_page)
        except ValueError:
            # If conversion fails, reset to current zoom level
            if hasattr(self, 'nav_bar') and self.nav_bar is not None:
                zoom_text = f"{int(self.zoom_level * 100)}%"
                self.nav_bar.zoom_combo.blockSignals(True)
                index = self.nav_bar.zoom_combo.findText(zoom_text)
                if index >= 0:
                    self.nav_bar.zoom_combo.setCurrentIndex(index)
                else:
                    self.nav_bar.zoom_combo.setEditText(zoom_text)
                self.nav_bar.zoom_combo.blockSignals(False)
    
    def exit_fullscreen(self, current_page=None):
        """Exit full-screen mode and return to parent window"""
        # Use provided page if available, otherwise use the tracked current page
        if current_page is not None:
            self.current_page = current_page
            
        self.close()
        if self.parent_window:
            # Inform parent window of the current page and zoom
            if hasattr(self.parent_window, 'return_from_fullscreen'):
                self.parent_window.return_from_fullscreen(self.current_page, self.zoom_level)
    
    def mouseMoveEvent(self, event):
        """Show the navbar when mouse moves"""
        if hasattr(self, 'nav_bar') and self.nav_bar is not None:
            self.nav_bar.show_bar()
            self.nav_bar.reset_timeout()
        super().mouseMoveEvent(event)
    
    def resizeEvent(self, event):
        """Handle window resize events to reposition navbar"""
        super().resizeEvent(event)
        self.reposition_navbar()

    def zoom_in(self):
        """Increase zoom level (larger step - for compatibility with keyboard shortcuts)"""
        if not self.doc:
            return
            
        # Increase by 25% steps for standard zoom in
        new_zoom = self.zoom_level * 1.25
        self.apply_zoom(new_zoom)
    
    def zoom_out(self):
        """Decrease zoom level (larger step - for compatibility with keyboard shortcuts)"""
        if not self.doc:
            return
            
        # Decrease by 20% steps for standard zoom out
        new_zoom = max(0.1, self.zoom_level * 0.8)
        self.apply_zoom(new_zoom)

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
            view_width = self.scroll_viewer.viewport().width() - 80  # Increased padding for corners
            
            # Calculate the zoom needed for the page to fit the view width
            if page_width > 0:
                # Apply a small reduction factor (0.95) to ensure both corners are visible
                new_zoom = (view_width / page_width) * 0.95
                
                # Limit zoom to reasonable bounds
                new_zoom = max(0.1, min(3.0, new_zoom))
                
                # Apply the new zoom level
                self.apply_zoom(new_zoom)
                
                # Center the page horizontally
                QTimer.singleShot(100, lambda: self.scroll_viewer.horizontalScrollBar().setValue(0))
                
                # Update status in the zoom combo box
                fit_text = f"{int(new_zoom * 100)}%"
                if hasattr(self, 'nav_bar') and self.nav_bar is not None:
                    self.nav_bar.zoom_combo.blockSignals(True)
                    self.nav_bar.zoom_combo.setEditText(fit_text)
                    self.nav_bar.zoom_combo.blockSignals(False)
        
        except Exception as e:
            print(f"Error in fit_to_screen: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # This is for testing only - normally this would be called from the main viewer
    # Open a test PDF if given as command line argument
    if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
        doc = fitz.open(sys.argv[1])
        viewer = FullScreenPDFViewer(pdf_document=doc)
        viewer.show()
        sys.exit(app.exec_())
    else:
        print("Please provide a PDF file path as argument for testing")
        sys.exit(1) 