import requests

BASE_URL = "http://localhost:9090"

# 1. Test /list_tables
print("\n1. Testing /list_tables...")
list_tables_url = f"{BASE_URL}/list_tables"
resp = requests.get(list_tables_url)
tables = resp.json().get("tables", [])
print("Available Tables:", tables)

# Pick one table to test further
test_table = "Equity Analysis of a Project"

# 2. Test /get_table_details
print("\n2. Testing /get_table_details...")
get_rows_url = f"{BASE_URL}/get_table_details"
resp = requests.get(get_rows_url, params={"table_name": test_table})
rows = resp.json().get("row_names", [])
print(f"Row names in '{test_table}':", rows)

# 3. Test /row_sum for all rows in the table
print(f"\n3. Testing /row_sum for all rows in '{test_table}'...")
for row in rows:
    row_sum_url = f"{BASE_URL}/row_sum"
    resp = requests.get(row_sum_url, params={"table_name": test_table, "row_name": row})
    if resp.status_code == 200:
        data = resp.json()
        print(f"Row: {row:<50} Sum: {data['sum']}")
    else:
        print(f"Failed to compute sum for row '{row}':", resp.json()["detail"])
