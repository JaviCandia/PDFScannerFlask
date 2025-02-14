import pandas as pd
import json

def convert_values(value):
    """
    Converts values properly:
    - If a number has .0, it is converted to an integer.
    - If a number is in the Excel date format, it is converted to 'YYYY-MM-DD'.
    - Empty or NaN values are converted to empty strings.
    """
    if pd.isna(value) or value in ["nan", "NaN", "None"]:  # Manejo de valores NaN
        return ""

    try:
        # Intentar convertir a número
        num = float(value)

        # Si es un número entero, verificar si es una fecha de Excel
        if num.is_integer():
            excel_start_date = pd.Timestamp("1899-12-30")  # Corrección de fechas de Excel
            converted_date = excel_start_date + pd.to_timedelta(int(num), unit="D")

            # Si la fecha es razonable (posterior a 1900 y antes de 2100), devolverla formateada
            if pd.Timestamp("1900-01-01") <= converted_date <= pd.Timestamp("2100-12-31"):
                return converted_date.strftime("%Y-%m-%d")  # Convertir a formato 'YYYY-MM-DD'

            return int(num)  # Si no es fecha válida, convertirlo a entero normal
        
        return str(value)  # Convertir todo lo demás a string
    
    except ValueError:
        return str(value)  # Si no es numérico, devolverlo como string

def read_sheet_and_convert(file_path, sheet_name, selected_columns, column_mapping, opportunity_type_value):
    """
    Reads a sheet from the XLSB file, extracts specific columns, renames them, 
    properly formats values, and adds the opportunity_type field.
    """
    try:
        # Leer el archivo XLSB con todos los valores como string
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='pyxlsb', dtype=str)

        # Verificar si las columnas existen en el archivo
        missing_columns = [col for col in selected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in sheet {sheet_name}: {missing_columns}")

        # Filtrar DataFrame con las columnas requeridas
        filtered_df = df[selected_columns]

        # Renombrar columnas según el diccionario de mapeo
        filtered_df = filtered_df.rename(columns=column_mapping)

        # Reemplazar NaN con valores vacíos
        filtered_df = filtered_df.fillna("")

        # 🔥 ELIMINAR FILAS QUE ESTÁN COMPLETAMENTE VACÍAS 🔥
        filtered_df = filtered_df.replace("", pd.NA).dropna(how="all")

        # Convertir valores correctamente
        filtered_df = filtered_df.applymap(convert_values)

        # Convertir a JSON
        json_data = filtered_df.to_dict(orient='records')

        # Agregar el campo "opportunity_type" con el valor de la hoja
        for record in json_data:
            record["opportunity_type"] = opportunity_type_value

        return json_data

    except Exception as e:
        print(f"Error processing sheet {sheet_name}: {e}")
        return []

# Función para leer y procesar el Excel
def excel_xlsb_to_json(file_path, output_json_path):
    try:
        # Columnas originales en el archivo Excel
        selected_columns = [
            "Role #", "Role Title", "Project Client", "Role Description", "Project Industry",
            "Role Fulfillment L4", "Role Location Type", "Role Management Level From",
            "Role Management Level To", "Role Primary Skill", "Role Skills",
            "Role Primary Contact", "Role Start Date", "Role End Date", "Role Primary Skill Category Group"
        ]

        # Diccionario para cambiar los nombres en el JSON de salida
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

        # Procesar la hoja "Database" con opportunity_type = "Database"
        data_database = read_sheet_and_convert(file_path, "Database", selected_columns, column_mapping, "Database")

        # Procesar la hoja "1k" con opportunity_type = "1k"
        data_1k = read_sheet_and_convert(file_path, "1k", selected_columns, column_mapping, "1k")

        # Fusionar ambas listas de datos
        final_data = data_database + data_1k

        # Guardar el JSON en un archivo
        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(final_data, json_file, indent=4, ensure_ascii=False)

        print(f"JSON file saved successfully at: {output_json_path}")

    except Exception as e:
        print(f"Error: {e}")

# Ruta del archivo XLSB
file_path = "C:\\Users\\julio.c.gomez.valdez\\Downloads\\Demand.xlsb"
output_json_path = "C:\\Users\\julio.c.gomez.valdez\\Downloads\\output.json"

# Ejecutar la función
excel_xlsb_to_json(file_path, output_json_path)