import pandas as pd
import json

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
        num = float(value)
        if num.is_integer():
            excel_start_date = pd.Timestamp("1899-12-30")  # Excel date correction
            converted_date = excel_start_date + pd.to_timedelta(int(num), unit="D")

            if pd.Timestamp("1900-01-01") <= converted_date <= pd.Timestamp("2100-12-31"):
                return converted_date.strftime("%Y-%m-%d")

            return int(num) 
        
        return str(value)
    
    except ValueError:
        return str(value)

def read_sheet_and_convert(file_path, sheet_name, selected_columns, column_mapping, opportunity_type_value, unique_roles):
    """
    Reads a sheet from the XLSB file, extracts specific columns, renames them,
    properly formats values, and ensures `roleId` uniqueness by updating existing ones.
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='pyxlsb', dtype=str)

        # Check for missing columns in the sheet
        missing_columns = [col for col in selected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in sheet {sheet_name}: {missing_columns}")

        # Select and rename required columns
        filtered_df = df[selected_columns].rename(columns=column_mapping).fillna("")

        # Remove completely empty rows
        filtered_df = filtered_df.replace("", pd.NA).dropna(how="all")

        # Convert values according to format rules
        filtered_df = filtered_df.applymap(convert_values)

        # Convert DataFrame to JSON records
        json_data = filtered_df.to_dict(orient='records')

        # Add the "opportunity_type" field
        for record in json_data:
            record["opportunity_type"] = opportunity_type_value

            # Ensure roleId uniqueness by overwriting existing ones
            role_id = record.get("roleId")
            if role_id:
                unique_roles[role_id] = record  # If it exists, overwrite it

    except Exception as e:
        print(f"Error processing sheet {sheet_name}: {e}")

# Function to read and process the Excel file
def excel_xlsb_to_json(file_path, output_json_path):
    """
    Reads an XLSB file, extracts relevant data, ensures unique roleId values,
    and saves the final cleaned data as a JSON file.
    """
    try:
        # Original columns in the Excel file
        selected_columns = [
            "Role #", "Role Title", "Project Client", "Role Description", "Project Industry",
            "Role Fulfillment L4", "Role Location Type", "Role Management Level From",
            "Role Management Level To", "Role Primary Skill", "Role Skills",
            "Role Primary Contact", "Role Start Date", "Role End Date", "Role Primary Skill Category Group",
            "Role Type", "Role Status", "Role Create Date"
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
            "Role Primary Skill Category Group": "capability",
            "Role Type":"roleType", 
            "Role Status":"roleStatus", 
            "Role Create Date":"roleCreateDate"
        }

        unique_roles = {}  # Dictionary to ensure unique roleId values

        # Process the "Database" sheet with opportunity_type = "Database"
        read_sheet_and_convert(file_path, "Database", selected_columns, column_mapping, "Database", unique_roles)

        # Process the "1k" sheet with opportunity_type = "1k"
        #read_sheet_and_convert(file_path, "1k", selected_columns, column_mapping, "1k", unique_roles)

        # Convert dictionary values to a list for JSON output
        final_data = list(unique_roles.values())

        # Save the JSON file
        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(final_data, json_file, indent=4, ensure_ascii=False)

        print(f"JSON file saved successfully at: {output_json_path}")

    except Exception as e:
        print(f"Error: {e}")

# File paths
file_path = "/Users/julio.c.gomez.valdez/Documents/Demanda/Demand.xlsb"
output_json_path = "/Users/julio.c.gomez.valdez/Documents/Demanda/demand_output.json"

# Run the function
excel_xlsb_to_json(file_path, output_json_path)
