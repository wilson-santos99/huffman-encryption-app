# Importaciones necesarias para el módulo de rutas Flask
from flask import Blueprint, request, jsonify, send_file
from .huffman import huffman_encrypt, huffman_decrypt
from .huffman import build_huffman_tree, calculate_frequencies
import os  # Para manejo de rutas de archivos
import time  # Para generar timestamps únicos

# Creamos un Blueprint para organizar las rutas relacionadas con Huffman
huffman_bp = Blueprint('huffman', __name__)

# Ruta básica de salud del servidor
@huffman_bp.route('/api/health', methods=['GET'])
def health_check():
    # Simple endpoint para verificar que el backend está funcionando
    return jsonify({"status": "Backend funcionando correctamente"})

# Ruta para encriptar mensajes usando Huffman
@huffman_bp.route('/api/encrypt', methods=['POST'])
def encrypt_message():
    # Obtenemos los datos JSON del request
    data = request.json
    phrase = data.get('phrase')
    
    # Validamos que se haya proporcionado una frase
    if not phrase:
        return jsonify({"error": "Falta la frase a encriptar"}), 400

    try:
        # 1. Encriptamos la frase usando las funciones del módulo huffman
        encrypted_message, tree_image, codebook, _ = huffman_encrypt(phrase)

        # 2. Configuramos el directorio de salida para las imágenes
        output_dir = os.path.abspath(os.path.join('app', 'static'))
        os.makedirs(output_dir, exist_ok=True)  # Creamos el directorio si no existe
        base_output_path = os.path.join(output_dir, 'huffman_tree')
        
        # 3. Generamos los archivos de imagen (PNG y PDF) del árbol
        tree_image.render(base_output_path, format='png', cleanup=True)
        tree_image.render(base_output_path, format='pdf', cleanup=True)

        # 4. Retornamos la respuesta con los datos necesarios
        timestamp = int(time.time())  # Timestamp para evitar caché del navegador
        return jsonify({
            'encrypted_message': encrypted_message,
            'tree_image_path': f'/static/huffman_tree.png?t={timestamp}',  # Ruta de la imagen
            'codebook': codebook  # Tabla de códigos Huffman
        })
    except Exception as e:
        # Manejo de errores genéricos
        return jsonify({'error': str(e)}), 500

# Ruta para servir archivos estáticos (imágenes del árbol)
@huffman_bp.route('/static/<path:filename>')
def serve_static(filename):
    # Obtenemos la ruta absoluta del directorio static
    static_dir = os.path.abspath(os.path.join('app', 'static'))
    # Enviamos el archivo solicitado
    return send_file(os.path.join(static_dir, filename))

# Ruta para desencriptar mensajes
@huffman_bp.route('/api/decrypt', methods=['POST'])
def decrypt():
    # Obtenemos los datos del request
    data = request.json
    binary_string = data.get('binary')  # Mensaje encriptado en binario
    original_phrase = data.get('original')  # Frase original para reconstruir el árbol
    
    # Validamos que tengamos todos los datos necesarios
    if not binary_string or not original_phrase:
        return jsonify({'error': 'Datos incompletos para desencriptar'}), 400
    
    try:
        # 1. Reconstruimos el árbol de Huffman usando la frase original
        root = build_huffman_tree(calculate_frequencies(original_phrase))
        
        # 2. Desencriptamos el mensaje binario
        decrypted_message = huffman_decrypt(binary_string, root)
        
        # 3. Retornamos el mensaje desencriptado
        return jsonify({'decrypted_message': decrypted_message})
    except Exception as e:
        # Manejo de errores
        return jsonify({'error': str(e)}), 500