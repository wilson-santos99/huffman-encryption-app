import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // Estados de la aplicación
  const [phrase, setPhrase] = useState(''); // Almacena la frase a encriptar
  const [encrypted, setEncrypted] = useState(''); // Almacena el mensaje encriptado
  const [treeImageUrl, setTreeImageUrl] = useState(''); // URL de la imagen del árbol
  const [codebook, setCodebook] = useState({}); // Diccionario de códigos Huffman
  const [decrypted, setDecrypted] = useState(''); // Mensaje desencriptado
  const [loading, setLoading] = useState(false); // Estado de carga
  const [error, setError] = useState(null); // Mensajes de error

  /**
   * Maneja la descarga del árbol en formato PDF
   * @async
   */
  const handleDownloadPDF = async () => {
    try {
      setLoading(true);
      setError(null); // Limpiar errores previos
      
      // Hacer petición para obtener el PDF
      const response = await axios.get("http://localhost:5000/static/huffman_tree.pdf", {
        responseType: "blob", // Especificar que esperamos un archivo binario
        timeout: 10000 // Timeout de 10 segundos
      });
      
      // Validar que recibimos datos
      if (!response.data) {
        throw new Error('No se recibieron datos del PDF');
      }

      // Crear enlace temporal para descarga
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "huffman_tree.pdf"); // Forzar descarga
      document.body.appendChild(link);
      link.click(); // Simular click
      link.remove(); // Limpiar el DOM
    } catch (error) {
      console.error("Error al descargar PDF:", error);
      // Mostrar error específico si está disponible, o mensaje genérico
      setError(error.response?.data?.error || "Error al descargar el PDF. Verifica que el árbol haya sido generado.");
    } finally {
      setLoading(false); // Terminar estado de carga
    }
  };

  /**
   * Maneja el envío del formulario para encriptar la frase
   * @param {Event} e - Evento del formulario
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null); // Resetear errores
    
    // Validación básica
    if (!phrase.trim()) {
      setError("Por favor ingresa una frase válida.");
      return;
    }

    try {
      setLoading(true);
      // Petición al backend para encriptar
      const response = await axios.post('http://localhost:5000/api/encrypt', {
        phrase
      }, {
        timeout: 10000 // Timeout de 10 segundos
      });

      // Validar estructura de respuesta
      if (!response.data?.encrypted_message || !response.data?.codebook) {
        throw new Error('Respuesta del servidor incompleta');
      }

      // Actualizar estados con la respuesta
      setEncrypted(response.data.encrypted_message);
      setTreeImageUrl(`/static/huffman_tree.png?t=${Date.now()}`); // Timestamp para evitar caché
      setCodebook(response.data.codebook);
      setDecrypted(''); // Resetear desencriptado anterior
    } catch (err) {
      console.error(err);
      // Priorizar mensajes de error: respuesta del servidor > mensaje de error > genérico
      const errorMessage = err.response?.data?.error || 
                         err.message || 
                         "Error al encriptar la frase. Verifica tu conexión.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Maneja la desencriptación del mensaje
   */
  const handleDecrypt = async () => {
    // Validación silenciosa (el botón ya está deshabilitado si no hay contenido)
    if (!encrypted || !phrase) return;
    
    try {
      setLoading(true);
      setError(null);
      // Petición al backend para desencriptar
      const response = await axios.post('http://localhost:5000/api/decrypt', {
        binary: encrypted,
        original: phrase
      }, {
        timeout: 10000
      });

      // Validar respuesta
      if (!response.data?.decrypted_message) {
        throw new Error('No se recibió mensaje desencriptado');
      }

      // Actualizar estado con mensaje desencriptado
      setDecrypted(response.data.decrypted_message);
    } catch (err) {
      console.error(err);
      // Manejo de errores similar a handleSubmit
      const errorMessage = err.response?.data?.error || 
                         err.message || 
                         "Error al desencriptar el mensaje.";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Encriptador Huffman</h1>
      
      {/* Mostrar indicador de carga */}
      {loading && <div className="loading">Cargando...</div>}
      
      {/* Mostrar mensajes de error si existen */}
      {error && <div className="error-message">{error}</div>}

      {/* Formulario principal */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={phrase}
          onChange={(e) => {
            setPhrase(e.target.value);
            setError(null); // Limpiar errores al editar
          }}
          placeholder="Escribe tu frase"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>
          Encriptar
        </button>
      </form>

      {/* Mostrar resultados solo si hay mensaje encriptado */}
      {encrypted && (
        <>
          {/* Mensaje encriptado */}
          <section>
            <h2>Mensaje Encriptado:</h2>
            <div className="encrypted-message">{encrypted}</div>
          </section>

          {/* Tabla de códigos Huffman */}
          {Object.keys(codebook).length > 0 && (
            <section className="codebook-section">
              <h2>Códigos binarios por carácter:</h2>
              <div className="codebook-container">
                <table>
                  <thead>
                    <tr>
                      <th>Carácter</th>
                      <th>Código Binario</th>
                    </tr>
                  </thead>
                  <tbody>
                    {Object.entries(codebook).map(([char, code]) => (
                      <tr key={`row-${char}`}>
                        <td>{char === ' ' ? '[espacio]' : char}</td>
                        <td>{code}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </section>  
          )}

          {/* Visualización del árbol */}
          {treeImageUrl && (
            <section className="tree-section">
              <h2>Árbol de Huffman:</h2>
              <div className="tree-image-container">
                <img
                  src={`http://localhost:5000${treeImageUrl}`}
                  alt="Árbol Huffman"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = 'placeholder-tree.png'; // Fallback si la imagen no carga
                  }}
                />
              </div>
              <button 
                onClick={handleDownloadPDF} 
                disabled={loading || !treeImageUrl}
              >
                Descargar Árbol en PDF
              </button>
            </section>
          )}

          {/* Tabla de frecuencias - DENTRO DEL BLOQUE encrypted */}
          <section className="frequency-section">
            <h3>Frecuencias de Caracteres</h3>
            <div className="frequency-table">
              <table>
                {Object.entries(
                  phrase.split('').reduce((acc, char) => ({ 
                    ...acc, 
                    [char]: (acc[char] || 0) + 1 
                  }), {})
                ).map(([char, freq]) => (
                  <tr key={char}>
                    <td>{char === ' ' ? '[espacio]' : char}</td>
                    <td>{freq}</td>
                  </tr>
                ))}
              </table>
            </div>
          </section>
        </>
      )}

      {/* Sección de desencriptación - solo visible con mensaje encriptado */}
      {encrypted && (
        <section className="decrypt-section">
          <button 
            onClick={handleDecrypt} 
            disabled={loading} // Deshabilitar solo durante carga
          >
            Desencriptar
          </button>
          {/* Mostrar resultado de desencriptación */}
          {decrypted && (
            <div className="decrypted-message">
              <h2>Mensaje Desencriptado:</h2>
              <p>{decrypted}</p>
            </div>
          )}
        </section>
      )}
    </div>
  );
}

export default App;