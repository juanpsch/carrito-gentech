# tienda/views.py

import json
import os
from django.shortcuts import render
from django.http import Http404, HttpRequest
from typing import List, Dict, Any, Union

# Define los nombres de los archivos JSON disponibles.
# Asume que los archivos están en la misma carpeta que el archivo original.
DATA_FILES = {
    'minorista': 'Gentech_Sep-25_minorista.json',
    'mayorista': 'Gentech_Sep-25_mayorista.json',
    'distribuidor': 'Gentech_Sep-25_distribuidor.json',
}


def get_data_path(filename: str) -> str:
    """
    Construye la ruta absoluta al archivo de datos.
    Esto es una buena práctica para evitar errores de ruta.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, filename)


def load_products_data(filename: str) -> List[Dict[str, Union[str, int, float]]]:
    """
    Carga los datos de los productos desde un archivo JSON específico,
    asigna un ID único y limpia las claves.
    """
    data_path = get_data_path(filename)
    try:
        with open(data_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            clean_products = []
            for i, item in enumerate(data):
                clean_item = {
                    'ID': i + 1,  # Asigna un ID único basado en el índice
                    'Categoria': item.get('Categoria', 'Sin Categoría'),
                    'DESCRIPCION': item.get('DESCRIPCIÓN'),
                    'PRESENTACION': item.get('PRESENTACIÓN'),
                    'CONTENIDO_NETO': item.get('CONTENIDO NETO'),
                    'CANTIDAD_POR_BULTO': item.get('CANTIDAD POR BULTO'),
                    'PRECIO_UNITARIO_NETO': item.get('PRECIO UNITARIO NETO'),
                    'PRECIO_UNITARIO_CON_IVA': item.get('PRECIO UNITARIO CON IVA')
                }
                clean_products.append(clean_item)
            return clean_products

    except FileNotFoundError:
        print(f"Error: El archivo de datos '{data_path}' no fue encontrado.")
        return []


def catalogo(request: HttpRequest) -> render:
    """
    Muestra la página principal con los productos.
    Permite seleccionar la lista de precios a través del parámetro 'source' en la URL.
    """
    # Obtiene la clave de la lista de precios desde el parámetro 'source' en la URL.
    # Si no se especifica, usa 'minorista' como valor por defecto.
    source_key = request.GET.get('source', 'minorista')

    # Valida si la clave existe en la lista de archivos disponibles
    if source_key not in DATA_FILES:
        source_key = 'minorista' # Vuelve a la opción por defecto si no es válida

    # Carga los productos usando el archivo correspondiente
    selected_file = DATA_FILES[source_key]
    products = load_products_data(selected_file)

    # Segmenta los productos por categoría
    categorized_products = {}
    for producto in products:
        categoria = producto.get('Categoria', 'Sin categoría')
        if categoria not in categorized_products:
            categorized_products[categoria] = []
        categorized_products[categoria].append(producto)

    # Prepara el contexto para el template
    context = {
        'categorized_products': categorized_products,
        'data_sources': DATA_FILES.keys(), # Pasa las opciones disponibles al template
        'selected_source': source_key, # Pasa la opción seleccionada para resaltarla
    }
    return render(request, 'tienda/catalogo.html', context)


def detalle_producto(request: HttpRequest, id: int) -> Union[render, Http404]:
    """
    Muestra los detalles de un solo producto.
    Nota: Esta vista no cambia porque solo muestra un producto a la vez.
    """
    # Asume que los productos se cargan desde la lista minorista para esta vista
    products = load_products_data(DATA_FILES['minorista'])
    producto = next((p for p in products if str(p.get('ID')) == str(id)), None)
    if not producto:
        raise Http404("Producto no encontrado.")

    context = {
        'producto': producto
    }
    return render(request, 'tienda/detalle_producto.html', context)