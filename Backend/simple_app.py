from flask import Flask
import os

app = Flask(__name__)

print("📍 Current directory:", os.getcwd())
print("📁 Files:", os.listdir('.'))

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DECORA - Test</title>
        <style>
            body { font-family: Arial; margin: 40px; background: #f0f0f0; }
            .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎉 DECORA Events - TEST PAGE</h1>
            <p>If you can see this, Flask is working!</p>
            <p>Current directory: """ + os.getcwd() + """</p>
            <h3>HTML files found:</h3>
            <ul>
    """ + ''.join([f"<li>{f}</li>" for f in os.listdir('.') if f.endswith('.html')]) + """
            </ul>
        </div>
    </body>
    </html>
    """

if __name__ == '__main__':
    print("🚀 Starting SIMPLE Flask server...")
    app.run(debug=True, port=5000, host='0.0.0.0')