import React, { useState } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  // Estados de la aplicación
  const [phrase, setPhrase] = useState('');
  const [encrypted, setEncrypted] = useState('');
  const [treeImageUrl, setTreeImageUrl] = useState('');
  const [codebook, setCodebook] = useState({});
  const [decrypted, setDecrypted] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [logs, setLogs] = useState([]);

  // Función para agregar logs (solo visibles en la consola)
  const addLog = (message) => {
    const timestamp = new Date().toLocaleTimeString();
    const logMessage = `[${timestamp}] ${message}`;
    setLogs(prev => [logMessage, ...prev].slice(0, 50)); // Se mantiene por si se quiere usar más adelante
    console.log(logMessage); // Solo se imprime en consola
  };

  /**
   * Maneja la descarga del árbol de Huffman en formato PDF
   */
  const handleDownloadPDF = async () => {
    try {
      setLoading(true);
      setError(null);
      addLog("Iniciando descarga del árbol en PDF...");

      const response = await axios.get("http://localhost:5000/static/huffman_tree.pdf", {
        responseType: "blob",
        timeout: 10000
      });

      if (!response.data) {
        addLog("Error: No se recibieron datos del PDF");
        throw new Error('No se recibieron datos del PDF');
      }

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", "huffman_tree.pdf");
      document.body.appendChild(link);
      link.click();
      link.remove();

      addLog("Árbol descargado exitosamente en formato PDF");
    } catch (error) {
      const errorMsg = error.response?.data?.error || "Error al descargar el PDF";
      addLog(`Error en descarga: ${errorMsg}`);
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Maneja el envío del formulario para encriptar la frase
   */
  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!phrase.trim()) {
      addLog("Validación fallida: No se ingresó ninguna frase");
      setError("Por favor ingresa una frase válida.");
      return;
    }

    try {
      setLoading(true);
      addLog(`Iniciando encriptación de la frase: "${phrase}"`);

      const response = await axios.post('http://localhost:5000/api/encrypt', { phrase }, { timeout: 10000 });

      if (!response.data?.encrypted_message || !response.data?.codebook) {
        addLog("Error: Respuesta del servidor incompleta");
        throw new Error('Respuesta del servidor incompleta');
      }

      setEncrypted(response.data.encrypted_message);
      setTreeImageUrl(`/static/huffman_tree.png?t=${Date.now()}`); // Forzar actualización de imagen
      setCodebook(response.data.codebook);
      setDecrypted('');

      addLog(`Frase encriptada exitosamente: ${response.data.encrypted_message}`);
      addLog("Tabla de códigos recibida:");
      Object.entries(response.data.codebook).forEach(([char, code]) => {
        addLog(`  "${char === ' ' ? '[espacio]' : char}": ${code}`);
      });
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || "Error al encriptar la frase";
      addLog(`Error en encriptación: ${errorMessage}`);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  /**
   * Maneja la desencriptación del mensaje binario usando la frase original
   */
  const handleDecrypt = async () => {
    if (!encrypted || !phrase) return;

    try {
      setLoading(true);
      setError(null);
      addLog(`Iniciando desencriptación del mensaje binario: ${encrypted}`);
      addLog(`Usando frase original para reconstruir árbol: "${phrase}"`);

      const response = await axios.post('http://localhost:5000/api/decrypt', {
        binary: encrypted,
        original: phrase
      }, {
        timeout: 10000
      });

      if (!response.data?.decrypted_message) {
        addLog("Error: No se recibió mensaje desencriptado");
        throw new Error('No se recibió mensaje desencriptado');
      }

      setDecrypted(response.data.decrypted_message);
      addLog(`Mensaje desencriptado exitosamente: "${response.data.decrypted_message}"`);
    } catch (err) {
      const errorMessage = err.response?.data?.error || err.message || "Error al desencriptar el mensaje";
      addLog(`Error en desencriptación: ${errorMessage}`);
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <h1>Encriptador Huffman</h1>

      {/* Indicador de carga */}
      {loading && <div className="loading">Cargando...</div>}

      {/* Mensaje de error */}
      {error && <div className="error-message">{error}</div>}

      {/* Formulario para ingresar frase */}
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={phrase}
          onChange={(e) => {
            setPhrase(e.target.value);
            setError(null);
          }}
          placeholder="Escribe tu frase"
          disabled={loading}
        />
        <button type="submit" disabled={loading}>Encriptar</button>
      </form>

      {/* Resultados tras encriptación */}
      {encrypted && (
        <>
          {/* Mostrar mensaje encriptado */}
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

          {/* Imagen del árbol Huffman */}
          {treeImageUrl && (
            <section className="tree-section">
              <h2>Árbol de Huffman:</h2>
              <div className="tree-image-container">
                <img
                  src={`http://localhost:5000${treeImageUrl}`}
                  alt="Árbol Huffman"
                  onError={(e) => {
                    e.target.onerror = null;
                    e.target.src = 'placeholder-tree.png';
                  }}
                />
              </div>
              <button onClick={handleDownloadPDF} disabled={loading || !treeImageUrl}>
                Descargar Árbol en PDF
              </button>
            </section>
          )}

          {/* Tabla de frecuencias de caracteres */}
          <section className="frequency-section">
            <h3>Frecuencias de Caracteres</h3>
            <div className="frequency-table">
              <table>
                <tbody>
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
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}

      {/* Sección de desencriptación */}
      {encrypted && (
        <section className="decrypt-section">
          <button onClick={handleDecrypt} disabled={loading}>Desencriptar</button>
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
