# PDF Merger

A beautiful desktop application for merging multiple PDF files into a single document.

## Features

- Drag and drop functionality for easy file selection
- File browser support for adding PDFs
- Rearrange PDF files before merging
- Preview file names and details
- Simple and intuitive user interface

## Requirements

- Python 3.6+
- PyQt5
- PyPDF2

## Installation

### Automatic Installation (Windows)

Simply double-click the `run_pdf_merger.bat` file included in the directory:
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
1. Simply double-click the `run_pdf_merger.bat` file included in the directory
   - This will automatically install dependencies and start the application

#### Using PowerShell:
1. Open PowerShell by searching for it in the Start menu or pressing `Win+X` and selecting "Windows PowerShell"
2. Navigate to the directory containing the application:
   ```
   cd C:\path\to\pdf_merger
   ```
3. Run the application:
   ```
   python pdf_merger.py
   ```

#### Using Command Prompt:
1. Open Command Prompt by searching for it in the Start menu
2. Navigate to the directory containing the application:
   ```
   cd C:\path\to\pdf_merger
   ```
3. Run the application:
   ```
   python pdf_merger.py
   ```

### Using the Application
1. Add PDF files using drag and drop or the "Add Files" button
2. Rearrange files if needed using the up/down buttons
3. Click "Merge PDFs" to combine the files
4. Choose a location to save the merged PDF file

## Created By

This application was created by Abhishek Shukla. Visit [my GitHub profile](https://github.com/abhis699) for more projects.
