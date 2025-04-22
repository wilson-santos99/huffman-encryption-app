# Importaciones necesarias para el módulo de rutas Flask
from flask import Blueprint, request, jsonify, send_file  # Funciones de Flask para crear rutas y manejar peticiones/respuestas
from .huffman import huffman_encrypt, huffman_decrypt     # Funciones para encriptar y desencriptar usando Huffman
from .huffman import build_huffman_tree, calculate_frequencies  # Funciones auxiliares para reconstruir el árbol de Huffman
import os  # Para manejo de rutas de archivos
import time  # Para generar timestamps únicos y evitar caché en imágenes

# Creamos un Blueprint para organizar las rutas relacionadas con Huffman
huffman_bp = Blueprint('huffman', __name__)

# Ruta de prueba para verificar que el backend está funcionando
@huffman_bp.route('/api/health', methods=['GET'])
def health_check():
    print("[LOG] - Health check solicitado")  # Registro de actividad
    return jsonify({"status": "Backend funcionando correctamente"})  # Respuesta en formato JSON

# Ruta para encriptar un mensaje usando el algoritmo de Huffman
@huffman_bp.route('/api/encrypt', methods=['POST'])
def encrypt_message():
    print("\n[LOG] - Iniciando proceso de encriptación")  # Registro de inicio
    data = request.json  # Se obtiene el JSON del cuerpo de la petición
    phrase = data.get('phrase')  # Se extrae la frase a encriptar
    
    # Validación: verificar que se haya enviado una frase
    if not phrase:
        print("[ERROR] - Frase vacía recibida")  # Log de error
        return jsonify({"error": "Falta la frase a encriptar"}), 400

    try:
        print(f"[LOG] - Frase recibida: '{phrase}'")  # Log informativo
        
        # Se llama a la función que encripta y genera el árbol y diccionario
        encrypted_message, tree_image, codebook, _ = huffman_encrypt(phrase)
        print("[LOG] - Frase encriptada correctamente")

        # Preparar carpeta de salida para las imágenes del árbol
        output_dir = os.path.abspath(os.path.join('app', 'static'))
        os.makedirs(output_dir, exist_ok=True)
        base_output_path = os.path.join(output_dir, 'huffman_tree')
        
        print("[LOG] - Generando imágenes del árbol...")
        # Renderizar imagen del árbol tanto en PNG como en PDF
        tree_image.render(base_output_path, format='png', cleanup=True)
        tree_image.render(base_output_path, format='pdf', cleanup=True)
        print("[LOG] - Imágenes del árbol generadas")

        # Se agrega un timestamp para evitar que el navegador cachee la imagen
        timestamp = int(time.time())
        print("[LOG] - Proceso de encriptación completado\n")

        # Se envía la respuesta con el mensaje encriptado, path de la imagen y el codebook
        return jsonify({
            'encrypted_message': encrypted_message,
            'tree_image_path': f'/static/huffman_tree.png?t={timestamp}',
            'codebook': codebook
        })
    except Exception as e:
        print(f"[ERROR] - Error durante encriptación: {str(e)}")  # Log de error
        return jsonify({'error': str(e)}), 500  # Error interno del servidor

# Ruta para servir archivos estáticos desde el backend (como imágenes)
@huffman_bp.route('/static/<path:filename>')
def serve_static(filename):
    print(f"[LOG] - Solicitando archivo estático: {filename}")
    static_dir = os.path.abspath(os.path.join('app', 'static'))  # Carpeta de archivos estáticos
    return send_file(os.path.join(static_dir, filename))  # Se envía el archivo solicitado

# Ruta para desencriptar un mensaje binario usando el árbol original
@huffman_bp.route('/api/decrypt', methods=['POST'])
def decrypt():
    print("\n[LOG] - Iniciando proceso de desencriptación")
    data = request.json  # Se obtiene el JSON del cuerpo de la petición
    binary_string = data.get('binary')  # Se extrae el mensaje binario
    original_phrase = data.get('original')  # Se extrae la frase original para reconstruir el árbol

    # Validación de datos
    if not binary_string or not original_phrase:
        print("[ERROR] - Datos incompletos para desencriptar")
        return jsonify({'error': 'Datos incompletos para desencriptar'}), 400

    try:
        print(f"[LOG] - Mensaje binario recibido: {binary_string}")
        print(f"[LOG] - Frase original recibida: '{original_phrase}'")

        # Se reconstruye el árbol con la frase original
        root = build_huffman_tree(calculate_frequencies(original_phrase))
        print("[LOG] - Árbol de Huffman reconstruido")

        # Se desencripta el mensaje binario usando el árbol
        decrypted_message = huffman_decrypt(binary_string, root)
        print(f"[LOG] - Mensaje desencriptado: '{decrypted_message}'")
        print("[LOG] - Proceso de desencriptación completado\n")

        # Se envía el mensaje desencriptado
        return jsonify({'decrypted_message': decrypted_message})
    except Exception as e:
        print(f"[ERROR] - Error durante desencriptación: {str(e)}")  # Log de error
        return jsonify({'error': str(e)}), 500  # Error interno del servidor
