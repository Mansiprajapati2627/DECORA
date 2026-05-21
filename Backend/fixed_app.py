from flask import Flask, send_from_directory, jsonify
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'decora_admin_secret_key_2025'

# Backend/ is the current dir, so root is one level up
ROOT_DIR    = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')
IMG_DIR      = os.path.join(ROOT_DIR, 'img')

print(f"📁 ROOT:     {ROOT_DIR}")
print(f"📁 FRONTEND: {FRONTEND_DIR}")
print(f"📁 IMG:      {IMG_DIR}")

@app.route('/')
def serve_home():
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"Server Error: {str(e)}", 500

@app.route('/img/<path:filename>')
def serve_image(filename):
    """Serve images from the root img/ folder"""
    try:
        return send_from_directory(IMG_DIR, filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        return f"Image {filename} not found", 404

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve all other static files from frontend/"""
    try:
        if '.' not in filename:
            filename += '.html'
        file_path = os.path.join(FRONTEND_DIR, filename)
        if not os.path.exists(file_path):
            return f"File {filename} not found", 404
        return send_from_directory(FRONTEND_DIR, filename)
    except Exception as e:
        logger.error(f"Error serving {filename}: {str(e)}")
        return f"Error: {str(e)}", 404

@app.route('/test')
def test():
    return jsonify({
        "message": "✅ API is working!",
        "frontend": FRONTEND_DIR,
        "img": IMG_DIR
    })

if __name__ == '__main__':
    print("🚀 Starting DECORA Server...")
    app.run(debug=True, port=5000, host='0.0.0.0')