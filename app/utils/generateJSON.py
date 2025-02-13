import pandas as pd
import json

def convert_values(value):
    """
    Converts values properly:
    - If a number has .0, it is converted to an integer.
    - If a number is in the Excel date format, it is converted to 'YYYY-MM-DD'.
    - Other values remain as strings.
    """
    try:
        # Intentar convertir a número
        num = float(value)

        # Si es un número entero, verificar si es una fecha de Excel
        if num.is_integer():
            excel_start_date = pd.Timestamp("1899-12-30")  # Excel starts from 1900-01-01 but pandas needs offset -1
            converted_date = excel_start_date + pd.to_timedelta(int(num), unit="D")

            # Si la fecha es razonable (por ejemplo, posterior a 1900 y antes de 2100), devolverla formateada
            if pd.Timestamp("1900-01-01") <= converted_date <= pd.Timestamp("2100-12-31"):
                return converted_date.strftime("%Y-%m-%d")  # Convertir a formato 'YYYY-MM-DD'

            return int(num)  # Si no es fecha válida, convertirlo a entero normal
        
        return str(value)  # Convertir todo lo demás a string
    
    except ValueError:
        return str(value)  # Si no es numérico, devolverlo como string

def excel_xlsb_to_json(file_path, sheet_name, selected_columns, column_mapping, output_json_path):
    """
    Reads an XLSB file from a specific sheet, extracts specific columns, renames them, 
    properly formats numeric values and dates, and saves the data as a JSON file.

    :param file_path: Path to the XLSB file.
    :param sheet_name: Name of the sheet to read.
    :param selected_columns: List of column names to include in the JSON.
    :param column_mapping: Dictionary to rename columns in the output JSON.
    :param output_json_path: Path to save the JSON file.
    """
    try:
        # Leer el archivo XLSB con todos los valores como string para evitar conversiones automáticas
        df = pd.read_excel(file_path, sheet_name=sheet_name, engine='pyxlsb', dtype=str)

        # Mostrar las columnas disponibles para depuración
        print("Available columns in the sheet:", df.columns.tolist())

        # Verificar si las columnas existen en el archivo
        missing_columns = [col for col in selected_columns if col not in df.columns]
        if missing_columns:
            raise ValueError(f"Missing columns in the file: {missing_columns}")

        # Filtrar DataFrame con las columnas requeridas
        filtered_df = df[selected_columns]

        # Renombrar columnas según el diccionario de mapeo
        filtered_df = filtered_df.rename(columns=column_mapping)

        # Convertir valores correctamente (manejo de números, fechas y strings)
        filtered_df = filtered_df.applymap(convert_values)

        # Convertir a JSON
        json_data = filtered_df.to_dict(orient='records')

        # Guardar el JSON en un archivo
        with open(output_json_path, 'w', encoding='utf-8') as json_file:
            json.dump(json_data, json_file, indent=4, ensure_ascii=False)

        print(f"JSON file saved successfully at: {output_json_path}")

    except Exception as e:
        print(f"Error: {e}")
# Ejemplo de uso
file_path = "C:\\Users\\julio.c.gomez.valdez\\Downloads\\Demand.xlsb"  # Ruta del archivo XLSB
sheet_name = "Database"  # Nombre de la hoja en el archivo
output_json_path = "C:\\Users\\julio.c.gomez.valdez\\Downloads\\output.json"
# Columnas originales en el archivo Excel
selected_columns = ["Role #", "Role Title", "Project Client","Role Description","Project Industry" ,"Role Fulfillment L4",
                    "Role Location Type","Role Management Level From" ,"Role Management Level To","Role Primary Skill",
                    "Role Skills","Role Primary Contact","Role Start Date","Role End Date",
                    "Role Primary Skill Category Group"] 


# Diccionario para cambiar los nombres en el JSON de salida
column_mapping = {
   "Role #":"roleId", 
    "Role Title":"roleName", 
"Project Client":"project",
"Role Description":"description",
"Project Industry":"industry",
"Role Fulfillment L4":"location",
"Role Location Type":"locationType",
"Role Management Level From":"level",
"Role Management Level To":"level2",
"Role Primary Skill":"mainSkill",
"Role Skills":"secondarySkill",
"Role Primary Contact":"contact",
"Role End Date":"endDate",
"Role Start Date":"startDate",
"Role Primary Skill Category Group":"capability",
}


excel_xlsb_to_json(file_path, sheet_name, selected_columns, column_mapping, output_json_path)
