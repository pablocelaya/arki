from flask import Flask, request, jsonify, send_file 
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)
CORS(app)

# Configuración para producción
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Carpetas
UPLOAD_FOLDER = 'uploads'
PROCESSED_FOLDER = 'processed'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024  # 32MB

ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ========================================================
#   FUNCIÓN SIMPLIFICADA (sin pdf2image por ahora)
# ========================================================
def make_pdf_non_editable(input_path, output_path):
    """
    Aplica protección al PDF sin conversión a imágenes
    """
    try:
        with open(input_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            writer = PyPDF2.PdfWriter()

            for page in reader.pages:
                writer.add_page(page)

            # Aplicar protección
            writer.encrypt(
                user_password="",
                owner_password="arki_protection",
                use_128bit=True,
                permissions_flag=0  # bloquear edición/copias
            )

            with open(output_path, 'wb') as out:
                writer.write(out)
        
        return True
    except Exception as e:
        print(f"[ERROR make_pdf_non_editable] {e}")
        return False

# ========================================================
#   ENDPOINTS ESENCIALES
# ========================================================
@app.route('/')
def home():
    return jsonify({
        'status': 'OK',
        'message': 'ARKI PDF Server is running!',
        'service': 'ARKI PDF Processor',
        'version': '1.0.0'
    })

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status': 'OK',
        'timestamp': '2025-11-14T17:52:00Z'
    })

@app.route('/api/upload-pdf', methods=['POST'])
def upload_pdf():
    try:
        if 'pdf' not in request.files:
            return jsonify({'error': 'No PDF file found'}), 400

        file = request.files['pdf']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not allowed_file(file.filename):
            return jsonify({'error': 'Only PDF files allowed'}), 400

        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        output_filename = f"protected_{filename}"
        output_path = os.path.join(PROCESSED_FOLDER, output_filename)

        # Procesar PDF
        if make_pdf_non_editable(input_path, output_path):
            return jsonify({
                'message': 'PDF processed successfully',
                'download_url': f'/api/download/{output_filename}',
                'filename': output_filename
            })
        else:
            return jsonify({'error': 'Failed to process PDF'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<filename>', methods=['GET'])
def download_file(filename):
    try:
        path = os.path.join(PROCESSED_FOLDER, filename)
        
        if not os.path.exists(path):
            return jsonify({'error': 'File not found'}), 404

        return send_file(path, as_attachment=True, download_name=filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ========================================================
#   CONFIGURACIÓN DE PRODUCCIÓN
# ========================================================
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"🚀 Starting ARKI PDF Server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)