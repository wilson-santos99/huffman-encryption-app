# Importación de módulos necesarios
import heapq           # Para estructuras de cola de prioridad
from collections import defaultdict  # Para manejo eficiente de frecuencias
import graphviz        # Para generación de gráficos del árbol
import os              # Para operaciones del sistema de archivos

class Node:
    """Representa un nodo en el árbol de Huffman"""
    def __init__(self, char=None, freq=None):
        self.char = char  # Carácter (solo en nodos hoja)
        self.freq = freq  # Frecuencia del carácter/suma de frecuencias
        self.left = None  # Referencia al hijo izquierdo (bit 0)
        self.right = None # Referencia al hijo derecho (bit 1)

    def __lt__(self, other):
        """Permite comparar nodos por frecuencia para el ordenamiento"""
        return self.freq < other.freq

def calculate_frequencies(phrase):
    """
    Calcula la frecuencia de cada carácter en la frase de entrada
    
    Args:
        phrase (str): Cadena de texto a analizar
        
    Returns:
        defaultdict: Diccionario con caracteres como keys y frecuencias como valores
    """
    return defaultdict(int, {char: phrase.count(char) for char in phrase})

def build_huffman_tree(frequencies):
    """
    Construye el árbol de Huffman a partir de las frecuencias de caracteres
    
    Args:
        frequencies (dict): Diccionario de frecuencias de caracteres
        
    Returns:
        Node: Nodo raíz del árbol construido
    """
    heap = []
    count = 0  # Contador para mantener orden con frecuencias iguales
    
    # Crear nodo inicial para cada carácter
    for char, freq in frequencies.items():
        heapq.heappush(heap, (freq, count, Node(char, freq)))
        count += 1

    # Combinar nodos hasta tener un solo árbol
    while len(heap) > 1:
        # Extraer los dos nodos con menor frecuencia
        freq1, _, left = heapq.heappop(heap)
        freq2, _, right = heapq.heappop(heap)
        
        # Crear nuevo nodo interno combinando los dos nodos
        merged = Node(None, freq1 + freq2)
        merged.left = left
        merged.right = right
        
        # Insertar el nodo combinado de vuelta al heap
        heapq.heappush(heap, (merged.freq, count, merged))
        count += 1

    return heap[0][2]  # Retorna el nodo raíz del árbol

def generate_codes(node, prefix='', codebook=None):
    """
    Genera los códigos binarios recursivamente recorriendo el árbol
    
    Args:
        node (Node): Nodo actual del árbol
        prefix (str): Prefijo del código hasta este nodo
        codebook (dict): Diccionario para almacenar los códigos
        
    Returns:
        dict: Diccionario completo con los códigos Huffman
    """
    if codebook is None:
        codebook = {}
    
    # Si es nodo hoja, almacenar el código generado
    if node.char is not None:
        codebook[node.char] = prefix
    
    # Recorrer subárbol izquierdo (bit 0)
    if node.left:
        generate_codes(node.left, prefix + '0', codebook)
    
    # Recorrer subárbol derecho (bit 1)
    if node.right:
        generate_codes(node.right, prefix + '1', codebook)
    
    return codebook

def encrypt(phrase, codebook):
    """
    Encripta una frase usando la tabla de códigos generada
    
    Args:
        phrase (str): Texto a encriptar
        codebook (dict): Diccionario de codificación Huffman
        
    Returns:
        str: Mensaje encriptado como secuencia binaria
    """
    return ''.join(codebook[char] for char in phrase)

def generate_tree_image(root):
    """
    Genera una representación visual del árbol de Huffman
    
    Args:
        root (Node): Nodo raíz del árbol
        
    Returns:
        graphviz.Digraph: Objeto gráfico del árbol
    """
    # Configuración básica del gráfico
    dot = graphviz.Digraph(
        graph_attr={
            'rankdir': 'TB',    # Orientación Top-to-Bottom
            'bgcolor': 'white', # Fondo blanco
            'dpi': '150'        # Resolución media
        }
    )
    
    # Configuración de estilo para los nodos
    dot.attr('node', 
             shape='circle',    # Forma circular
             style='filled',    # Relleno de color
             fillcolor='white', # Color de relleno
             color='black',     # Color del borde
             fontname='Arial',  # Tipografía
             fontsize='12',     # Tamaño de fuente
             penwidth='1.5')    # Grosor del borde
    
    # Configuración de estilo para las conexiones
    dot.attr('edge',
             color='black',     # Color de línea
             arrowsize='0.7',   # Tamaño de flecha
             penwidth='1.2',    # Grosor de línea
             fontname='Arial',  # Tipografía
             fontsize='10')     # Tamaño de fuente
    
    def add_nodes_edges(node):
        """
        Función auxiliar recursiva para construir el gráfico
        
        Args:
            node (Node): Nodo actual del árbol
        """
        if node:
            # Crear etiqueta según tipo de nodo
            label = f"{node.char}:{node.freq}" if node.char else str(node.freq)
            
            # Añadir nodo al gráfico
            dot.node(str(id(node)), label=label)
            
            # Añadir conexión izquierda (bit 0) si existe
            if node.left:
                dot.edge(str(id(node)), str(id(node.left)), label='0')
                add_nodes_edges(node.left)  # Llamada recursiva
            
            # Añadir conexión derecha (bit 1) si existe
            if node.right:
                dot.edge(str(id(node)), str(id(node.right)), label='1')
                add_nodes_edges(node.right)  # Llamada recursiva
    
    # Iniciar la construcción del gráfico desde la raíz
    add_nodes_edges(root)
    return dot

def huffman_encrypt(phrase):
    """
    Ejecuta el proceso completo de encriptación Huffman
    
    Args:
        phrase (str): Texto a encriptar
        
    Returns:
        tuple: (mensaje_encriptado, imagen_arbol, codebook, raiz_arbol)
    """
    # 1. Calcular frecuencias de caracteres
    frequencies = calculate_frequencies(phrase)
    
    # 2. Construir el árbol de Huffman
    root = build_huffman_tree(frequencies)
    
    # 3. Generar la tabla de códigos
    codebook = generate_codes(root)
    
    # 4. Encriptar el mensaje
    encrypted_message = encrypt(phrase, codebook)
    
    # 5. Generar la imagen del árbol
    tree_image = generate_tree_image(root)
    
    return encrypted_message, tree_image, codebook, root

def huffman_decrypt(binary_string, root):
    """
    Desencripta un mensaje usando el árbol de Huffman
    
    Args:
        binary_string (str): Mensaje binario a desencriptar
        root (Node): Raíz del árbol de Huffman original
        
    Returns:
        str: Mensaje desencriptado
    """
    result = []      # Para almacenar el resultado
    current = root   # Comenzar desde la raíz
    
    # Recorrer cada bit del mensaje
    for bit in binary_string:
        # Navegar por el árbol según el bit
        current = current.left if bit == '0' else current.right
        
        # Si llegamos a un nodo hoja
        if current.char is not None:
            result.append(current.char)  # Agregar carácter al resultado
            current = root               # Volver a la raíz
    
    # Unir todos los caracteres encontrados
    return ''.join(result)