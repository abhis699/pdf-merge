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

### Splitting Options

The application offers three splitting methods:

- **Page ranges**: Extract specific pages by entering ranges and individual numbers (e.g., "1-3,5,7-9"). Saves as a single file with your chosen name.
- **Every N pages**: Create documents with a fixed number of pages per file. Files are automatically named with sequential part numbers.
- **Individual pages**: Create a separate PDF file for each page in the document. Files are automatically named with page numbers.

## Project Structure

- `main.py` - Main entry point with menu interface
- `pdf_merger.py`