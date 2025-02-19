import pandas as pd

def convert_values(value):
    if pd.isna(value) or value in ["nan", "NaN", "None"]:
        return ""
    try:
        num = float(value)
        if num.is_integer():
            excel_start_date = pd.Timestamp("1899-12-30")
            converted_date = excel_start_date + pd.to_timedelta(int(num), unit="D")
            if pd.Timestamp("1900-01-01") <= converted_date <= pd.Timestamp("2100-12-31"):
                return converted_date.strftime("%Y-%m-%d")
            return int(num)
        return str(value)
    except ValueError:
        return str(value)

def read_sheet_and_convert(file, sheet_name, selected_columns, column_mapping, opportunity_type_value):
    try:
        df = pd.read_excel(file, sheet_name=sheet_name, engine='pyxlsb', dtype=str)
        missing_columns = [col for col in selected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in sheet {sheet_name}: {missing_columns}")
        filtered_df = df[selected_columns]
        filtered_df = filtered_df.rename(columns=column_mapping)
        filtered_df = filtered_df.fillna("")
        filtered_df = filtered_df.replace("", pd.NA).dropna(how="all")
        filtered_df = filtered_df.applymap(convert_values)
        json_data = filtered_df.to_dict(orient='records')
        for record in json_data:
            record["opportunity_type"] = opportunity_type_value
        return json_data
    except Exception as e:
        print(f"Error processing sheet {sheet_name}: {e}")
        return []

selected_columns = [
    "Role #", "Role Title", "Project Client", "Role Description", "Project Industry",
    "Role Fulfillment L4", "Role Location Type", "Role Management Level From",
    "Role Management Level To", "Role Primary Skill", "Role Skills",
    "Role Primary Contact", "Role Start Date", "Role End Date", "Role Primary Skill Category Group"
]

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