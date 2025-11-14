import { useState, useEffect } from "react";
import "./App.css";

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [pdfPreview, setPdfPreview] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [downloadUrl, setDownloadUrl] = useState("");
  const [toast, setToast] = useState("");

  // URL del backend en producción
  const BACKEND_URL = "https://arki-production.up.railway.app";

  const carouselImages = [
    "/carousel1.png",
    "/carousel2.png",
    "/carousel3.png",
    "/carousel4.png",
  ];

  const [currentIndex, setCurrentIndex] = useState(0);

  // Carrusel automático
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentIndex((prev) =>
        prev + 1 === carouselImages.length ? 0 : prev + 1
      );
    }, 2500);
    return () => clearInterval(interval);
  }, []);

  // Progreso
  useEffect(() => {
    if (isProcessing) {
      setProgress(0);
      const interval = setInterval(() => {
        setProgress((prev) => (prev >= 90 ? 90 : prev + 10));
      }, 250);
      return () => clearInterval(interval);
    }
  }, [isProcessing]);

  // Selección archivo
  const handleFileSelect = (e) => {
    const file = e.target.files[0];

    if (file?.type === "application/pdf") {
      setSelectedFile(file);
      setDownloadUrl("");

      const previewURL = URL.createObjectURL(file);
      setPdfPreview(previewURL);
    }
  };

  // Eliminar archivo
  const removeFile = () => {
    setSelectedFile(null);
    setPdfPreview("");
    setDownloadUrl("");
  };

  // Subir archivo - ACTUALIZADO para producción
  const handleUpload = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);

    const formData = new FormData();
    formData.append("pdf", selectedFile);

    try {
      const res = await fetch(`${BACKEND_URL}/api/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      const data = await res.json();

      if (res.ok) {
        setProgress(100);
        setTimeout(() => {
          setToast("PDF procesado exitosamente!");
          setDownloadUrl(`${BACKEND_URL}${data.download_url}`);
        }, 400);
      } else {
        setToast(data.error || "Error procesando el PDF");
      }
    } catch (err) {
      setToast("Error de conexión con el servidor");
    } finally {
      setTimeout(() => setIsProcessing(false), 600);
      setTimeout(() => setToast(""), 4000);
    }
  };

  return (
    <div className="app">
      {/* Sidebar */}
      <div className="sidebar">
        <img
          src="/logo.png"
          className="sidebar-logo"
          alt="Logo"
          onClick={() => window.location.reload()}
        />
      </div>

      {/* Main Content */}
      <div className="main">
        {/* Header */}
        <div className="header">
          <div className="logo-box-header">
            <img src="/logo.png" alt="ARKI LOGO" />
          </div>

          <div className="header-right">
            <span>Optimizar PDF</span>
            <img src="/icono.png" alt="User" className="user-icon" />
          </div>
        </div>

        {/* Content */}
        <div className="content">
          {/* Carrusel */}
          <div className="carousel">
            <img src={carouselImages[currentIndex]} alt="carousel" />
          </div>

          {/* Upload */}
          <div className="upload-container">
            <input
              type="file"
              accept=".pdf"
              id="pdf-input"
              className="file-input"
              onChange={handleFileSelect}
            />

            <label htmlFor="pdf-input" className="upload-button">
              {selectedFile ? selectedFile.name : "Selecciona un archivo PDF"}
            </label>

            {selectedFile && !isProcessing && !downloadUrl && (
              <button className="process-btn" onClick={handleUpload}>
                Procesar PDF
              </button>
            )}
          </div>

          {/* Progreso */}
          {isProcessing && (
            <div className="progress-bar">
              <div className="progress" style={{ width: `${progress}%` }} />
            </div>
          )}

          {downloadUrl && (
            <div className="download-section">
              <button className="reset-btn" onClick={removeFile}>
                Volver a optimizar
              </button>

              <a href={downloadUrl} download className="download-btn">
                Descargar PDF
              </a>
            </div>
          )}
        </div>
      </div>

      {/* Toast */}
      {toast && <div className="toast">{toast}</div>}
    </div>
  );
}

export default App;
