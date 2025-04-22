# Importación de librerías necesarias
import heapq  # Para implementar la cola de prioridad (heap)
from collections import defaultdict  # Para contar frecuencias de caracteres fácilmente
import graphviz  # Para generar la imagen del árbol de Huffman
import os  # Para manejar rutas si es necesario (aunque no se usa en este archivo)

# Clase que representa un nodo en el árbol de Huffman
class Node:
    def __init__(self, char=None, freq=None):
        self.char = char  # Caracter que representa el nodo (hoja)
        self.freq = freq  # Frecuencia del caracter
        self.left = None  # Hijo izquierdo
        self.right = None  # Hijo derecho

    def __lt__(self, other):
        # Permite comparar nodos por frecuencia (necesario para heapq)
        return self.freq < other.freq

# Función para calcular las frecuencias de cada caracter en una frase
def calculate_frequencies(phrase):
    print("\n[HUFFMAN] - Calculando frecuencias de caracteres...")
    freq_dict = defaultdict(int)
    for char in phrase:
        freq_dict[char] += 1

    print("[HUFFMAN] - Frecuencias calculadas:")
    for char, freq in sorted(freq_dict.items()):
        print(f"  '{char}': {freq}")

    return freq_dict

# Función para construir el árbol de Huffman a partir de las frecuencias
def build_huffman_tree(frequencies):
    print("\n[HUFFMAN] - Construyendo árbol de Huffman...")
    heap = []
    count = 0  # Para evitar colisiones si dos nodos tienen la misma frecuencia

    # Insertamos cada nodo hoja en el heap
    for char, freq in frequencies.items():
        heapq.heappush(heap, (freq, count, Node(char, freq)))
        count += 1

    # Iteramos hasta que quede un solo nodo (el raíz)
    while len(heap) > 1:
        item1 = heapq.heappop(heap)
        item2 = heapq.heappop(heap)

        freq1, _, node1 = item1
        freq2, _, node2 = item2

        # Creamos un nuevo nodo interno combinando los dos de menor frecuencia
        merged = Node(freq=freq1 + freq2)
        merged.left = node1
        merged.right = node2

        # Lo volvemos a insertar en el heap
        heapq.heappush(heap, (merged.freq, count, merged))
        count += 1

    print("[HUFFMAN] - Árbol de Huffman construido")
    return heap[0][2]  # Retornamos el nodo raíz

# Función recursiva para generar los códigos binarios Huffman
def generate_codes(node, prefix='', codebook=None):
    if codebook is None:
        codebook = {}

    if node.char is not None:
        # Si es hoja, se guarda el código binario generado
        codebook[node.char] = prefix

    if node.left:
        generate_codes(node.left, prefix + '0', codebook)
    if node.right:
        generate_codes(node.right, prefix + '1', codebook)

    return codebook

# Codifica una frase utilizando un codebook de Huffman
def encrypt(phrase, codebook):
    print("\n[HUFFMAN] - Codificando mensaje...")
    encrypted = []
    for char in phrase:
        encrypted.append(codebook[char])

    print("[HUFFMAN] - Mensaje codificado:")
    print(f"  Original: '{phrase}'")
    print(f"  Codificado: '{''.join(encrypted)}'")

    return ''.join(encrypted)

# Genera una visualización en Graphviz del árbol de Huffman
def generate_tree_image(root):
    print("\n[HUFFMAN] - Generando visualización del árbol...")
    dot = graphviz.Digraph(
        graph_attr={
            'rankdir': 'TB',
            'bgcolor': 'transparent',
            'dpi': '150',
            'fontname': 'Arial'
        }
    )

    # Estilo de los nodos
    dot.attr('node',
             shape='Mrecord',
             style='filled,rounded',
             fillcolor='#F0F8FF:#E6E6FA',
             gradientangle='270',
             color='#4682B4',
             fontname='Arial',
             fontsize='11',
             penwidth='1.5',
             margin='0.15,0.05')

    # Estilo de las aristas
    dot.attr('edge',
             color='#708090',
             arrowsize='0.6',
             penwidth='1.3',
             fontname='Arial',
             fontsize='10')

    # Función recursiva para agregar nodos y conexiones
    def add_nodes_edges(node):
        if node:
            if node.char is not None:
                label = f'{{ {node.freq} | {node.char} }}'
            else:
                label = f'{{ {node.freq} | }}'

            dot.node(str(id(node)), label=label, fillcolor='#F0F8FF:#E6E6FA', fontcolor='#2F4F4F')

            if node.left:
                dot.edge(str(id(node)), str(id(node.left)), label='0')
                add_nodes_edges(node.left)

            if node.right:
                dot.edge(str(id(node)), str(id(node.right)), label='1')
                add_nodes_edges(node.right)

    add_nodes_edges(root)
    print("[HUFFMAN] - Visualización del árbol generada")
    return dot

# Función principal de encriptación Huffman
def huffman_encrypt(phrase):
    frequencies = calculate_frequencies(phrase)
    root = build_huffman_tree(frequencies)
    codebook = generate_codes(root)
    encrypted_message = encrypt(phrase, codebook)
    tree_image = generate_tree_image(root)
    return encrypted_message, tree_image, codebook, root

# Función de desencriptación Huffman
def huffman_decrypt(binary_string, root):
    print("\n[HUFFMAN] - Decodificando mensaje...")
    result = []
    current = root

    for bit in binary_string:
        if bit == '0':
            current = current.left
        else:
            current = current.right

        if current.char is not None:
            # Se encontró una hoja, se agrega el caracter
            result.append(current.char)
            current = root

    decrypted = ''.join(result)
    print(f"[HUFFMAN] - Mensaje decodificado: '{decrypted}'")
    return decrypted
