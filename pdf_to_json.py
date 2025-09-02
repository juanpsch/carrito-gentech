import camelot
import pandas as pd
import json
import os
import re
import sys
import numpy as np

def procesarDf(df: pd.DataFrame) -> pd.DataFrame:
    """
    Limpia y procesa un DataFrame extraído de un PDF para estructurar los datos
    de productos y categorías.

    Esta función realiza los siguientes pasos:
    1. Limpia los datos eliminando espacios y filas vacías.
    2. Renombra las columnas para una mejor legibilidad.
    3. Propaga las descripciones de productos y las categorías a las filas correspondientes,
       manejando celdas combinadas y saltos de línea.
    4. Elimina las filas de categoría y cualquier otra fila irrelevante.
    5. Elimina las filas de producto que no pudieron ser categorizadas.
    6. Reordena las columnas para una presentación más lógica.

    Args:
        df (pd.DataFrame): El DataFrame original extraído directamente del PDF.

    Returns:
        pd.DataFrame: Un DataFrame limpio y estructurado con productos,
                      sus descripciones y categorías.
    """
    # 1. Limpieza inicial del DataFrame
    # Eliminar espacios extra de todas las celdas
    df = df.applymap(lambda x: str(x).strip() if isinstance(x, str) else x)

    # Eliminar filas que están completamente vacías
    df.dropna(how='all', inplace=True)

    # Eliminar la fila de encabezado que a veces se extrae
    df = df[~df.iloc[:, 0].str.contains('DESCRIPCIÓN', na=False)]

    # 2. Reorganizar los encabezados y datos
    df.columns = ['DESCRIPCIÓN', 'PRESENTACIÓN', 'CONTENIDO NETO', 'CANTIDAD POR BULTO', 'PRECIO UNITARIO NETO', 'PRECIO UNITARIO CON IVA']

    # 3. Propagación de descripciones de productos y categorías
    df_combined = df.copy()

    # Propagar las descripciones de productos, buscando tanto hacia adelante (ffill)
    # como hacia atrás (bfill) para manejar celdas combinadas.
    df_combined['temp_DESCRIPCIÓN'] = df_combined['DESCRIPCIÓN'].replace('', pd.NA).ffill().bfill()

    # Identificar y propagar las categorías.
    category_keywords = ['LINEA ALTO RENDIMIENTO', 'LINEA PREMIUM', 'LINEA IRON', 'LINEA BEAUTY', 'LINEA PRE_WORKOUT', 'LINEA NUTRICION',
                         'LINEA KIDS', 'LINEA VEGGIE PLANT BASED', 'ACCESORIOS']
    
    # Función para encontrar la categoría en una fila.
    def find_category(row):
        row_str = ' '.join(str(val) for val in row.tolist()).upper()
        for keyword in category_keywords:
            if keyword in row_str:
                cleaned_name = re.sub(r'(LÍNEA|LINEA)\s*', '', keyword, flags=re.IGNORECASE).strip()
                return cleaned_name
        return None

    df_combined['Categoria'] = df_combined.apply(find_category, axis=1)
    df_combined['Categoria'] = df_combined['Categoria'].replace('', pd.NA).ffill()

    # 4. Crear el DataFrame final y limpiar
    # Se filtra el DataFrame para incluir solo las filas con un precio válido.
    df_processed = df_combined[df_combined['PRECIO UNITARIO CON IVA'].apply(lambda x: str(x).strip() != '')].copy()

    # Asignar la descripción propagada a la columna principal.
    df_processed['DESCRIPCIÓN'] = df_processed['temp_DESCRIPCIÓN']

    # 5. Limpiar y reordenar el DataFrame final
    df_processed.drop(columns=['temp_DESCRIPCIÓN'], inplace=True)
    df_processed.reset_index(drop=True, inplace=True)

    # Eliminar las filas donde no se pudo asignar una categoría.
    df_processed = df_processed.dropna(subset=['Categoria'])
    df_processed.reset_index(drop=True, inplace=True)

    # Opcional: Reordenar las columnas.
    column_order = ['Categoria', 'DESCRIPCIÓN'] + [col for col in df_processed.columns if col not in ['Categoria', 'DESCRIPCIÓN']]
    df_processed = df_processed[column_order]

    return df_processed

# --- Lógica principal del script ---
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Uso: python pdf_to_json_pipeline.py <ruta_del_pdf> <ruta_del_json_destino>")
        sys.exit(1)

    pdf_file_path = sys.argv[1]
    output_json_file = sys.argv[2]
    
    if not os.path.exists(pdf_file_path):
        print(f"Error: El archivo PDF '{pdf_file_path}' no se encontró.")
        sys.exit(1)

    try:
        print(f"🕵️‍♂️ Extrayendo tablas de '{pdf_file_path}' usando el método 'hybrid'...")
        tables = camelot.read_pdf(pdf_file_path, flavor='hybrid', pages='1', table_areas=['50,780,800,0'])

        if tables.n == 0:
            print("❌ No se encontraron tablas. Verifique las coordenadas o el tipo de tabla.")
            sys.exit(1)

        # Usar la función procesarDf para limpiar y estructurar el DataFrame
        df_final = procesarDf(tables[0].df.copy())
        
        # Convertir el DataFrame procesado a una lista de diccionarios
        final_data = df_final.to_dict('records')
        
        # Escribir los datos en el archivo JSON
        with open(output_json_file, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, ensure_ascii=False, indent=4)
        
        print(f"✅ ¡Éxito! {len(final_data)} productos procesados y guardados en '{output_json_file}'.")

    except Exception as e:
        print(f"❌ Ocurrió un error inesperado durante el procesamiento: {e}")







### Para ejecutar el script con los nuevos parámetros, usa el siguiente comando en tu terminal:

## ```bash
### python pdf_to_json.py "LISTA DE PRECIOS DISTRIBUIDOR - GENTECH - SEPTIEMBRE 2025.pdf" "Gentech_Sep-25_distribuidor.json"
### python pdf_to_json.py "LISTA DE PRECIOS MAYORISTA - GENTECH - SEPTIEMBRE 2025.pdf" "Gentech_Sep-25_mayorista.json"
### python pdf_to_json.py "LISTA DE PRECIOS MINORISTA - GENTECH - SEPTIEMBRE 2025.pdf" "Gentech_Sep-25_minorista.json"
