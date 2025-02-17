import os
import pandas as pd
import json
from dotenv import load_dotenv

load_dotenv()

def convert_values(value):
    """
    Converts values properly:
    - If a number has .0, it is converted to an integer.
    - If a number is in the Excel date format, it is converted to 'YYYY-MM-DD'.
    - Empty or NaN values are converted to empty strings.
    """
    if pd.isna(value) or value in ["nan", "NaN", "None"]:  # Handling NaN values
        return ""

    try:
        # Try to convert to a number
        num = float(value)

        # If it's an integer, check if it's an Excel date
        if num.is_integer():
            excel_start_date = pd.Timestamp("1899-12-30")  # Excel date correction
            converted_date = excel_start_date + pd.to_timedelta(int(num), unit="D")

            # If the date is reasonable (after 1900 and before 2100), return it formatted
            if pd.Timestamp("1900-01-01") <= converted_date <= pd.Timestamp("2100-12-31"):
                return converted_date.strftime("%Y-%m-%d")  # Convert to 'YYYY-MM-DD' format

            return int(num)  # If it's not a valid date, convert it to a normal integer
        
        return str(value)  # Convert everything else to a string
    
    except ValueError:
        return str(value)  # If it's not numeric, return it as a string

def read_sheet_and_convert(file_path, sheet_name, selected_columns, column_mapping, opportunity_type_value):
    """
    Reads a sheet from the XLSB file, extracts specific columns, renames them, 
    properly formats values, and adds the opportunity_type field.
    """
    try:
        # Read the XLSB file with all values as strings
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='pyxlsb', dtype=str)

        # Check if the required columns exist in the file
        missing_columns = [col for col in selected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in sheet {sheet_name}: {missing_columns}")

        # Filter DataFrame with the required columns
        filtered_df = df[selected_columns]

        # Rename columns according to the mapping dictionary
        filtered_df = filtered_df.rename(columns=column_mapping)

        # Replace NaN values with empty strings
        filtered_df = filtered_df.fillna("")

        # 🔥 REMOVE ROWS THAT ARE COMPLETELY EMPTY 🔥
        filtered_df = filtered_df.replace("", pd.NA).dropna(how="all")

        # Convert values properly
        filtered_df = filtered_df.applymap(convert_values)

        # Convert to JSON
        json_data = filtered_df.to_dict(orient='records')

        # Add the "opportunity_type" field with the sheet value
        for record in json_data:
            record["opportunity_type"] = opportunity_type_value

        return json_data

    except Exception as e:
        print(f"Error processing sheet {sheet_name}: {e}")
        return []

# Function to read and process the Excel file
def excel_xlsb_to_json(file_path, output_json_path):
    try:
        # Original columns in the Excel file
        selected_columns = [
            "Role #", "Role Title", "Project Client", "Role Description", "Project Industry",
            "Role Fulfillment L4", "Role Location Type", "Role Management Level From",
            "Role Management Level To", "Role Primary Skill", "Role Skills",
            "Role Primary Contact", "Role Start Date", "Role End Date", "Role Primary Skill Category Group"
        ]

        # Dictionary to rename columns in the output JSON
        column_mapping = {
            "Role #": "roleId",
            "Role Title": "roleName",
            "Project Client": "project",
            "Role Description": "description",
            "Project Industry": "industry",
            "Role Fulfillment L4": "location",
            "Role Location Type": "locationType",
            "Role Management Level From": "level",
            "Role Management Level To": "level2",
            "Role Primary Skill": "mainSkill",
            "Role Skills": "secondarySkill",
            "Role Primary Contact": "contact",
            "Role Start Date": "startDate",
            "Role End Date": "endDate",
            "Role Primary Skill Category Group": "capability"
        }

        # Process the "Database" sheet with opportunity_type = "Database"
        data_database = read_sheet_and_convert(file_path, "Database", selected_columns, column_mapping, "Database")

        # Process the "1k" sheet with opportunity_type = "1k"
        data_1k = read_sheet_and_convert(file_path, "1k", selected_columns, column_mapping, "1k")

        # Merge both data lists
        final_data = data_database + data_1k

        # Save the JSON to a file
        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(final_data, json_file, indent=4, ensure_ascii=False)

        print(f"JSON file saved successfully at: {output_json_path}")

    except Exception as e:
        print(f"Error: {e}")

# Path to the XLSB file
file_path = os.getenv("DOWNLOAD_PATH") + "Demand.xlsb"
output_json_path = os.getenv("DOWNLOAD_PATH") + "output.json"

# Run the function
excel_xlsb_to_json(file_path, output_json_path)