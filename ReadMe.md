# Excelerate - Process Flow Documentation

<div align="center">
  <img src="assets/GitHub_Logo.png" alt="Project Logo" width="300" />
</div>

![Python Version](https://img.shields.io/badge/Python-3.11.1-4571A1)
![Last Commit](https://img.shields.io/github/last-commit/calumsudo/Excelerate)
![Issues](https://img.shields.io/github/issues/calumsudo/Excelerate)

## Introduction
This document outlines the operational procedure for the 'Excelerate' application, which automates the integration of financial data from CSV files provided by various funders into a central Excel workbook stored in Microsoft OneDrive.

## Install
- Make sure you have Python Installed
- Clone the repository `git clone https://github.com/calumsudo/Excelerate.git`
- Then navigate to the root directory `cd /path/to/your/project`
- Create Virtual Environment `python -m venv env`
- Activate the Environment
    - Windows: `.\env\Scripts\activate`
    - MacOS / Linux: `source env/bin/activate`
- Install the Dependencies: `pip install -r requirements.txt`
- Start the program: `python main.py` or `python3 main.py`


## Workflow Steps

### 1. Launching the Application
- The user starts the 'Excelerate' application.
- A user interface (UI) loads, presenting an authentication button.
<div align="center">
  <img src="assets/Excelerate_Authentication.png" alt="Project Logo" width="300" />
</div>

### 2. Authentication
- The user clicks the authentication button to begin the process.
- Once authentication is successful, the UI updates to display a new window.
<div align="center">
  <img src="assets/Microsoft_Authentication.png" alt="Project Logo" width="300" />
</div>

### 3. Workbook Selection
- In the updated UI, the user is prompted to select a workbook from a list.
- The selected workbook is then downloaded from Microsoft OneDrive.
- A backup duplicate copy of the workbook is automatically created for safety.

### 4. Data Processing Activation
- With the workbook downloaded, the UI activates functionality for CSV file processing.

### 5. CSV File Upload
- The user uploads each funder's Weekly or Daily CSV files.
- If time permits, enhance the UI with drag-and-drop capabilities for file upload.
- CSV files then get cleaned and processed with the parsing functions

### 6. Queue Creation and Processing
- As CSV files are uploaded, they are placed into a queue to ensure that each funder's data is processed sequentially.
- The application processes one CSV file at a time, corresponding to each funder's data.

### 7. Data Validation and Logging
- During processing, the application checks for:
  - Duplicate merchant entries.
  - Merchants that do not exist in the workbook.
- Any discrepancies are logged for later review.

### 8. Reporting
- After all CSV files are processed, the application compiles a report PDF which includes:
  - The pivot table for each funder's CSV.
  - Totals for each column in the pivot tables.
  - A summary of any errors, exceptions, or duplicate entries found during processing.

### 9. Finalizing the Workbook
- The processed data is inserted into the Excel workbook.
- The workbook is saved with all updates applied.

### 10. Uploading the Updated Workbook
- The updated workbook is uploaded back to _Microsoft OneDrive_ using the _Microsoft Graph API_.
- Any changes are synchronized, and the backup copy is retained as per the set retention policy.

## Conclusion
The _Excelerate_ application streamlines the process of updating financial data, ensuring that the information from various funders is consolidated efficiently and accurately into a central workbook. The process also includes robust error handling and reporting mechanisms to facilitate data integrity and accountability.


