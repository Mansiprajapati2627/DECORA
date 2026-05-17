from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
import mysql.connector
import bcrypt
import os
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Get the absolute paths
BACKEND_DIR = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_ROOT, 'frontend')
IMG_DIR = os.path.join(PROJECT_ROOT, 'img')

print(f"📁 Backend directory: {BACKEND_DIR}")
print(f"📁 Project root: {PROJECT_ROOT}")
print(f"📁 Frontend directory: {FRONTEND_DIR}")
print(f"📁 Image directory: {IMG_DIR}")
print(f"📁 Frontend exists: {os.path.exists(FRONTEND_DIR)}")
print(f"📁 Images exists: {os.path.exists(IMG_DIR)}")

if os.path.exists(FRONTEND_DIR):
    print("📄 Files in frontend folder:")
    for file in os.listdir(FRONTEND_DIR):
        print(f"   📄 {file}")

if os.path.exists(IMG_DIR):
    print("🖼️ Images in img folder:")
    for file in os.listdir(IMG_DIR)[:10]:
        print(f"   🖼️ {file}")

# Flask app configuration
app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path='')
app.secret_key = 'decora_admin_secret_key_2025'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False

# Configure CORS properly
CORS(app, 
     supports_credentials=True,
     origins=["http://localhost:5000", "http://127.0.0.1:5000", "http://localhost:8080", "http://127.0.0.1:8080"],
     allow_headers=["Content-Type", "Authorization", "Accept"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# Database configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'decora_events_final'
}

# ===== DEBUG ROUTE =====
@app.route('/api/debug')
def debug_info():
    """Debug endpoint to check server status"""
    return jsonify({
        'status': 'Server is running',
        'frontend_dir': FRONTEND_DIR,
        'frontend_exists': os.path.exists(FRONTEND_DIR),
        'backend_dir': BACKEND_DIR,
        'files_in_frontend': os.listdir(FRONTEND_DIR) if os.path.exists(FRONTEND_DIR) else 'Directory not found',
        'current_working_dir': os.getcwd()
    })

# ===== STATIC FILE SERVING =====
@app.route('/')
def serve_home():
    """Serve the main homepage"""
    try:
        return send_from_directory(FRONTEND_DIR, 'index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        return f"Error serving homepage: {str(e)}", 500

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve all static files (HTML, CSS, JS)"""
    try:
        # Security check
        if '..' in filename or filename.startswith('/'):
            return "Invalid path", 400
        
        # Don't serve API routes as static files
        if filename.startswith('api/'):
            return "Endpoint not found", 404
        
        # If no extension, assume it's an HTML page
        if not '.' in filename:
            filename += '.html'
            
        file_path = os.path.join(FRONTEND_DIR, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {filename}")
            return f"Page not found: {filename}", 404
            
        return send_from_directory(FRONTEND_DIR, filename)
        
    except Exception as e:
        logger.error(f"Error serving {filename}: {str(e)}")
        return f"Error serving {filename}: {str(e)}", 404

# ===== IMAGE SERVING =====
@app.route('/img/<path:filename>')
def serve_images(filename):
    """Serve images from img folder"""
    try:
        return send_from_directory(IMG_DIR, filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {str(e)}")
        return f"Error serving image {filename}: {str(e)}", 404

# ===== AUTHENTICATION APIs =====
@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    try:
        if session.get('user_logged_in'):
            return jsonify({
                'logged_in': True,
                'user': {
                    'id': session.get('user_id'),
                    'name': session.get('user_name'),
                    'email': session.get('user_email')
                }
            })
        return jsonify({'logged_in': False})
    except Exception as e:
        logger.error(f"Error in check_auth: {str(e)}")
        return jsonify({'logged_in': False, 'error': str(e)}), 500

@app.route('/api/register', methods=['POST'])
def register():
    """User registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
            
        full_name = data.get('full_name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([full_name, email, password]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'User already exists'}), 400
            
            # Insert new user
            hashed_password = hash_password(password)
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
                (full_name, email, hashed_password)
            )
            conn.commit()
            
            return jsonify({'success': True, 'message': 'Registration successful'})
            
        except mysql.connector.Error as err:
            return jsonify({'success': False, 'message': f'Database error: {err}'}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in register: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'message': 'Email and password required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check user credentials
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if user:
                if check_password(password, user['password']):
                    session['user_id'] = user['id']
                    session['user_email'] = user['email']
                    session['user_name'] = user['name']
                    session['user_logged_in'] = True
                    
                    return jsonify({
                        'success': True, 
                        'message': 'Login successful',
                        'user': {
                            'id': user['id'],
                            'name': user['name'],
                            'email': user['email']
                        }
                    })
                else:
                    return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
                
        except mysql.connector.Error as err:
            return jsonify({'success': False, 'message': f'Database error: {err}'}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in login: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    """Logout user"""
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logged out successfully'})
    except Exception as e:
        logger.error(f"Error in logout: {str(e)}")
        return jsonify({'success': False, 'message': 'Logout failed'}), 500

# ===== BOOKING APIs =====
# ===== BOOKING APIs =====
@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """Create a new booking - UPDATED to match frontend form fields exactly"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
        
        # Get data from frontend form - using exact field names from your HTML
        bookingname = data.get('bookingname')  # From 'bookingname' input field
        phone = data.get('phone')              # From 'phone' input field
        event_type = data.get('event')         # From 'event' select field
        event_date = data.get('date')          # From 'date' input field
        event_time = data.get('time')          # From 'time' input field
        
        print(f"📋 Received booking data: {data}")  # Debug log
        
        # Check required fields - using exact frontend field names
        if not all([bookingname, phone, event_type, event_date, event_time]):
            missing = []
            if not bookingname: missing.append('bookingname')
            if not phone: missing.append('phone')
            if not event_type: missing.append('event')
            if not event_date: missing.append('date')
            if not event_time: missing.append('time')
            
            print(f"❌ Missing fields: {missing}")  # Debug log
            return jsonify({'success': False, 'message': f'Missing required fields: {", ".join(missing)}'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor()
            
            # Get user_id from session
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'User not logged in'}), 401
            
            # Generate booking_id
            cursor.execute("SELECT COUNT(*) FROM bookings")
            booking_count = cursor.fetchone()[0]
            booking_id = f"B{(booking_count + 1):03d}"
            
            # Set default values for database fields not in the form
            package_type = 'Basic'  # Default value
            theme = 'Standard'      # Default value
            decoration_title = ''   # Default value
            
            cursor.execute(
                """INSERT INTO bookings 
                (booking_id, user_id, bookingname, phone, event_type, event_date, event_time, package_type, theme, decoration_title, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'Pending')""",
                (booking_id, user_id, bookingname, phone, event_type, event_date, event_time, package_type, theme, decoration_title)
            )
            conn.commit()
            
            print(f"✅ Booking created successfully: {booking_id}")  # Debug log
            
            return jsonify({
                'success': True, 
                'message': 'Booking created successfully',
                'booking_id': booking_id
            })
            
        except mysql.connector.Error as err:
            print(f"❌ Database error: {err}")  # Debug log
            return jsonify({'success': False, 'message': str(err)}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in create_booking: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500
    

@app.route('/api/bookings', methods=['GET'])
def get_bookings():
    """Return REAL bookings data from database - UPDATED to match schema"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': True, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT 
                    b.booking_id,
                    b.bookingname as customer,
                    b.phone,
                    b.event_type as service,
                    b.event_date,
                    b.event_time,
                    b.package_type,
                    b.theme,
                    b.decoration_title,
                    b.status,
                    u.name,
                    u.email,
                    b.created_at
                FROM bookings b
                LEFT JOIN users u ON b.user_id = u.id
                ORDER BY b.created_at DESC
            """)
            bookings = cursor.fetchall()
            
            # Format the data for frontend
            formatted_bookings = []
            for booking in bookings:
                formatted_bookings.append({
                    'booking_id': booking['booking_id'],
                    'customer': booking['customer'] or 'Unknown',
                    'service': booking['service'] or 'Unknown',
                    'date': booking['event_date'].strftime('%d %b %Y') if booking['event_date'] else 'N/A',
                    'time': str(booking['event_time']) if booking['event_time'] else 'N/A',
                    'package_type': booking['package_type'] or 'N/A',
                    'theme': booking['theme'] or 'N/A',
                    'decoration_title': booking['decoration_title'] or 'N/A',
                    'phone': booking['phone'] or 'N/A',
                    'email': booking['email'] or 'N/A',
                    'status': booking['status'] or 'Pending'
                })
            
            return jsonify(formatted_bookings)
            
        except mysql.connector.Error as err:
            return jsonify({'error': True, 'message': str(err)}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in get_bookings: {str(e)}")
        return jsonify({'error': True, 'message': 'Server error'}), 500

@app.route('/api/bookings/<booking_id>', methods=['PUT'])
def update_booking_status(booking_id):
    """Update booking status - UPDATED to use booking_id string"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
        
        status = data.get('status')
        if not status:
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE bookings SET status = %s WHERE booking_id = %s",
                (status, booking_id)
            )
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Booking not found'}), 404
            
            conn.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Booking status updated to {status}'
            })
            
        except mysql.connector.Error as err:
            return jsonify({'success': False, 'message': str(err)}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in update_booking_status: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

# ===== CUSTOMIZATION APIs =====
@app.route('/api/customizations', methods=['POST'])
def create_customization():
    """Create a customization request - UPDATED to handle both field naming conventions"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
        
        # Support both field naming conventions
        customName = data.get('customName') or data.get('name')
        customEventType = data.get('customEventType') or data.get('event_type')
        customDate = data.get('customDate') or data.get('event_date')
        customTime = data.get('customTime') or data.get('event_time')
        customDescription = data.get('customDescription') or data.get('special_requests') or data.get('description')
        
        print(f"🔧 Customization data received: {data}")
        print(f"🔧 Parsed fields - Name: {customName}, Event: {customEventType}, Date: {customDate}, Time: {customTime}")
        
        if not all([customName, customEventType, customDate, customTime, customDescription]):
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor()
            
            # Get user_id from session
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'User not logged in'}), 401
            
            # Generate customization_id
            cursor.execute("SELECT COUNT(*) FROM customizations")
            customization_count = cursor.fetchone()[0]
            customization_id = f"C{(customization_count + 1):03d}"
            
            cursor.execute(
                """INSERT INTO customizations 
                (customization_id, user_id, customName, customEventType, customDate, customTime, customDescription, status) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'New')""",
                (customization_id, user_id, customName, customEventType, customDate, customTime, customDescription)
            )
            
            conn.commit()
            
            print(f"✅ Customization created: {customization_id}")
            
            return jsonify({
                'success': True, 
                'message': 'Customization request submitted successfully',
                'customization_id': customization_id
            })
            
        except mysql.connector.Error as err:
            print(f"❌ Database error: {err}")
            return jsonify({'success': False, 'message': str(err)}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in create_customization: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500
    


@app.route('/api/customizations', methods=['GET'])
def get_customizations():
    """Return ALL customization requests from database regardless of status"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': True, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get ALL customizations regardless of status - removed WHERE clause
            cursor.execute("""
                SELECT c.*, u.name, u.email
                FROM customizations c
                LEFT JOIN users u ON c.user_id = u.id
                ORDER BY c.submitted_date DESC
            """)
            customizations = cursor.fetchall()
            
            # Debug: Print what we're getting from database
            print(f"🔧 Found {len(customizations)} customizations in database:")
            for cust in customizations:
                print(f"   - ID: {cust['customization_id']}, Name: {cust['customName']}, Status: {cust['status']}")
            
            # Format dates for frontend
            for cust in customizations:
                if cust['customDate']:
                    cust['customDate'] = cust['customDate'].strftime('%Y-%m-%d')
                if cust['submitted_date']:
                    cust['submitted_date'] = cust['submitted_date'].strftime('%d %b %Y')
                if cust['customTime']:
                    cust['customTime'] = str(cust['customTime'])
            
            return jsonify(customizations)
            
        except mysql.connector.Error as err:
            return jsonify({'error': True, 'message': str(err)}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in get_customizations: {str(e)}")
        return jsonify({'error': True, 'message': 'Server error'}), 500
     
@app.route('/api/customizations/<customization_id>', methods=['PUT'])
def update_customization_status(customization_id):
    """Update customization request status - UPDATED to use customization_id string"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
        
        status = data.get('status')
        if not status:
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE customizations SET status = %s WHERE customization_id = %s",
                (status, customization_id)
            )
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Customization request not found'}), 404
            
            conn.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Customization request status updated to {status}'
            })
            
        except mysql.connector.Error as err:
            return jsonify({'success': False, 'message': str(err)}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in update_customization_status: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

# ===== REVIEW APIs =====
# ===== REVIEW APIs =====
@app.route('/api/reviews', methods=['POST'])
@app.route('/api/reviews', methods=['POST'])
def create_review():
    """Create a review - FIXED rating conversion"""
    try:
        data = request.get_json()
        print(f"📝 Review data received: {data}")
        
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
        
        # Get review data from frontend
        reviewname = data.get('reviewname') or data.get('user_name') or 'Anonymous'
        rating_input = data.get('rating')  # This could be number or stars
        review = data.get('review') or data.get('comment')
        
        print(f"🔍 Parsed review data:")
        print(f"   reviewname: {reviewname}")
        print(f"   rating: {rating_input}")
        print(f"   review: {review}")
        
        # Check required fields
        if not reviewname:
            return jsonify({'success': False, 'message': 'Review name is required'}), 400
        if not rating_input:
            return jsonify({'success': False, 'message': 'Rating is required'}), 400
        if not review:
            return jsonify({'success': False, 'message': 'Review text is required'}), 400
        
        # Convert rating to star format
        rating_map = {
            1: '⭐',
            2: '⭐⭐', 
            3: '⭐⭐⭐',
            4: '⭐⭐⭐⭐',
            5: '⭐⭐⭐⭐⭐'
        }
        
        # Handle both numeric and star ratings
        if isinstance(rating_input, int):
            rating_stars = rating_map.get(rating_input, '⭐⭐⭐')
        elif '⭐' in str(rating_input):
            rating_stars = rating_input
        else:
            # Try to convert string to int
            try:
                rating_num = int(rating_input)
                rating_stars = rating_map.get(rating_num, '⭐⭐⭐')
            except:
                rating_stars = '⭐⭐⭐'  # Default
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor()
            
            # Get user_id from session
            user_id = session.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'User not logged in'}), 401
            
            # Insert review
            cursor.execute(
                "INSERT INTO reviews (user_id, reviewname, rating, review, status) VALUES (%s, %s, %s, %s, 'Pending')",
                (user_id, reviewname, rating_stars, review)
            )
            conn.commit()
            
            print(f"✅ Review submitted successfully by user {user_id}")
            
            return jsonify({'success': True, 'message': 'Review submitted successfully'})
            
        except mysql.connector.Error as err:
            print(f"❌ Database error: {err}")
            return jsonify({'success': False, 'message': f'Database error: {err}'}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
                
    except Exception as e:
        logger.error(f"Error in create_review: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500
    
@app.route('/api/reviews', methods=['GET'])
def get_reviews():
    """Get all reviews for display - UPDATED to match database schema"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': True, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT r.*, u.name as user_name
                FROM reviews r
                LEFT JOIN users u ON r.user_id = u.id
                WHERE r.status = 'Approved'
                ORDER BY r.created_at DESC
            """)
            reviews = cursor.fetchall()
            
            return jsonify(reviews)
            
        except mysql.connector.Error as err:
            return jsonify({'error': True, 'message': str(err)}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in get_reviews: {str(e)}")
        return jsonify({'error': True, 'message': 'Server error'}), 500
    
@app.route('/api/reviews/<review_id>', methods=['PUT'])
def update_review_status(review_id):
    """Update review status"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
        
        status = data.get('status')
        if not status:
            return jsonify({'success': False, 'message': 'Status is required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor()
            
            cursor.execute(
                "UPDATE reviews SET status = %s WHERE id = %s",
                (status, review_id)
            )
            
            if cursor.rowcount == 0:
                return jsonify({'success': False, 'message': 'Review not found'}), 404
            
            conn.commit()
            
            return jsonify({
                'success': True, 
                'message': f'Review status updated to {status}'
            })
            
        except mysql.connector.Error as err:
            return jsonify({'success': False, 'message': str(err)}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in update_review_status: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500    

# ===== ADMIN DASHBOARD APIs =====
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login using admin table"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'No JSON data received'}), 400
            
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Check admin credentials from admin table
            cursor.execute("SELECT * FROM admin WHERE username = %s", (username,))
            admin = cursor.fetchone()
            
            if admin:
                # Simple password comparison
                if admin['password'] == password:
                    session['admin_logged_in'] = True
                    session['admin_username'] = admin['username']
                    
                    return jsonify({
                        'success': True, 
                        'message': 'Admin login successful',
                        'admin': {
                            'username': admin['username']
                        }
                    })
                else:
                    return jsonify({'success': False, 'message': 'Invalid password'}), 401
            else:
                return jsonify({'success': False, 'message': 'Admin user not found'}), 401
                
        except mysql.connector.Error as err:
            return jsonify({'success': False, 'message': str(err)}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in admin_login: {str(e)}")
        return jsonify({'success': False, 'message': 'Server error'}), 500

@app.route('/api/dashboard/stats')
def dashboard_stats():
    """Return REAL dashboard statistics from database - FIXED rating calculation"""
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': True, 'message': 'Database connection failed'}), 500
        
        try:
            cursor = conn.cursor(dictionary=True)
            
            # Get total bookings count
            cursor.execute("SELECT COUNT(*) as count FROM bookings")
            total_bookings = cursor.fetchone()['count']
            
            # Get pending bookings
            cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'Pending'")
            pending_bookings = cursor.fetchone()['count']
            
            # Get completed bookings
            cursor.execute("SELECT COUNT(*) as count FROM bookings WHERE status = 'Completed'")
            completed_bookings = cursor.fetchone()['count']
            
            # Get average rating (convert star ratings to numbers)
            cursor.execute("SELECT rating FROM reviews WHERE status = 'Approved'")
            ratings = cursor.fetchall()
            
            total_rating = 0
            rating_count = 0
            for rating in ratings:
                if rating['rating']:
                    # Count stars in the rating
                    star_count = rating['rating'].count('⭐')
                    total_rating += star_count
                    rating_count += 1
            
            avg_rating = round(total_rating / rating_count, 1) if rating_count > 0 else 0.0
            
            # Get total packages
            cursor.execute("SELECT COUNT(*) as count FROM packages WHERE status = 'Active'")
            total_packages = cursor.fetchone()['count']
            
            # Get total customizations
            cursor.execute("SELECT COUNT(*) as count FROM customizations")
            total_customizations = cursor.fetchone()['count']
            
            # Get pending customizations
            cursor.execute("SELECT COUNT(*) as count FROM customizations WHERE status = 'New'")
            pending_customizations = cursor.fetchone()['count']
            
            # Get total users
            cursor.execute("SELECT COUNT(*) as count FROM users")
            total_users = cursor.fetchone()['count']
            
            return jsonify({
                'total_bookings': total_bookings,
                'pending_bookings': pending_bookings,
                'completed_bookings': completed_bookings,
                'avg_rating': avg_rating,
                'packages': total_packages,
                'customizations': total_customizations,
                'pending_customizations': pending_customizations,
                'total_users': total_users,
                'error': False
            })
            
        except mysql.connector.Error as err:
            return jsonify({'error': True, 'message': str(err)}), 500
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                conn.close()
    except Exception as e:
        logger.error(f"Error in dashboard_stats: {str(e)}")
        return jsonify({'error': True, 'message': 'Server error'}), 500
    
@app.route('/api/admin/check-auth')
def check_admin_auth():
    """Check if admin is authenticated"""
    try:
        if session.get('admin_logged_in'):
            return jsonify({'logged_in': True})
        return jsonify({'logged_in': False})
    except Exception as e:
        logger.error(f"Error in check_admin_auth: {str(e)}")
        return jsonify({'logged_in': False})

# ===== DATABASE FUNCTIONS =====
def create_database_and_tables():
    """Create database and tables if they don't exist - UPDATED to match your SQL schema"""
    try:
        # First connect without database to create it
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        cursor = conn.cursor()
        
        # Create database if it doesn't exist
        cursor.execute("CREATE DATABASE IF NOT EXISTS decora_events_final")
        cursor.execute("USE decora_events_final")
        
        # Create tables that match your SQL schema exactly
        tables_sql = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Admin table
            """
            CREATE TABLE IF NOT EXISTS admin (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Packages table
            """
            CREATE TABLE IF NOT EXISTS packages (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                category ENUM('Birthday','Wedding','Engagement','Baby Shower','Corporate','Themes') NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                description TEXT,
                status ENUM('Active','Inactive') DEFAULT 'Active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            
            # Bookings table
            """
            CREATE TABLE IF NOT EXISTS bookings (
                id INT AUTO_INCREMENT PRIMARY KEY,
                booking_id VARCHAR(20) NOT NULL UNIQUE,
                user_id INT,
                bookingname VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                event_type ENUM('Themed','Engagement','BabyShower','Seminar') NOT NULL,
                event_date DATE NOT NULL,
                event_time TIME NOT NULL,
                package_type ENUM('Basic','Moderate','Luxury') NOT NULL,
                theme VARCHAR(50),
                decoration_title VARCHAR(255),
                status ENUM('Pending','Confirmed','Completed','Cancelled') DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """,
            
            # Customizations table
            """
            CREATE TABLE IF NOT EXISTS customizations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                customization_id VARCHAR(20) NOT NULL UNIQUE,
                user_id INT,
                customName VARCHAR(100) NOT NULL,
                customEventType ENUM('Themed','Engagement','Baby Shower','Seminar','Other') NOT NULL,
                customDate DATE NOT NULL,
                customTime TIME NOT NULL,
                customDescription TEXT NOT NULL,
                status ENUM('New','In Progress','Completed') DEFAULT 'New',
                submitted_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """,
            
            # Reviews table
            """
            CREATE TABLE IF NOT EXISTS reviews (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                reviewname VARCHAR(100) NOT NULL,
                rating ENUM('⭐','⭐⭐','⭐⭐⭐','⭐⭐⭐⭐','⭐⭐⭐⭐⭐') NOT NULL,
                review TEXT NOT NULL,
                status ENUM('Pending','Approved') DEFAULT 'Pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
            )
            """
        ]
        
        for sql in tables_sql:
            try:
                cursor.execute(sql)
            except mysql.connector.Error as err:
                print(f"Note: Table might already exist: {err}")
        
        # Insert default admin user if not exists
        cursor.execute("SELECT COUNT(*) FROM admin")
        if cursor.fetchone()[0] == 0:
            cursor.execute(
                "INSERT INTO admin (username, password) VALUES (%s, %s)",
                ('admin', 'admin123')
            )
        
        # Insert sample packages if not exists
        cursor.execute("SELECT COUNT(*) FROM packages")
        if cursor.fetchone()[0] == 0:
            packages = [
                ('Basic Wedding', 'Wedding', 50000.00, 'Beautiful wedding decorations with flowers and lighting'),
                ('Luxury Birthday', 'Birthday', 15000.00, 'Fun and colorful birthday party decorations'),
                ('Corporate Event', 'Corporate', 30000.00, 'Professional corporate event setups'),
                ('Baby Shower', 'Baby Shower', 12000.00, 'Cute and adorable baby shower themes'),
                ('Anniversary', 'Wedding', 20000.00, 'Elegant anniversary celebration decorations'),
                ('Engagement Party', 'Engagement', 25000.00, 'Romantic engagement party setups')
            ]
            cursor.executemany(
                "INSERT INTO packages (name, category, price, description) VALUES (%s, %s, %s, %s)",
                packages
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Database and tables created successfully!")
        return True
        
    except mysql.connector.Error as err:
        print(f"❌ Error creating database: {err}")
        return False

def get_db_connection():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"❌ Database connection error: {err}")
        return None

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def check_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except:
        return False

# ===== MAIN EXECUTION =====
if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    print(f"📁 Serving frontend from: {FRONTEND_DIR}")
    print("🌐 Server will be available at: http://localhost:5000")
    print("🔧 Debug mode: ON")
    
    # Create database and tables if they don't exist
    create_database_and_tables()
    
    app.run(debug=True, host='0.0.0.0', port=5000)