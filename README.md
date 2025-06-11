# Excel Data API using FastAPI

# Overview
This project is part of the IRIS assignment and involves building a RESTful API using FastAPI to process an Excel file containing multiple logical tables spread across various sheets. The application allows users to interact with the Excel data through defined API endpoints that support:

Listing all detected tables across the Excel file.

Retrieving the row names (first column values) from a specified table.

Computing the sum of numerical values in a specified row of a selected table.

The system intelligently identifies logical tables by detecting breaks (empty rows) within and across sheets. It supports both .xlsx and .xls formats using the openpyxl and xlrd libraries respectively.

# Objective
The key objectives of the project are:

To enable users to list all logical tables extracted from an Excel file.

To allow retrieval of row identifiers from a specific table.

To calculate the sum of numeric values present in any row, excluding the first column.

# Implementation Details
Excel Input: The input file capbudg.xlsx is stored inside the Data directory.

API Logic: The core API logic is implemented in main.py, which defines the three primary endpoints.

Testing: The test_api.py script automates testing by calling all endpoints and displaying their outputs for verification.

Data Handling: Logical tables are split using empty rows. Each row's first cell is treated as its identifier, and summation excludes non-numeric or invalid cells.

# API Endpoints

1. GET /list_tables
Description:
Returns a list of all logical table names detected in the Excel file.

2. GET /get_table_details
Query Parameter:

table_name (string): Name of the target table.
Description:
Returns the row names (i.e., first-column values) of the specified table.

3. GET /row_sum
Query Parameters:

table_name (string): Name of the table.

row_name (string): Name of the row to sum.
Description:
Returns the sum of all numeric values in the specified row (excluding the first cell).


# Setup Instructions
Create and activate a virtual environment:
python -m venv venv
venv\Scripts\activate    # On Windows

Install dependencies:
pip install fastapi uvicorn pandas openpyxl xlrd requests

Run the server:
python main.py

To verify that all endpoints work as expected, run:
python test_api.py


