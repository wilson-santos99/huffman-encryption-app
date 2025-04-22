# Importaciones necesarias desde Flask y los módulos internos de Huffman
from flask import Blueprint, request, jsonify, send_file
from .huffman import huffman_encrypt, huffman_decrypt
from .huffman import build_huffman_tree, calculate_frequencies
import os
import time

# Se crea un blueprint para las rutas relacionadas con Huffman
huffman_bp = Blueprint('huffman', __name__)

# Ruta de prueba para verificar que el backend está funcionando
@huffman_bp.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({"status": "Backend funcionando correctamente"})

# Ruta para encriptar un mensaje usando Huffman
@huffman_bp.route('/api/encrypt', methods=['POST'])
def encrypt_message():
    data = request.json                     # Se obtiene el JSON enviado desde el frontend
    phrase = data.get('phrase')            # Se extrae la frase a encriptar
    
    if not phrase:
        return jsonify({"error": "Falta la frase a encriptar"}), 400  # Si no hay frase, se retorna error

    try:
        # Se realiza la encriptación usando el algoritmo de Huffman
        encrypted_message, tree_image, codebook, _ = huffman_encrypt(phrase)

        # Se define la carpeta de salida donde se guardará la imagen del árbol
        output_dir = os.path.abspath(os.path.join('app', 'static'))
        os.makedirs(output_dir, exist_ok=True)
        base_output_path = os.path.join(output_dir, 'huffman_tree')
        
        # Se renderiza el árbol como imagen PNG y PDF
        tree_image.render(base_output_path, format='png', cleanup=True)
        tree_image.render(base_output_path, format='pdf', cleanup=True)

        # Se agrega un timestamp para evitar el caché del navegador
        timestamp = int(time.time())
        
        # Se retorna el mensaje encriptado, la ruta de la imagen y el codebook (tabla de codificación)
        return jsonify({
            'encrypted_message': encrypted_message,
            'tree_image_path': f'/static/huffman_tree.png?t={timestamp}',
            'codebook': codebook
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500  # Si algo falla, se devuelve un error 500

# Ruta para servir archivos estáticos como la imagen del árbol
@huffman_bp.route('/static/<path:filename>')
def serve_static(filename):
    static_dir = os.path.abspath(os.path.join('app', 'static'))
    return send_file(os.path.join(static_dir, filename))

# Ruta para desencriptar un mensaje binario usando el árbol de Huffman original
@huffman_bp.route('/api/decrypt', methods=['POST'])
def decrypt():
    data = request.json
    binary_string = data.get('binary')         # Se obtiene la cadena binaria
    original_phrase = data.get('original')     # Se obtiene la frase original para reconstruir el árbol
    
    if not binary_string or not original_phrase:
        return jsonify({'error': 'Datos incompletos para desencriptar'}), 400

    try:
        # Se reconstruye el árbol de Huffman usando la frase original
        root = build_huffman_tree(calculate_frequencies(original_phrase))
        
        # Se desencripta el mensaje binario
        decrypted_message = huffman_decrypt(binary_string, root)
        return jsonify({'decrypted_message': decrypted_message})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
