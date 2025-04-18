from flask import Flask
from flask_cors import CORS

def create_app():
    """Crea y configura la aplicación Flask principal"""
    
    # Inicializa la app Flask
    app = Flask(__name__, static_folder='static')  
    # __name__ = nombre del módulo actual
    # static_folder = carpeta para archivos estáticos (CSS, imágenes)
    
    # Habilita CORS (permite peticiones desde frontend)
    CORS(app)
    
    # Importa y registra las rutas del blueprint
    from .routes import huffman_bp
    app.register_blueprint(huffman_bp)
    
    return app