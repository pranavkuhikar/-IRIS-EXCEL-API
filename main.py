from fastapi import FastAPI, HTTPException, Query
import pandas as pd
from pathlib import Path

app = FastAPI()

# File path - adjust as needed
EXCEL_FILE_PATH = Path("Data/capbudg.xlsx")

def load_excel_file(file_path):
    """Load Excel file with automatic engine detection"""
    try:
        if file_path.suffix.lower() == '.xlsx':
            return pd.read_excel(file_path, sheet_name=None, engine="openpyxl", header=None)
        elif file_path.suffix.lower() == '.xls':
            return pd.read_excel(file_path, sheet_name=None, engine="xlrd", header=None)
        else:
            try:
                return pd.read_excel(file_path, sheet_name=None, engine="openpyxl", header=None)
            except:
                return pd.read_excel(file_path, sheet_name=None, engine="xlrd", header=None)
    except Exception as e:
        raise RuntimeError(f"Failed to load Excel file: {e}")

def extract_logical_tables(sheet_df):
    """Extract logical tables from a sheet by splitting on empty rows"""
    tables = {}
    current_table_rows = []
    table_counter = 1
    
    for idx, row in sheet_df.iterrows():
        # Check if the entire row is empty/null
        if row.isnull().all() or (row.astype(str).str.strip() == '').all():
            # If we have accumulated rows, create a table
            if current_table_rows:
                table_df = pd.DataFrame(current_table_rows).reset_index(drop=True)
                
                # Get table name from first non-empty cell in first row
                table_name = None
                first_row = current_table_rows[0]
                for val in first_row:
                    if pd.notna(val) and str(val).strip() != "":
                        table_name = str(val).strip()
                        break
                
                # Fallback to generic name if no good name found
                if not table_name or table_name.lower() == "nan":
                    table_name = f"Table {table_counter}"
                
                tables[table_name] = table_df
                current_table_rows = []
                table_counter += 1
        else:
            # Add row to current table
            current_table_rows.append(row)

    # Handle the last table if there are remaining rows
    if current_table_rows:
        table_df = pd.DataFrame(current_table_rows).reset_index(drop=True)
        
        table_name = None
        first_row = current_table_rows[0]
        for val in first_row:
            if pd.notna(val) and str(val).strip() != "":
                table_name = str(val).strip()
                break
        
        if not table_name or table_name.lower() == "nan":
            table_name = f"Table {table_counter}"
            
        tables[table_name] = table_df

    return tables

# Load the Excel file and extract tables
try:
    all_sheets = load_excel_file(EXCEL_FILE_PATH)
    
    # Extract all tables from all sheets
    tables = {}
    for sheet_name, df in all_sheets.items():
        extracted = extract_logical_tables(df)
        tables.update(extracted)
        
    print(f"Successfully loaded {len(tables)} tables: {list(tables.keys())}")
    
except Exception as e:
    raise RuntimeError(f"Failed to process Excel file: {e}")

# API Endpoints as per assignment requirements

@app.get("/list_tables")
def list_tables():
    """
    Functionality: List all the table names present in the Excel sheet.
    Returns: JSON with list of table names
    """
    return {"tables": list(tables.keys())}

@app.get("/get_table_details")
def get_table_details(table_name: str = Query(..., description="Query parameter specifying the name of the table")):
    """
    Functionality: Return the names of the rows for the selected table.
    These row names are typically the values found in the first column of that table.
    
    Parameters:
    - table_name: str (Query parameter specifying the name of the table)
    
    Returns: JSON with table name and list of row names
    """
    if table_name not in tables:
        available_tables = list(tables.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Table '{table_name}' not found. Available tables: {available_tables}"
        )

    table_df = tables[table_name]
    
    # Get all non-null values from the first column (row names)
    row_names = []
    for val in table_df[0]:
        if pd.notna(val) and str(val).strip() != "":
            row_names.append(str(val).strip())
    
    return {
        "table_name": table_name,
        "row_names": row_names
    }

@app.get("/row_sum")
def row_sum(
    table_name: str = Query(..., description="Query parameter specifying the name of the table"),
    row_name: str = Query(..., description="Query parameter specifying the name of the row")
):
    """
    Functionality: Calculate and return the sum of all numerical data points 
    in the specified row of the specified table.
    
    Parameters:
    - table_name: str (Query parameter specifying the name of the table)
    - row_name: str (Query parameter specifying the name of the row)
    
    Returns: JSON with table name, row name, and sum of numerical values
    """
    if table_name not in tables:
        available_tables = list(tables.keys())
        raise HTTPException(
            status_code=404, 
            detail=f"Table '{table_name}' not found. Available tables: {available_tables}"
        )

    table_df = tables[table_name]
    
    # Find the row with matching name
    target_row = None
    for idx, row in table_df.iterrows():
        if pd.notna(row[0]) and str(row[0]).strip() == row_name.strip():
            target_row = row
            break
    
    if target_row is None:
        # Get available row names for error message
        available_rows = []
        for val in table_df[0]:
            if pd.notna(val) and str(val).strip() != "":
                available_rows.append(str(val).strip())
        
        raise HTTPException(
            status_code=404, 
            detail=f"Row '{row_name}' not found in table '{table_name}'. Available rows: {available_rows}"
        )
    
    # Extract and sum numerical values from the row (excluding first column which is row name)
    numerical_sum = 0
    for val in target_row[1:]:  # Skip first column (row name)
        if pd.notna(val):
            try:
                # Handle different number formats
                if isinstance(val, (int, float)):
                    numerical_sum += float(val)
                elif isinstance(val, str):
                    # Handle percentage strings like "10%"
                    if val.strip().endswith('%'):
                        numerical_sum += float(val.strip().rstrip('%'))
                    else:
                        # Try to convert string to number
                        numerical_sum += float(val.strip())
            except (ValueError, TypeError):
                # Skip non-numerical values
                continue
    
    return {
        "table_name": table_name,
        "row_name": row_name,
        "sum": numerical_sum
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090)