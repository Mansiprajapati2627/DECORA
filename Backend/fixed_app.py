from flask import Flask, send_from_directory, jsonify
import os
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'decora_admin_secret_key_2025'

# Get the absolute path to the current directory
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
print(f"📁 BASE DIRECTORY: {BASE_DIR}")

@app.route('/')
def serve_home():
    """Serve the main homepage"""
    try:
        index_path = os.path.join(BASE_DIR, 'index.html')
        print(f"🔍 Looking for index.html at: {index_path}")
        print(f"📄 File exists: {os.path.exists(index_path)}")
        
        if os.path.exists(index_path):
            return send_from_directory(BASE_DIR, 'index.html')
        else:
            # Create a simple homepage if index.html doesn't exist
            return f"""
            <html>
                <body>
                    <h1>DECORA Events Server is Running! 🚀</h1>
                    <p>But index.html was not found at: {index_path}</p>
                    <p>Files in directory:</p>
                    <ul>
                        {"".join([f"<li>{f}</li>" for f in os.listdir(BASE_DIR) if f.endswith('.html')])}
                    </ul>
                    <a href="/test">Test API</a>
                </body>
            </html>
            """, 404
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return f"Server Error: {str(e)}", 500

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve all static files"""
    try:
        # Add .html extension if no extension is present
        if '.' not in filename:
            filename += '.html'
            
        file_path = os.path.join(BASE_DIR, filename)
        print(f"🔍 Looking for: {filename} at {file_path}")
        print(f"📄 File exists: {os.path.exists(file_path)}")
        
        if not os.path.exists(file_path):
            return f"File {filename} not found at {file_path}", 404
            
        return send_from_directory(BASE_DIR, filename)
    except Exception as e:
        logger.error(f"Error serving {filename}: {str(e)}")
        return f"Error: {str(e)}", 404

@app.route('/img/<path:filename>')
def serve_image(filename):
    """Serve images from the img/ subfolder"""
    img_dir = os.path.join(BASE_DIR, 'img')
    try:
        return send_from_directory(img_dir, filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        return f"Image {filename} not found", 404

@app.route('/test')
def test():
    return jsonify({"message": "✅ API is working!", "directory": BASE_DIR})

if __name__ == '__main__':
    print("🚀 Starting FIXED DECORA Server...")
    print("📁 Base directory:", BASE_DIR)
    print("📄 HTML files available:")
    for file in os.listdir(BASE_DIR):
        if file.endswith('.html'):
            print(f"   ✅ {file}")
    
    app.run(debug=True, port=5000, host='0.0.0.0')