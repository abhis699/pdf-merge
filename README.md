# Ultimate PDF Tools

A beautiful desktop application for managing PDF files with a clean, intuitive interface.

## Features

- **PDF Merger**: Combine multiple PDFs into a single document
  - Drag and drop functionality for easy file selection
  - Rearrange PDF files before merging
  - Preview file names and sizes

- **PDF Splitter**: Divide PDF files into smaller documents
  - Split by page ranges (e.g., 1-3,5,7-9)
  - Split by every N pages (e.g., every 2 pages)
  - Split into individual pages
  - Custom filename for output files
  - Batch processing of multiple files

- **PDF Viewer**: Open and view PDF files with a modern interface
  - Navigate through pages with ease
  - Zoom in/out with customizable zoom levels
  - Display file information and page count
  - Full-screen presentation mode with auto-hiding controls
  - Continuous scrolling through multiple pages
  - Keyboard shortcuts for navigation (Arrow keys, ESC)
  - Print PDFs directly from the viewer

- **Common Features**
  - Modern, user-friendly interface
  - Drag and drop support
  - File browser integration
  - Detailed progress indicators

## Requirements

- Python 3.6+
- PyQt5
- PyPDF2
- pikepdf
- PyMuPDF (fitz)
- PyQtWebEngine

## Installation

### Automatic Installation (Windows)

Simply double-click the `run_ultimate_pdf_tools.bat` file included in the directory:
- It automatically checks if Python is installed
- Installs required dependencies if they're missing
- Launches the application

### Manual Installation

1. Clone this repository or download the files
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running on Windows

#### Easiest Method:
1. Simply double-click the `run_ultimate_pdf_tools.bat` file included in the directory
   - This will automatically install dependencies and start the application

#### Using PowerShell:
1. Open PowerShell by searching for it in the Start menu or pressing `Win+X` and selecting "Windows PowerShell"
2. Navigate to the directory containing the application:
   ```
   cd C:\path\to\pdf_tools
   ```
3. Run the application:
   ```
   python main.py
   ```

#### Using Command Prompt:
1. Open Command Prompt by searching for it in the Start menu
2. Navigate to the directory containing the application:
   ```
   cd C:\path\to\pdf_tools
   ```
3. Run the application:
   ```
   python main.py
   ```

### Using the Application

#### PDF Merger
1. From the main menu, click on "Merge PDF Files"
2. Add PDF files using drag and drop or the "Add Files" button
3. Rearrange files if needed using the up/down buttons
4. Click "Merge PDFs" to combine the files
5. Choose a location to save the merged PDF file

#### PDF Splitter
1. From the main menu, click on "Split PDF Files"
2. Add PDF files using drag and drop or the "Add Files" button
3. Select a splitting method:
   - Split by page ranges: Enter page numbers and ranges (e.g., "1-3,5,7-9")
   - Split by every N pages: Select how many pages per document
   - Split into individual pages: Create a separate PDF for each page
4. Click "Split PDF" to process the files
5. Depending on the split method:
   - For page ranges: Choose a specific output filename
   - For other methods: Choose an output directory and enter a base name for the output files
6. The application will create properly named PDF files according to your settings

#### PDF Viewer
1. From the main menu, click on "View & Present PDF Files"
2. Click the "Open PDF" button in the toolbar
3. Select a PDF file to view
4. Navigate through pages using:
   - Previous/Next buttons
   - Page number input box
5. Adjust zoom level using:
   - Zoom In/Out buttons
   - Zoom level dropdown (50% to 300%)
6. View file information including name, size, and page count
7. Print the PDF using the "Print" button
8. Enter full-screen presentation mode:
   - Click the "Full Screen" button in the toolbar
   - Or press F11 key
   - Exit full-screen mode with ESC key

### Full-screen Presentation Mode

The full-screen mode offers enhanced viewing capabilities:

- **Continuous scrolling**: Scroll smoothly through all pages in the document
- **Auto-hiding navigation bar**: Controls fade when not in use and appear on mouse movement
- **Navigation**: 
  - Left/Right arrow keys to move between pages
  - ESC key to exit full-screen mode
  - On-screen controls for page navigation and zoom
- **Smart page detection**: The viewer automatically detects which page is currently visible while scrolling
- **Cross-page reading**: Seamlessly read content that spans multiple pages

### Splitting Options

The application offers three splitting methods:

- **Page ranges**: Extract specific pages by entering ranges and individual numbers (e.g., "1-3,5,7-9"). Saves as a single file with your chosen name.
- **Every N pages**: Create documents with a fixed number of pages per file. Files are automatically named with sequential part numbers.
- **Individual pages**: Create a separate PDF file for each page in the document. Files are automatically named with page numbers.

## Project Structure

- `main.py` - Main entry point with menu interface
- `pdf_merger.py` - PDF merging functionality
- `pdf_splitter.py` - PDF splitting functionality
- `pdf_viewer.py` - PDF viewing functionality in standard window
- `pdf_fullscreen_viewer.py` - Full-screen PDF viewer with continuous scrolling
- `utils.py` - Shared utility functions and classes
- `run_ultimate_pdf_tools.bat` - Windows launcher script

## Created By

This application was created by Abhishek Shukla. Visit [my GitHub profile](https://github.com/abhis699) for more projects.