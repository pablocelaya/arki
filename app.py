from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from pdf2image import convert_from_path
import img2pdf
import tempfile


app = Flask(__name__)
CORS(app)

# ===============================================
#   RUTA LOCAL DE POPPLER (DENTRO DEL PROYECTO)
# ===============================================
POPLER_PATH = r"C:\Users\gato4\Desktop\Proyectos Personales\ARKI\poppler\Library\bin"

# Carpetas
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  #  MB ---- revisar

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ========================================================
#   ÚNICA FUNCIÓN → APLANADO REAL (PDF → IMAGEN → PDF)
#   200 DPI FIJOS — SIN SEGURIDAD — SIN OPCIONES
# ========================================================
def flatten_pdf_200dpi(input_path, output_path):
    """
    Convierte cada página del PDF a imagen (200 dpi)
    y reconstruye un PDF completamente aplanado.
    """
    try:
        # Convertir a imágenes a 200 DPI
        images = convert_from_path(
            input_path,
            dpi=300,
            poppler_path=POPLER_PATH
        )

        # Guardar imágenes temporales
        temp_paths = []
        for i, img in enumerate(images):
            temp_path = f"temp_page_{i}.png"
            img.save(temp_path, "PNG")
            temp_paths.append(temp_path)

        # Convertir imágenes → PDF final
        with open(output_path, "wb") as f:
            f.write(img2pdf.convert(temp_paths))

        # Eliminar imágenes temporales
        for path in temp_paths:
            if os.path.exists(path):
                os.remove(path)

        return True

    except Exception as e:
        print(f"[ERROR flatten_pdf_200dpi] {e}")
        return False


# ========================================================
#   ENDPOINT PRINCIPAL
# ========================================================
@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No se encontró el archivo PDF'}), 400

        file = request.files['pdf']

        if file.filename == '':
            return jsonify({'error': 'No se seleccionó archivo'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Solo se permiten PDF'}), 400

        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        output_filename = f"aplanado_{filename}"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)

        # Aplanado único a 200 DPI
        success = flatten_pdf_200dpi(input_path, output_path)

        if success:
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            return jsonify({
                'message': 'PDF aplanado correctamente a 200 DPI',
                'download_url': f'/api/download/{output_filename}',
                'size_mb': round(size_mb, 2),
                'dpi': 200,
                'status': 'OK'
            })

        return jsonify({'error': 'Error al aplanar el PDF'}), 500

    except Exception as e:
        print(f"[ERROR upload_pdf] {e}")
        return jsonify({'error': str(e)}), 500


# ========================================================
#   ENDPOINT DOWNLOAD
# ========================================================
@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    path = os.path.join(PROCESSED_FOLDER, filename)

    if not os.path.exists(path):
        return jsonify({'error': 'Archivo no encontrado'}), 404

    return send_file(path, as_attachment=True, download_name=filename)


# ========================================================
#   HEALTH CHECK
# ========================================================
@app.route('/api/health')
def health():
    return jsonify({'status': 'OK'})


# Agrega esto ANTES del if __name__ == '__main__':

@app.route('/')
def home():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>ARKI PDF Server</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 ARKI PDF Server</h1>
            <p>Servidor backend para procesamiento y protección de PDFs</p>
            
            <h2>Endpoints disponibles:</h2>
            <div class="endpoint">
                <strong>GET /api/health</strong> - Estado del servidor
            </div>
            <div class="endpoint">
                <strong>POST /api/upload-pdf</strong> - Subir y procesar PDF
            </div>
            <div class="endpoint">
                <strong>GET /api/download/&lt;filename&gt;</strong> - Descargar PDF procesado
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/health')
def health():
    return jsonify({
        'status': 'OK',
        'message': 'ARKI PDF Server is running',
        'timestamp': '2025-11-14T17:52:00Z'
    })


# ========================================================
#   RUN SERVER
# ========================================================
# Cambia esto al final:
import os

# ... todo tu código anterior ...

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f"🚀 Starting ARKI PDF Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)