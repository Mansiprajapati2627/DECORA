from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS
import os
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'decora_admin_secret_key_2025'

CORS(app, supports_credentials=True)

# Directories
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
FRONTEND_DIR = os.path.join(ROOT_DIR, 'frontend')
IMG_DIR = os.path.join(ROOT_DIR, 'img')

print(f"📁 ROOT: {ROOT_DIR}")
print(f"📁 FRONTEND: {FRONTEND_DIR}")
print(f"📁 IMG: {IMG_DIR}")

# Temporary user storage
users = []

# =========================
# FRONTEND ROUTES
# =========================

@app.route('/')
def serve_home():
    return send_from_directory(FRONTEND_DIR, 'index.html')

@app.route('/img/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMG_DIR, filename)

@app.route('/<path:filename>')
def serve_static(filename):

    if '.' not in filename:
        filename += '.html'

    file_path = os.path.join(FRONTEND_DIR, filename)

    if not os.path.exists(file_path):
        return f"File {filename} not found", 404

    return send_from_directory(FRONTEND_DIR, filename)

# =========================
# AUTH ROUTES
# =========================

@app.route('/api/register', methods=['POST'])
def register():

    data = request.json

    name = data.get('name') or data.get('full_name')
    email = data.get('email')
    password = data.get('password')

    # Check if already exists
    for user in users:
        if user['email'] == email:
            return jsonify({
                "success": False,
                "message": "User already exists"
            })

    new_user = {
        "name": name,
        "email": email,
        "password": password
    }

    users.append(new_user)

    session['user'] = {
        "name": name,
        "email": email
    }

    return jsonify({
        "success": True,
        "message": "Registration successful",
        "user": session['user']
    })

@app.route('/api/login', methods=['POST'])
def login():

    data = request.json

    email = data.get('email')
    password = data.get('password')

    for user in users:

        if user['email'] == email and user['password'] == password:

            session['user'] = {
                "name": user['name'],
                "email": user['email']
            }

            return jsonify({
                "success": True,
                "message": "Login successful",
                "user": session['user']
            })

    return jsonify({
        "success": False,
        "message": "Invalid email or password"
    })

@app.route('/api/check-auth')
def check_auth():

    if 'user' in session:
        return jsonify({
            "logged_in": True,
            "user": session['user']
        })

    return jsonify({
        "logged_in": False
    })

@app.route('/api/logout', methods=['POST'])
def logout():

    session.pop('user', None)

    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    })


# =========================
# BOOKINGS ROUTE
# =========================

bookings = []

@app.route('/api/bookings', methods=['POST'])
def create_booking():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Please login to book."})
    data = request.json
    booking = {
        "booking_id": f"DEC{len(bookings)+1:04d}",
        "user": session['user']['email'],
        "bookingname": data.get('bookingname'),
        "phone": data.get('phone'),
        "event": data.get('event'),
        "date": data.get('date'),
        "time": data.get('time'),
    }
    bookings.append(booking)
    return jsonify({"success": True, "booking_id": booking['booking_id'], "message": "Booking confirmed!"})

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    return jsonify({"success": True, "bookings": bookings})

# =========================
# REVIEWS ROUTE
# =========================

reviews = []

@app.route('/api/reviews', methods=['POST'])
def create_review():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Please login to submit a review."})
    data = request.json
    review = {
        "review_id": f"REV{len(reviews)+1:04d}",
        "user": session['user']['email'],
        "reviewname": data.get('reviewname') or session['user'].get('name') or session['user']['email'].split('@')[0],
        "rating": data.get('rating'),
        "review": data.get('review'),
    }
    reviews.append(review)
    return jsonify({"success": True, "message": "Review submitted successfully!"})

@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    return jsonify({"success": True, "reviews": reviews})

# =========================
# CUSTOMIZATIONS ROUTE
# =========================

customizations = []

@app.route('/api/customizations', methods=['POST'])
def create_customization():
    if 'user' not in session:
        return jsonify({"success": False, "message": "Please login to submit a customization request."})
    data = request.json
    custom = {
        "custom_id": f"CUS{len(customizations)+1:04d}",
        "user": session['user']['email'],
        "customName": data.get('customName') or session['user'].get('name'),
        "customEventType": data.get('customEventType'),
        "customDate": data.get('customDate'),
        "customTime": data.get('customTime'),
        "customDescription": data.get('customDescription'),
    }
    customizations.append(custom)
    return jsonify({"success": True, "message": "Customization request submitted!"})

@app.route('/api/customizations', methods=['GET'])
def get_customizations():
    return jsonify({"success": True, "customizations": customizations})

# =========================
# TEST ROUTE
# =========================

@app.route('/test')
def test():

    return jsonify({
        "message": "✅ DECORA backend working!",
        "frontend": FRONTEND_DIR,
        "img": IMG_DIR
    })

# =========================
# START APP
# =========================

if __name__ == '__main__':
    print("🚀 Starting DECORA Server...")
    app.run(debug=True, port=5000, host='0.0.0.0')