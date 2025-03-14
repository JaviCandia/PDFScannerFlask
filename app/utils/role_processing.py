import json
import os
from threading import Thread
from app.utils.generateJSON_util import read_sheet_and_convert, selected_columns, column_mapping
from app.utils.db_insert_role import insert_roles_to_db

def process_and_upload_to_db(role_data):
    try:
        # Ensure that role_data is a list
        if isinstance(role_data, dict):
            role_list = [role_data]
        else:
            role_list = role_data
        insert_roles_to_db(role_list)
        print("Roles inserted/updated successfully.")
    except Exception as e:
        print(f"Error inserting roles into DB: {e}")

def process_demand_file(file):
    # Read the XLSB file and convert to JSON using utility functions
    data_database = read_sheet_and_convert(file, "Database", selected_columns, column_mapping, "Database")
    data_1k = read_sheet_and_convert(file, "1k", selected_columns, column_mapping, "1k")
    final_data = data_database + data_1k

    # Save output as demand_output.json
    with open('demand_output.json', 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=4)

    # Start background role processing
        Thread(target=process_and_upload_to_db, args=(final_data,)).start()

    # Return a status message with the count of roles processed
    return {"status": f"Role processing initiated, {len(final_data)} roles processed"}
