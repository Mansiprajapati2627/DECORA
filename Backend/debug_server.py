import os
from flask import Flask, send_from_directory

app = Flask(__name__)

# Print current working directory and files
print("🔍 Current working directory:", os.getcwd())
print("📁 Files in current directory:")
for file in os.listdir('.'):
    print(f"   - {file}")

@app.route('/')
def serve_home():
    """Serve the main homepage"""
    try:
        # Check if index.html exists
        if os.path.exists('index.html'):
            print("✅ index.html found!")
            return send_from_directory('.', 'index.html')
        else:
            print("❌ index.html NOT found!")
            return "index.html not found in current directory", 404
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return f"Error serving index.html: {str(e)}", 500

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve all static files including HTML pages"""
    try:
        print(f"📄 Requested file: {filename}")
        if not os.path.exists(filename):
            print(f"❌ File {filename} not found!")
            return f"File {filename} not found", 404
        return send_from_directory('.', filename)
    except Exception as e:
        print(f"❌ Error serving {filename}: {str(e)}")
        return f"Error serving {filename}: {str(e)}", 404

if __name__ == '__main__':
    print("🚀 Starting Debug Server...")
    app.run(debug=True, port=5001, host='0.0.0.0')