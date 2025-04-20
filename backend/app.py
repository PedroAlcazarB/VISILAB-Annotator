from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Carpeta donde se guardarán las imágenes
IMAGE_FOLDER = os.path.join(os.getcwd(), 'images')
os.makedirs(IMAGE_FOLDER, exist_ok=True)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No se encontró ninguna imagen'}), 400

    image = request.files['image']

    if image.filename == '':
        return jsonify({'error': 'Nombre de archivo vacío'}), 400

    save_path = os.path.join(IMAGE_FOLDER, image.filename)
    image.save(save_path)

    return jsonify({
        'message': 'Imagen subida correctamente',
        'filename': image.filename
    })

# Ruta para servir imágenes desde la carpeta "images"
@app.route('/images/<filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
