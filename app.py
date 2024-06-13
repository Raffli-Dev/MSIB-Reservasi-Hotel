import requests
from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash, json
from pymongo import MongoClient
import os
from os.path import join, dirname
from dotenv import load_dotenv
import hashlib
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from bson.objectid import ObjectId
import base64
import logging
import locale
import json
import pytz
from bson.errors import InvalidId



locale.setlocale(locale.LC_ALL, '')


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = 'static/img/uploads/profile'
app.config['MAX_CONTENT_PATH'] = 1 * 1024 * 1024  # Max Upload 16mb
app.secret_key = 'supersecretkey'

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

#Konvigurasi .env
MONGODB_URI = os.environ.get("MONGODB_URI")
DB_NAME = os.environ.get("DB_NAME")
SECRET_KEY = os.environ.get("SECRET_KEY")
MIDTRANS_SERVER_KEY = os.environ.get("MIDTRANS_SERVER_KEY")

client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_user_info():
    if 'logged_in' in session:
        email = session['email']
        user_info = db.users.find_one({'email': email})
        return user_info
    return None

def get_admin_info():
    if 'logged_in' in session:
        email = session['email']
        admin_info = db.admin.find_one({'email': email})
        return admin_info
    return None

@app.route('/', methods=['GET'])
def home():
    return render_template('home/index.html')

@app.route('/rooms', methods=['GET'])
def rooms():
    return render_template('room/rooms.html')

@app.route('/rooms/deluxe', methods=['GET'])
def deluxe_room():
    return render_template('room/rooms.html')

@app.route('/rooms/deluxe_family', methods=['GET'])
def deluxe_family():
    return render_template('room/deluxe_family.html')

@app.route('/facilities', methods=['GET'])
def facilities():
    return render_template('facilities/facilities.html')

@app.route('/gallery', methods=['GET'])
def gallery():
    return render_template('gallery/gallery.html')

@app.route('/contact', methods=['GET'])
def contact():
    return render_template('contact/contact.html')

@app.route('/book', methods=['GET'])
def book():
    return render_template('book/book.html')

@app.route('/sign_in', methods=['POST'])
def sign_in():
    email = request.form.get('email')
    password = request.form.get('password')

    user = db.users.find_one({'email': email})

    if user:
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if user['password'] == hashed_password:
            session['logged_in'] = True
            session['email'] = email
            session['full_name'] = user['full_name']
            session['user_id'] = str(user['_id'])
            return jsonify({'result': 'success', 'msg': 'Login berhasil'})
    return jsonify({'result': 'fail', 'msg': 'Password Salah!!!'})

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        phone_number = request.form.get('phoneNumber')
        birth_date = request.form.get('birthDate')
        gender = request.form.get('gender')
        address = request.form.get('address')
        city = request.form.get('city')
        region = request.form.get('region')
        postal_code = request.form.get('postalCode')

        if not full_name or not email or not password or not confirm_password or not phone_number or not birth_date or not gender or not address or not city or not region or not postal_code:
            return jsonify({'error': 'Semua field yang diberi tanda * harus diisi.'}), 400

        if password != confirm_password:
            return jsonify({'error': 'Kata sandi dan konfirmasi kata sandi tidak cocok.'}), 400

        if db.users.find_one({'email': email}):
            return jsonify({'error': 'Email sudah digunakan.'}), 400

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        profile_picture_url = url_for('static', filename='img/uploads/profile/profile_placeholder.png')

        user_data = {
            'full_name': full_name,
            'email': email,
            'password': hashed_password,
            'phone_number': phone_number,
            'birth_date': birth_date,
            'gender': gender,
            'address': address,
            'city': city,
            'region': region,
            'postal_code': postal_code,
            'profile_picture_url': profile_picture_url
            
        }

        db.users.insert_one(user_data)
        return jsonify({'success': 'Pendaftaran berhasil!'}), 200

    return render_template('register/register.html')

@app.route("/login")
def login():
    msg = request.args.get("msg")
    return render_template("login/login.html", msg=msg)

@app.route("/user/index")
def user_index():
    user_info = get_user_info()
    if user_info:
        return render_template('user/home/index.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

# khusus user login yang bisa akses
@app.route('/user/rooms', methods=['GET'])
def user_rooms():
    user_info = get_user_info()
    if user_info:
        return render_template('user/room/rooms.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/user/rooms/deluxe', methods=['GET'])
def user_deluxe_room():
    user_info = get_user_info()
    if user_info:
        return render_template('user/room/deluxe.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/user/rooms/deluxe_family', methods=['GET'])
def user_deluxe_family():
    user_info = get_user_info()
    if user_info:
        return render_template('user/room/deluxe_family.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/user/facilities', methods=['GET'])
def user_facilities():
    user_info = get_user_info()
    if user_info:
        return render_template('user/facilities/facilities.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/user/gallery', methods=['GET'])
def user_gallery():
    user_info = get_user_info()
    if user_info:
        return render_template('user/gallery/gallery.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/user/contact', methods=['GET'])
def user_contact():
    user_info = get_user_info()
    if user_info:
        return render_template('user/contact/contact.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/user/profile', methods=['GET'])
def user_profile():
    user_info = get_user_info()
    if user_info:
        email = user_info.get('email')
        reviews = list(db.reviews.find({'email': email}))
        return render_template('user/profile/profile.html', user_info=user_info, reviews=reviews)
    else:
        return redirect(url_for('login'))
    
@app.route('/delete_review/<review_id>', methods=['DELETE'])
def delete_review(review_id):
    email = session.get('email')
    if email:
        result = db.reviews.delete_one({'_id': ObjectId(review_id), 'email': email})
        if result.deleted_count:
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False}), 404
    else:
        return jsonify({'success': False}), 403

@app.route('/user/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    if 'logged_in' in session:
        email = session['email']
        user_info = db.users.find_one({'email': email})

        if request.method == 'POST':
            full_name = request.form.get('fullName')
            phone_number = request.form.get('phoneNumber')
            birth_date = request.form.get('birthDate')
            gender = request.form.get('gender')
            address = request.form.get('address')
            city = request.form.get('city')
            region = request.form.get('region')
            postal_code = request.form.get('postalCode')

            db.users.update_one(
                {'email': email},
                {'$set': {
                    'full_name': full_name,
                    'phone_number': phone_number,
                    'birth_date': birth_date,
                    'gender': gender,
                    'address': address,
                    'city': city,
                    'region': region,
                    'postal_code': postal_code
                }}
            )
            return redirect(url_for('user_profile'))
        
        return render_template('user/profile/edit_profile.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/user/profile/upload_photo', methods=['POST'])
def upload_photo():
    if 'logged_in' in session:
        email = session['email']
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture:
                filename = secure_filename(profile_picture.filename)
                profile_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_picture.save(profile_picture_path)
                
                profile_picture_url = url_for('static', filename='img/uploads/profile/' + filename)
                db.users.update_one(
                    {'email': email},
                    {'$set': {'profile_picture_url': profile_picture_url}}
                )
        return redirect(url_for('user_profile'))
    else:
        return redirect(url_for('login'))


def format_currency(value):
    return locale.format_string("%d", value, grouping=True)

# Timezone for Indonesia (Jakarta)
wib = pytz.timezone('Asia/Jakarta')


from datetime import datetime

@app.route('/user/reservasi', methods=['GET'])
def user_reservasi():
    if 'logged_in' in session:
        email = session['email']
        user_info = db.users.find_one({'email': email})
        
        # Fetch bookings from both collections
        deluxe_bookings = list(db.deluxe_booking.find({'email': email}).sort('created_at', -1))
        family_deluxe_bookings = list(db.family_deluxe_booking.find({'email': email}).sort('created_at', -1))
        
        # Combine bookings
        all_bookings = deluxe_bookings + family_deluxe_bookings

        now = datetime.now()

        for booking in all_bookings:
            # Convert string dates from the database to datetime objects
            check_in_date_str = booking.get('check_in_date', '')
            check_out_date_str = booking.get('check_out_date', '')
            
            try:
                check_in_date = datetime.strptime(check_in_date_str, '%d/%m/%Y')
                check_out_date = datetime.strptime(check_out_date_str, '%d/%m/%Y')
                
                # Convert dates to strings for the template to use
                booking['check_in_date'] = check_in_date.strftime('%d/%m/%Y')
                booking['check_out_date'] = check_out_date.strftime('%d/%m/%Y')

                # Check if current time is after check-out date
                booking['can_review'] = now > check_out_date
            except ValueError:
                booking['check_in_date'] = check_in_date_str
                booking['check_out_date'] = check_out_date_str
                booking['can_review'] = False

            review_exists = db.reviews.find_one({'booking_id': str(booking['_id']), 'email': email}) is not None
            booking['review_exists'] = review_exists

            # Debugging output
            print(f"Booking ID: {booking['_id']}, Can Review: {booking['can_review']}, Review Exists: {booking['review_exists']}, Status: {booking['status']}, Check-out Date: {booking['check_out_date']}, Now: {now}")

        return render_template('user/reservasi/reservasi.html', user_info=user_info, user_bookings=all_bookings, format_currency=format_currency)
    else:
        return redirect(url_for('login'))
        
@app.route('/give_review/<booking_id>', methods=['GET', 'POST'])
def give_review(booking_id):
    if 'logged_in' in session:
        email = session.get('email')
        if not email:
            flash('Anda harus login untuk memberikan ulasan', 'danger')
            return redirect(url_for('login'))

        user_info = db.users.find_one({'email': email})

        # Check booking in deluxe_booking collection
        booking = db.deluxe_booking.find_one({'_id': ObjectId(booking_id)})
        room_type = 'Deluxe'

        # If not found, check in family_deluxe_booking collection
        if not booking:
            booking = db.family_deluxe_booking.find_one({'_id': ObjectId(booking_id)})
            room_type = 'Family Deluxe'

        if not booking:
            flash('Booking tidak ditemukan', 'danger')
            return redirect(url_for('user_reservasi'))

        # Check if review already exists for this booking
        review_exists = db.reviews.find_one({'booking_id': booking_id, 'email': email})
        if review_exists:
            flash('Anda sudah menulis ulasan untuk booking ini', 'danger')
            return redirect(url_for('user_reservasi'))

        if request.method == 'POST':
            rating = int(request.form.get('rating'))
            review = request.form.get('review')

            db.reviews.insert_one({
                'booking_id': booking_id,
                'email': email,
                'rating': rating,
                'review': review,
                'tipe_kamar': room_type,
                'created_at': datetime.now(wib)
            })

            flash('Ulasan berhasil disimpan', 'success')
            return redirect(url_for('user_reservasi'))

        return render_template('user/reservasi/give_review.html', user_info=user_info, booking=booking)
    else:
        return redirect(url_for('login_user'))

@app.route('/user/book', methods=['GET'])
def user_book():
    user_info = get_user_info()
    check_in_date = request.args.get('check_in_date')
    
    if not check_in_date:
        check_in_date = datetime.today().strftime('%d/%m/%Y')
    else:
        check_in_date = datetime.strptime(check_in_date, '%Y-%m-%d').strftime('%d/%m/%Y')
    
    # Convert the date back to 'dd/mm/yyyy' for the database query
    query_date = datetime.strptime(check_in_date, '%d/%m/%Y').strftime('%d/%m/%Y')

    deluxe_room = db.room_prices.find_one({"date": query_date, "room_type": "Deluxe"})
    deluxe_family_room = db.room_prices.find_one({"date": query_date, "room_type": "Family Deluxe"})
    
    return render_template('user/book/book.html', user_info=user_info, deluxe_room=deluxe_room, deluxe_family_room=deluxe_family_room, format_currency=format_currency)

@app.route('/user/room/booking/deluxe-room', methods=['GET', 'POST'])
def user_deluxe_book():
    user_info = get_user_info()
    
    check_in_date_str = request.args.get('check_in_date', datetime.today().strftime('%Y-%m-%d'))
    check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d')
    
    harga_normal = float(request.args.get('harga_normal', '0'))
    harga_diskon = float(request.args.get('harga_diskon', '0'))
    
    lama_inap = int(request.args.get('lamaInap', '1'))
    
    check_out_date = check_in_date + timedelta(days=lama_inap)
    
    check_in_date_display_str = check_in_date.strftime('%d/%m/%Y')
    check_out_date_display_str = check_out_date.strftime('%d/%m/%Y')

    if user_info:
        return render_template(
            'user/book/deluxe_book.html', 
            user_info=user_info, 
            check_in_date_display=check_in_date_display_str,  
            check_in_date=check_in_date_str,  
            check_out_date=check_out_date_display_str,
            harga_normal=harga_normal, 
            harga_diskon=harga_diskon, 
            lama_inap=lama_inap,
            format_currency=lambda x: 'Rp {:,.0f}'.format(x).replace(',', '.')
        )
    else:
        return redirect(url_for('login'))

@app.route('/deluxe_save_booking', methods=['POST'])
def deluxe_save_booking():
    if request.method == 'POST':
        data = request.get_json()

        booking_code = data.get('bookingCode')
        nama_lengkap = data.get('namaLengkap')
        email = data.get('email')
        nomor_handphone = data.get('nomorHandphone')
        pesanan_untuk = data.get('pesananUntuk')
        guest_name = data.get('guestName')  # Pastikan ini diambil dari data yang dikirim
        lama_inap = data.get('lamaInap')
        permintaan_khusus = data.get('permintaanKhusus')
        harga_normal = data.get('hargaNormal')
        harga_diskon = data.get('hargaDiskon')
        harga_total = data.get('hargaTotal')
        check_in_date = data.get('checkInDate')
        check_out_date = data.get('checkOutDate')
        created_at = datetime.now(wib)
        updated_at = datetime.now(wib)

        try:
            lama_inap = int(lama_inap)
        except ValueError:
            return jsonify({'error': 'Lama inap harus berupa angka.'}), 400

        booking_data = {
            'booking_code': booking_code,
            'tipe_kamar' : 'Deluxe',
            'nama_lengkap': nama_lengkap,
            'email': email,
            'nomor_handphone': nomor_handphone,
            'pesanan_untuk': pesanan_untuk,
            'guest_name': guest_name,  # Simpan guest_name ke database
            'lama_inap': lama_inap,
            'permintaan_khusus': permintaan_khusus,
            'harga_normal': harga_normal,
            'harga_diskon': harga_diskon,
            'harga_total': harga_total,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'created_at': created_at,
            'updated_at': updated_at,
            'status': 'menunggu pembayaran'
        }

        db.deluxe_booking.insert_one(booking_data)

        return jsonify({'success': 'Booking berhasil disimpan!'}), 200

    return jsonify({'error': 'Metode tidak valid.'}), 400

@app.template_filter('tojson')
def tojson_filter(value):
    def convert(o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime):
            return o.isoformat()
        return json.JSONEncoder().default(o)
    return json.dumps(value, default=convert)

@app.route('/payment_token/<booking_code>', methods=['GET'])
def payment_token(booking_code):
    logger.info(f'Received payment token request for booking_code: {booking_code}')
    booking = db.deluxe_booking.find_one({'booking_code': booking_code}) or db.family_deluxe_booking.find_one({'booking_code': booking_code})
    if booking:
        # Prepare item details based on booking data
        item_details = [
            {
                'id': booking_code,
                'price': booking['harga_total'],
                'quantity': 1,
                'name': f"Kamar {booking['tipe_kamar']}: {booking['lama_inap']} malam"
            }
        ]

        transaction_details = {
            'order_id': booking_code,
            'gross_amount': booking['harga_total']
        }
        customer_details = {
            'first_name': booking['nama_lengkap'],
            'email': booking['email'],
            'phone': booking['nomor_handphone']
        }
        payload = {
            'transaction_details': transaction_details,
            'customer_details': customer_details,
            'item_details': item_details  # Include item details in the payload
        }
        headers = {
            'Authorization': 'Basic ' + base64.b64encode((MIDTRANS_SERVER_KEY + ':').encode()).decode(),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        response = requests.post('https://app.sandbox.midtrans.com/snap/v1/transactions', headers=headers, json=payload)
        response_data = response.json()
        logger.info(f'Response from Midtrans: {response_data}')
        if 'token' in response_data:
            return jsonify({'token': response_data['token']})
        else:
            logger.error(f'Error from Midtrans: {response_data}')
            return jsonify({'error': response_data}), 500
    logger.error(f'Booking not found for booking_code: {booking_code}')
    return jsonify({'error': 'Booking not found'}), 404

@app.route('/payment_callback', methods=['POST'])
def payment_callback():
    data = request.json
    order_id = data['order_id']
    transaction_status = data['transaction_status']
    fraud_status = data['fraud_status']
    
    logger.info(f'Payment callback received for order_id: {order_id} with status: {transaction_status} and fraud status: {fraud_status}')
    
    booking = db.deluxe_booking.find_one({'booking_code': order_id}) or db.family_deluxe_booking.find_one({'booking_code': order_id})

    if booking:
        booking_collection = db.deluxe_booking if db.deluxe_booking.find_one({'booking_code': order_id}) else db.family_deluxe_booking
        if transaction_status == 'capture':
            if fraud_status == 'accept':
                booking_collection.update_one({'booking_code': order_id}, {'$set': {'status': 'menunggu konfirmasi'}})
                return jsonify({'result': 'success'})
        elif transaction_status in ['settlement', 'pending']:
            booking_collection.update_one({'booking_code': order_id}, {'$set': {'status': 'menunggu konfirmasi'}})
            return jsonify({'result': 'success'})
        elif transaction_status in ['deny', 'expire', 'cancel']:
            booking_collection.update_one({'booking_code': order_id}, {'$set': {'status': 'dibatalkan'}})
            return jsonify({'result': 'success'})
    return jsonify({'result': 'error'})

@app.route('/update_booking_status', methods=['POST'])
def update_booking_status():
    data = request.json
    if not data or 'booking_code' not in data or 'new_status' not in data:
        logger.error('Invalid request data')
        return jsonify({'result': 'error', 'message': 'Invalid request data'}), 400

    booking_code = data['booking_code']
    new_status = data['new_status']
    
    logger.info(f'Received request to update booking status for booking_code: {booking_code} to {new_status}')
    
    booking = db.deluxe_booking.find_one({'booking_code': booking_code}) or db.family_deluxe_booking.find_one({'booking_code': booking_code})
    if not booking:
        logger.error('Booking not found')
        return jsonify({'result': 'error', 'message': 'Booking not found'}), 404
    
    # Update booking status
    booking_collection = db.deluxe_booking if db.deluxe_booking.find_one({'booking_code': booking_code}) else db.family_deluxe_booking
    result = booking_collection.update_one({'booking_code': booking_code}, {'$set': {'status': new_status}})
    if result.modified_count > 0:
        # Update room stock
        try:
            check_in_date = datetime.strptime(booking['check_in_date'], '%d/%m/%Y')
            logger.info(f'Parsed check-in date: {check_in_date}')
        except ValueError:
            logger.error('Invalid date format in booking')
            return jsonify({'result': 'error', 'message': 'Invalid date format in booking'}), 400

        room_type = booking.get('tipe_kamar')
        if not room_type:
            logger.error('Room type not found in booking')
            return jsonify({'result': 'error', 'message': 'Room type not found in booking'}), 400

        # Log room type and check-in date
        logger.info(f'Room type: {room_type}, Check-in date: {check_in_date.strftime("%d/%m/%Y")}')

        # Ensure the room type matches the naming in room_prices
        if room_type == 'Deluxe Family':
            logger.info('Room type Deluxe Family detected')
            room_type = 'Family Deluxe'

        logger.info(f'Updating stock for room type: {room_type} on date: {check_in_date.strftime("%d/%m/%Y")}')
        
        # Check if the document exists in room_prices
        room_price_doc = db.room_prices.find_one({'date': check_in_date.strftime('%d/%m/%Y'), 'room_type': room_type})
        
        if room_price_doc:
            logger.info('Room price document found, updating stock')
            # If the document exists, update the stock
            update_result = db.room_prices.update_one(
                {'date': check_in_date.strftime('%d/%m/%Y'), 'room_type': room_type},
                {'$inc': {'stock': -1}}
            )
            logger.info(f'Update result: {update_result.modified_count}')
            if update_result.modified_count > 0:
                logger.info('Room stock updated successfully')
                return jsonify({'result': 'success'})
            else:
                logger.error('Failed to update room stock')
                return jsonify({'result': 'error', 'message': 'Failed to update room stock'}), 500
        else:
            logger.error('Room stock document not found for the specified date and room type')
            return jsonify({'result': 'error', 'message': 'Room stock document not found for the specified date and room type'}), 404
    else:
        logger.error('Failed to update booking status')
        return jsonify({'result': 'error', 'message': 'Failed to update booking status'}), 500

@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    booking_id = request.form.get('booking_id')
    logger.info(f'Cancel booking request received for booking_id: {booking_id}')
    if booking_id:
        result_deluxe = db.deluxe_booking.update_one({'_id': ObjectId(booking_id)}, {'$set': {'status': 'dibatalkan'}})
        result_family = db.family_deluxe_booking.update_one({'_id': ObjectId(booking_id)}, {'$set': {'status': 'dibatalkan'}})
        
        if result_deluxe.modified_count > 0 or result_family.modified_count > 0:
            logger.info(f'Booking cancelled successfully for booking_id: {booking_id}')
            return jsonify({'result': 'success', 'msg': 'Booking berhasil dibatalkan.'})
        else:
            logger.error(f'Failed to cancel booking for booking_id: {booking_id}')
            return jsonify({'result': 'error', 'msg': 'Gagal membatalkan booking.'})
    logger.error(f'Invalid booking_id: {booking_id}')
    return jsonify({'result': 'error', 'msg': 'ID booking tidak valid.'})

#route ini menangani ketika terjadi kesalahan dalam pembayaran midtrans maka akan dibatalkan otomatis oleh sistem
@app.route('/booking_dibatalkan', methods=['POST'])
def booking_dibatalkan():
    booking_id = request.form.get('booking_id')
    logger.info(f'Cancel booking request received for booking_id: {booking_id}')
    
    try:
        object_id = ObjectId(booking_id)
        result_deluxe = db.deluxe_booking.update_one({'_id': object_id}, {'$set': {'status': 'dibatalkan'}})
        result_family = db.family_deluxe_booking.update_one({'_id': object_id}, {'$set': {'status': 'dibatalkan'}})
    except InvalidId:
        result_deluxe = db.deluxe_booking.update_one({'booking_code': booking_id}, {'$set': {'status': 'dibatalkan'}})
        result_family = db.family_deluxe_booking.update_one({'booking_code': booking_id}, {'$set': {'status': 'dibatalkan'}})

    if result_deluxe.modified_count > 0 or result_family.modified_count > 0:
        logger.info(f'Booking cancelled successfully for booking_id: {booking_id}')
        return jsonify({'result': 'success', 'msg': 'Booking berhasil dibatalkan.'})
    else:
        logger.error(f'Failed to cancel booking for booking_id: {booking_id}')
        return jsonify({'result': 'error', 'msg': 'Gagal membatalkan booking.'})


@app.route('/user/room/booking/deluxe-room/order-place', methods=['GET', 'POST'])
def order_place():
    user_info = get_user_info()
    if user_info:
        return render_template('user/book/order_place.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/user/room/booking/deluxe-room/payment-success', methods=['GET', 'POST'])
def order_success():
    user_info = get_user_info()
    if user_info:
        return render_template('user/book/order_success.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/user/room/booking/family-deluxe-room', methods=['GET', 'POST'])
def user_family_deluxe_book():
    user_info = get_user_info()
    
    check_in_date_str = request.args.get('check_in_date', datetime.today().strftime('%Y-%m-%d'))
    check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d')
    
    harga_normal = float(request.args.get('harga_normal', '0'))
    harga_diskon = float(request.args.get('harga_diskon', '0'))
    
    lama_inap = int(request.args.get('lamaInap', '1'))
    
    check_out_date = check_in_date + timedelta(days=lama_inap)
    
    check_in_date_display_str = check_in_date.strftime('%d/%m/%Y')
    check_out_date_display_str = check_out_date.strftime('%d/%m/%Y')

    if user_info:
        return render_template(
            'user/book/family_deluxe_book.html', 
            user_info=user_info, 
            check_in_date_display=check_in_date_display_str,  
            check_in_date=check_in_date_str,  
            check_out_date=check_out_date_display_str,
            harga_normal=harga_normal, 
            harga_diskon=harga_diskon, 
            lama_inap=lama_inap,
            format_currency=lambda x: 'Rp {:,.0f}'.format(x).replace(',', '.')
        )
    else:
        return redirect(url_for('login'))

@app.route('/family_deluxe_save_booking', methods=['POST'])
def family_deluxe_save_booking():
    if request.method == 'POST':
        data = request.get_json()

        booking_code = data.get('bookingCode')
        nama_lengkap = data.get('namaLengkap')
        email = data.get('email')
        nomor_handphone = data.get('nomorHandphone')
        pesanan_untuk = data.get('pesananUntuk')
        guest_name = data.get('guestName')
        lama_inap = data.get('lamaInap')
        permintaan_khusus = data.get('permintaanKhusus')
        harga_normal = data.get('hargaNormal')
        harga_diskon = data.get('hargaDiskon')
        harga_total = data.get('hargaTotal')
        check_in_date = data.get('checkInDate')
        check_out_date = data.get('checkOutDate')
        created_at = datetime.now(wib)
        updated_at = datetime.now(wib)

        try:
            lama_inap = int(lama_inap)
        except ValueError:
            return jsonify({'error': 'Lama inap harus berupa angka.'}), 400

        booking_data = {
            'booking_code': booking_code,
            'tipe_kamar' : 'Family Deluxe',
            'nama_lengkap': nama_lengkap,
            'email': email,
            'nomor_handphone': nomor_handphone,
            'pesanan_untuk': pesanan_untuk,
            'guest_name': guest_name,
            'lama_inap': lama_inap,
            'permintaan_khusus': permintaan_khusus,
            'harga_normal': harga_normal,
            'harga_diskon': harga_diskon,
            'harga_total': harga_total,
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'created_at': created_at,
            'updated_at': updated_at,
            'status': 'menunggu pembayaran'
        }

        db.family_deluxe_booking.insert_one(booking_data)

        return jsonify({'success': 'Booking berhasil disimpan!'}), 200

    return jsonify({'error': 'Metode tidak valid.'}), 400

@app.route('/user/room/booking/family-deluxe-room/order-place', methods=['GET', 'POST'])
def family_order_place():
    user_info = get_user_info()
    if user_info:
        return render_template('user/book/order_place.html', user_info=user_info)
    else:
        return redirect(url_for('login'))

@app.route('/user/room/booking/family-deluxe-room/payment-success', methods=['GET', 'POST'])
def family_order_success():
    user_info = get_user_info()
    if user_info:
        return render_template('user/book/order_success.html', user_info=user_info)
    else:
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

# Route admin
@app.route("/admin/login")
def login_admin():
    msg = request.args.get("msg")
    return render_template("admin/login/login.html", msg=msg)

@app.route('/admin/sign_in', methods=['POST'])
def admin_login():
    email = request.form.get('email')
    password = request.form.get('password')

    admin = db.admin.find_one({'email': email})

    if admin:
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        if admin['password'] == hashed_password:
            session['logged_in'] = True
            session['email'] = email
            session['full_name'] = admin['full_name']
    
            return jsonify({'result': 'success', 'msg': 'Login berhasil'})
    return jsonify({'result': 'fail', 'msg': 'Password Salah!!!'})

@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        full_name = request.form.get('fullName')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirmPassword')
        role = request.form.get('role')

        if not full_name or not email or not password or not confirm_password:
            return jsonify({'error': 'Semua field yang diberi tanda * harus diisi.'}), 400

        if password != confirm_password:
            return jsonify({'error': 'Kata sandi dan konfirmasi kata sandi tidak cocok.'}), 400

        if db.users.find_one({'email': email}):
            return jsonify({'error': 'Email sudah digunakan.'}), 400

        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        profile_picture_url = url_for('static', filename='img/uploads/profile/profile_placeholder.png')

        user_data = {
            'full_name': full_name,
            'email': email,
            'password': hashed_password,
            'role': role,
            'profile_picture_url': profile_picture_url
            
        }
        db.admin.insert_one(user_data)
        return jsonify({'success': 'Pendaftaran berhasil!'}), 200

    return render_template('admin/register/register.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    session.pop('admin_email', None)
    session.pop('admin_full_name', None)
    return redirect(url_for('login_admin'))

def number_format(value):
    return "{:,.0f}".format(value)

# Register the filter in the Jinja environment
app.jinja_env.filters['number_format'] = number_format

@app.route('/admin/dashboard')
def admin_dashboard():
    admin_info = get_admin_info()
    if admin_info:
        # Mengambil data dari database
        # Data dari tabel deluxe_booking
        revenue_deluxe = sum(booking['harga_total'] for booking in db.deluxe_booking.find({'$or': [{'status': 'pesanan diterima'}, {'status': 'menunggu konfirmasi'}]}))
        total_guests_deluxe = db.deluxe_booking.count_documents({'status': 'pesanan diterima'})
        pending_payments_deluxe = db.deluxe_booking.count_documents({'status': 'menunggu pembayaran'})
        pending_confirmations_deluxe = db.deluxe_booking.count_documents({'status': 'menunggu konfirmasi'})
        accepted_bookings_deluxe = db.deluxe_booking.count_documents({'status': 'pesanan diterima'})
        rejected_bookings_deluxe = db.deluxe_booking.count_documents({'status': 'pesanan ditolak'})
        cancelled_bookings_deluxe = db.deluxe_booking.count_documents({'status': 'dibatalkan'})

        # Data dari tabel family_deluxe_booking
        revenue_family_deluxe = sum(booking['harga_total'] for booking in db.family_deluxe_booking.find({'$or': [{'status': 'pesanan diterima'}, {'status': 'menunggu konfirmasi'}]}))
        total_guests_family_deluxe = db.family_deluxe_booking.count_documents({'status': 'pesanan diterima'})
        pending_payments_family_deluxe = db.family_deluxe_booking.count_documents({'status': 'menunggu pembayaran'})
        pending_confirmations_family_deluxe = db.family_deluxe_booking.count_documents({'status': 'menunggu konfirmasi'})
        accepted_bookings_family_deluxe = db.family_deluxe_booking.count_documents({'status': 'pesanan diterima'})
        rejected_bookings_family_deluxe = db.family_deluxe_booking.count_documents({'status': 'pesanan ditolak'})
        cancelled_bookings_family_deluxe = db.family_deluxe_booking.count_documents({'status': 'dibatalkan'})

        # Menghitung pendapatan bulanan
        monthly_revenue = []
        for month in range(1, 13):
            start_date = datetime(2024, month, 1)
            if month == 12:
                end_date = datetime(2025, 1, 1)
            else:
                end_date = datetime(2024, month + 1, 1)
            monthly_sum = sum(booking['harga_total'] for booking in db.deluxe_booking.find({
                'status': 'pesanan diterima',
                'created_at': {
                    '$gte': start_date,
                    '$lt': end_date
                }
            }))
            monthly_revenue.append(monthly_sum)

        data = {
            'revenue': revenue_deluxe,
            'total_guests': total_guests_deluxe,
            'pending_payments': pending_payments_deluxe,
            'pending_confirmations': pending_confirmations_deluxe,
            'accepted_bookings': accepted_bookings_deluxe,
            'rejected_bookings': rejected_bookings_deluxe,
            'cancelled_bookings': cancelled_bookings_deluxe,
            'monthly_revenue': monthly_revenue,

            # Data dari tabel family_deluxe_booking
            'revenue_family_deluxe': revenue_family_deluxe,
            'total_guests_family_deluxe': total_guests_family_deluxe,
            'pending_payments_family_deluxe': pending_payments_family_deluxe,
            'pending_confirmations_family_deluxe': pending_confirmations_family_deluxe,
            'accepted_bookings_family_deluxe': accepted_bookings_family_deluxe,
            'rejected_bookings_family_deluxe': rejected_bookings_family_deluxe,
            'cancelled_bookings_family_deluxe': cancelled_bookings_family_deluxe
        }
        
        return render_template('admin/dashboard/dashboard.html', admin_info=admin_info, data=data)
    else:
        return redirect(url_for('login_admin'))
    
    
@app.route('/admin/profile', methods=['GET'])
def admin_profile():
    admin_info = get_admin_info()
    if admin_info:
        return render_template('admin/profile/profile.html', admin_info=admin_info)
    else:
        return redirect(url_for('login_admin'))

@app.route('/admin/profile/edit', methods=['GET', 'POST'])
def admin_edit_profile():
    if 'logged_in' in session:
        email = session['email']
        admin_info = db.admin.find_one({'email': email})

        if request.method == 'POST':
            full_name = request.form.get('fullName')
            phone_number = request.form.get('phoneNumber')
            birth_date = request.form.get('birthDate')
            gender = request.form.get('gender')
            address = request.form.get('address')
            city = request.form.get('city')
            region = request.form.get('region')
            postal_code = request.form.get('postalCode')

            db.admin.update_one(
                {'email': email},
                {'$set': {
                    'full_name': full_name,
                    'phone_number': phone_number,
                    'birth_date': birth_date,
                    'gender': gender,
                    'address': address,
                    'city': city,
                    'region': region,
                    'postal_code': postal_code
                }}
            )
            return redirect(url_for('admin_profile'))
        
        return render_template('admin/profile/edit_profile.html', admin_info=admin_info)
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/profile/upload_photo', methods=['POST'])
def admin_upload_photo():
    if 'logged_in' in session:
        email = session['email']
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture:
                filename = secure_filename(profile_picture.filename)
                profile_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_picture.save(profile_picture_path)
                
                profile_picture_url = url_for('static', filename='img/uploads/profile/' + filename)
                db.admin.update_one(
                    {'email': email},
                    {'$set': {'profile_picture_url': profile_picture_url}}
                )
        return redirect(url_for('admin_profile'))
    else:
        return redirect(url_for('admin_login'))

@app.route('/admin/user', methods=['GET'])
def admin_user():
    admin_info = get_admin_info()
    if admin_info:
        search_query = request.args.get('search')
        per_page = 5
        page = int(request.args.get('page', 1))
        
        if search_query:
            users = list(db.users.find({'email': {'$regex': search_query, '$options': 'i'}}).skip((page - 1) * per_page).limit(per_page))
            total_users = db.users.count_documents({'email': {'$regex': search_query, '$options': 'i'}})
        else:
            users = list(db.users.find().skip((page - 1) * per_page).limit(per_page))
            total_users = db.users.count_documents({})
        
        total_pages = (total_users + per_page - 1) // per_page
        return render_template('admin/user/user.html', users=users, admin_info=admin_info, page=page, total_pages=total_pages, total_users=total_users)
    else:
        return redirect(url_for('login_admin'))

@app.route('/admin/delete_user', methods=['POST'])
def admin_delete_user():
    user_id = request.form.get('user_id')
    if user_id:
        result = db.users.delete_one({'_id': ObjectId(user_id)})
        if result.deleted_count > 0:
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'error', 'msg': 'Gagal menghapus pengguna.'})
    return jsonify({'result': 'error', 'msg': 'ID pengguna tidak valid.'})

@app.route('/admin/bulk_delete_users', methods=['POST'])
def admin_bulk_delete_users():
    user_ids = request.form.getlist('user_ids[]')
    if user_ids:
        object_ids = [ObjectId(user_id) for user_id in user_ids]
        result = db.users.delete_many({'_id': {'$in': object_ids}})
        if result.deleted_count > 0:
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'error', 'msg': 'Gagal menghapus pengguna.'})
    return jsonify({'result': 'error', 'msg': 'Tidak ada ID pengguna yang valid.'})

@app.route('/admin/user/profile/<user_id>', methods=['GET', 'POST'])
def admin_edit_user_profile(user_id):
    if 'logged_in' in session:
        admin_info = get_admin_info()
        if admin_info:
            user_info = db.users.find_one({'_id': ObjectId(user_id)})

            if request.method == 'POST':
                full_name = request.form.get('fullName')
                phone_number = request.form.get('phoneNumber')
                birth_date = request.form.get('birthDate')
                gender = request.form.get('gender')
                address = request.form.get('address')
                city = request.form.get('city')
                region = request.form.get('region')
                postal_code = request.form.get('postalCode')

                db.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': {
                        'full_name': full_name,
                        'phone_number': phone_number,
                        'birth_date': birth_date,
                        'gender': gender,
                        'address': address,
                        'city': city,
                        'region': region,
                        'postal_code': postal_code
                    }}
                )
                return redirect(url_for('admin_edit_user_profile', user_id=user_id))

            return render_template('admin/user/edit_user_profile.html', admin_info=admin_info, user_info=user_info)
        else:
            return redirect('/admin/login')
    else:
        return redirect('/admin/login')

@app.route('/admin/user/profile/<user_id>/upload_photo', methods=['POST'])
def admin_upload_user_photo(user_id):
    if 'logged_in' in session:
        admin_info = get_admin_info()
        if admin_info and 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture:
                filename = secure_filename(profile_picture.filename)
                profile_picture_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                profile_picture.save(profile_picture_path)
                
                profile_picture_url = url_for('static', filename='img/uploads/profile/' + filename)
                db.users.update_one(
                    {'_id': ObjectId(user_id)},
                    {'$set': {'profile_picture_url': profile_picture_url}}
                )
        return redirect(url_for('admin_edit_user_profile', user_id=user_id))
    else:
        return redirect(url_for('login_admin'))

def to_date_input_format(value):
    return datetime.strptime(value, '%d/%m/%Y').strftime('%Y-%m-%d')

app.jinja_env.filters['to_date_input_format'] = to_date_input_format

@app.route('/admin/room/edit/<room_id>', methods=['GET', 'POST'])
def admin_edit_room(room_id):
    if 'logged_in' in session:
        admin_info = get_admin_info()
        room = db.room_prices.find_one({'_id': ObjectId(room_id)})

        if request.method == 'POST':
            room_type = request.form.get('roomType')
            date = request.form.get('date')
            normal_price = request.form.get('price')
            discount_price = request.form.get('discount_price')
            stock = request.form.get('stock')

            # Convert stock to integer
            try:
                stock = int(stock)
            except ValueError:
                return jsonify({'error': 'Stock harus berupa angka.'}), 400

            # Convert prices to integer
            try:
                normal_price = int(normal_price)
                discount_price = int(discount_price)
            except ValueError:
                return jsonify({'error': 'Harga harus berupa angka.'}), 400

            # Convert date to datetime object and format it as DD/MM/YYYY
            try:
                date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
            except ValueError:
                return jsonify({'error': 'Format tanggal salah.'}), 400

            db.room_prices.update_one(
                {'_id': ObjectId(room_id)},
                {'$set': {
                    'room_type': room_type,
                    'date': date,
                    'price': normal_price,
                    'discount_price': discount_price,
                    'stock': stock,
                    'updated_at': datetime.now(wib),
                }}
            )
            return redirect(url_for('admin_room'))

        # Ensure room_type is passed correctly to the template
        return render_template('admin/room/edit_room.html', admin_info=admin_info, room=room)
    else:
        return redirect(url_for('login_admin'))

@app.route('/admin/room/delete', methods=['POST'])
def admin_delete_room():
    room_id = request.form.get('room_id')
    if room_id:
        result = db.room_prices.delete_one({'_id': ObjectId(room_id)})
        if result.deleted_count > 0:
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'error', 'msg': 'Gagal menghapus kamar.'})
    return jsonify({'result': 'error', 'msg': 'ID kamar tidak valid.'})

@app.route('/admin/bulk_delete_rooms', methods=['POST'])
def admin_bulk_delete_rooms():
    room_ids = request.form.getlist('room_ids[]')
    if room_ids:
        object_ids = [ObjectId(room_id) for room_id in room_ids]
        result = db.room_prices.delete_many({'_id': {'$in': object_ids}})
        if result.deleted_count > 0:
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'error', 'msg': 'Gagal menghapus kamar.'})
    return jsonify({'result': 'error', 'msg': 'Tidak ada ID kamar yang valid.'})

@app.route('/admin/rooms', methods=['GET'])
def admin_room():
    admin_info = get_admin_info()
    if admin_info:
        search_query = request.args.get('search')
        room_type_filter = request.args.get('room_type')
        date_filter = request.args.get('date')
        per_page = 5
        page = int(request.args.get('page', 1))

        query = {}
        if search_query:
            query['type'] = {'$regex': search_query, '$options': 'i'}
        if room_type_filter:
            query['type'] = room_type_filter
        if date_filter:
            # Convert date to dd/mm/yyyy
            date_parts = date_filter.split('-')
            formatted_date = f"{date_parts[2]}/{date_parts[1]}/{date_parts[0]}"
            query['date'] = formatted_date

        rooms = list(db.room_prices.find(query)
                     .sort('created_at', -1)
                     .skip((page - 1) * per_page)
                     .limit(per_page))
        total_rooms = db.room_prices.count_documents(query)

        total_pages = (total_rooms + per_page - 1) // per_page
        return render_template('admin/room/room.html', rooms=rooms, admin_info=admin_info, page=page, total_pages=total_pages, total_rooms=total_rooms, format_currency=format_currency)
    else:
        return redirect(url_for('login_admin'))

@app.route('/admin/room/add', methods=['GET', 'POST'])
def admin_add_room():
    if 'logged_in' in session:
        admin_info = get_admin_info()
        
        if request.method == 'POST':
            room_type = request.form.get('roomType')
            date = request.form.get('date')
            normal_price = request.form.get('price')
            discount_price = request.form.get('discount_price')
            stock = request.form.get('stock')

            # Convert stock to integer
            try:
                stock = int(stock)
            except ValueError:
                return jsonify({'error': 'Stock harus berupa angka.'}), 400

            # Convert prices to integer
            try:
                normal_price = int(normal_price)
                discount_price = int(discount_price)
            except ValueError:
                return jsonify({'error': 'Harga harus berupa angka.'}), 400

            # Convert date to datetime object and format it as DD/MM/YYYY
            try:
                date = datetime.strptime(date, '%Y-%m-%d').strftime('%d/%m/%Y')
            except ValueError:
                return jsonify({'error': 'Format tanggal salah.'}), 400

            new_room = {
                'room_type': room_type,
                'date': date,
                'price': normal_price,
                'discount_price': discount_price,
                'stock': stock,
                'created_at': datetime.now(wib),
                'updated_at': datetime.now(wib)
            }

            db.room_prices.insert_one(new_room)
            return redirect(url_for('admin_room'))
        
        return render_template('admin/room/add_room.html', admin_info=admin_info)
    else:
        return redirect(url_for('login_admin'))

@app.route('/admin/guest', methods=['GET'])
def admin_guest():
    admin_info = get_admin_info()
    if admin_info:
        search_query = request.args.get('search')
        booking_code_query = request.args.get('booking_code')
        date_query = request.args.get('date')
        entries_per_page = int(request.args.get('entries_per_page', 10))
        page = int(request.args.get('page', 1))

        query = {}
        if search_query:
            query['tipe_kamar'] = {'$regex': search_query, '$options': 'i'}
        if booking_code_query:
            query['booking_code'] = {'$regex': booking_code_query, '$options': 'i'}

        # Retrieve guests from both collections
        deluxe_guests = list(db.deluxe_booking.find(query)
                             .sort('created_at', -1)
                             .skip((page - 1) * entries_per_page)
                             .limit(entries_per_page))
        
        family_deluxe_guests = list(db.family_deluxe_booking.find(query)
                                    .sort('created_at', -1)
                                    .skip((page - 1) * entries_per_page)
                                    .limit(entries_per_page))

        # Combine the two lists
        guests = deluxe_guests + family_deluxe_guests

        # Ensure created_at is a datetime object and sort the combined list by 'created_at' in descending order
        for guest in guests:
            if isinstance(guest['created_at'], str):
                try:
                    guest['created_at'] = datetime.strptime(guest['created_at'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    guest['created_at'] = datetime.strptime(guest['created_at'], '%d/%m/%Y %H:%M:%S')

        guests = sorted(guests, key=lambda x: x['created_at'], reverse=True)

        # Calculate the total number of guests from both collections
        total_deluxe_guests = db.deluxe_booking.count_documents(query)
        total_family_deluxe_guests = db.family_deluxe_booking.count_documents(query)
        total_guests = total_deluxe_guests + total_family_deluxe_guests

        # Calculate total pages
        total_pages = (total_guests + entries_per_page - 1) // entries_per_page

        return render_template('admin/guest/guest.html', 
                               guests=guests, 
                               admin_info=admin_info, 
                               page=page, 
                               total_pages=total_pages, 
                               total_guests=total_guests, 
                               entries_per_page=entries_per_page, 
                               format_currency=format_currency)
    else:
        return redirect(url_for('login_admin'))

@app.route('/admin/guest/delete/<guest_id>', methods=['POST'])
def admin_delete_guest(guest_id):
    if 'logged_in' in session:
        # Hapus dari deluxe_booking
        deluxe_result = db.deluxe_booking.delete_one({'_id': ObjectId(guest_id)})
        
        # Hapus dari family_deluxe_booking
        family_deluxe_result = db.family_deluxe_booking.delete_one({'_id': ObjectId(guest_id)})
        
        # Cek apakah ada data yang terhapus dari salah satu koleksi
        if deluxe_result.deleted_count > 0 or family_deluxe_result.deleted_count > 0:
            return jsonify({'result': 'success'})
        else:
            return jsonify({'result': 'error', 'message': 'Failed to delete guest'}), 400
    else:
        return jsonify({'result': 'error', 'message': 'Unauthorized'}), 401

@app.route('/admin/guest/bulk_delete', methods=['POST'])
def admin_bulk_delete_guests():
    if 'logged_in' in session:
        guest_ids = request.json.get('guest_ids', [])
        if guest_ids:
            db.deluxe_booking.delete_many({'_id': {'$in': [ObjectId(guest_id) for guest_id in guest_ids]}})
            db.family_deluxe_booking.delete_many({'_id': {'$in': [ObjectId(guest_id) for guest_id in guest_ids]}})

            return jsonify({'result': 'success'})
        return jsonify({'result': 'error', 'message': 'No guests selected'}), 400
    else:
        return jsonify({'result': 'error', 'message': 'Unauthorized'}), 401

@app.route('/admin/guest/edit/<guest_id>', methods=['GET', 'POST'])
def admin_edit_guest(guest_id):
    if 'logged_in' in session:
        admin_info = get_admin_info()
        guest = db.deluxe_booking.find_one({'_id': ObjectId(guest_id)})

        if request.method == 'POST':
            booking_code = request.form.get('bookingCode')
            nama_lengkap = request.form.get('namaLengkap')
            email = request.form.get('email')
            nomor_handphone = request.form.get('nomorHandphone')
            pesanan_untuk = request.form.get('pesananUntuk')
            guest_name = request.form.get('guestName')
            lama_inap = request.form.get('lamaInap')
            harga_normal = request.form.get('hargaNormal')
            harga_diskon = request.form.get('hargaDiskon')
            harga_total = request.form.get('hargaTotal')
            check_in_date = request.form.get('checkInDate')
            check_out_date = request.form.get('checkOutDate')
            status = request.form.get('status')
            alasan_penolakan = request.form.get('alasan_penolakan')
            updated_at = datetime.now(wib)
            if status == 'pesanan ditolak' and not alasan_penolakan:
                return jsonify({'error': 'Alasan penolakan wajib diisi'}), 400
            # Convert numeric values
            try:
                lama_inap = int(lama_inap)
                harga_normal = float(harga_normal)
                harga_diskon = float(harga_diskon)
                harga_total = float(harga_total)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

            db.deluxe_booking.update_one(
                {'_id': ObjectId(guest_id)},
                {'$set': {
                    'booking_code': booking_code,
                    'nama_lengkap': nama_lengkap,
                    'email': email,
                    'nomor_handphone': nomor_handphone,
                    'pesanan_untuk': pesanan_untuk,
                    'guest_name': guest_name,
                    'lama_inap': lama_inap,
                    'harga_normal': harga_normal,
                    'harga_diskon': harga_diskon,
                    'harga_total': harga_total,
                    'check_in_date': check_in_date,
                    'check_out_date': check_out_date,
                    'status': status,
                    'alasan_penolakan': alasan_penolakan,
                    'updated_at': updated_at
                }}
            )
            return redirect(url_for('admin_guest'))

        return render_template('admin/guest/edit_guest.html', admin_info=admin_info, guest=guest)
    else:
        return redirect(url_for('login_admin'))

@app.route('/admin/guest/edit/familydlx/<guest_id>', methods=['GET', 'POST'])
def admin_edit_family_guest(guest_id):
    if 'logged_in' in session:
        admin_info = get_admin_info()
        guest = db.family_deluxe_booking.find_one({'_id': ObjectId(guest_id)})

        if request.method == 'POST':
            booking_code = request.form.get('bookingCode')
            nama_lengkap = request.form.get('namaLengkap')
            email = request.form.get('email')
            nomor_handphone = request.form.get('nomorHandphone')
            pesanan_untuk = request.form.get('pesananUntuk')
            guest_name = request.form.get('guestName')
            lama_inap = request.form.get('lamaInap')
            harga_normal = request.form.get('hargaNormal')
            harga_diskon = request.form.get('hargaDiskon')
            harga_total = request.form.get('hargaTotal')
            check_in_date = request.form.get('checkInDate')
            check_out_date = request.form.get('checkOutDate')
            status = request.form.get('status')
            alasan_penolakan = request.form.get('alasan_penolakan')
            updated_at = datetime.now(wib)

            if status == 'pesanan ditolak' and not alasan_penolakan:
                return jsonify({'error': 'Alasan penolakan wajib diisi'}), 400
            # Convert numeric values
            try:
                lama_inap = int(lama_inap)
                harga_normal = float(harga_normal)
                harga_diskon = float(harga_diskon)
                harga_total = float(harga_total)
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

            db.family_deluxe_booking.update_one(
                {'_id': ObjectId(guest_id)},
                {'$set': {
                    'booking_code': booking_code,
                    'nama_lengkap': nama_lengkap,
                    'email': email,
                    'nomor_handphone': nomor_handphone,
                    'pesanan_untuk': pesanan_untuk,
                    'guest_name': guest_name,
                    'lama_inap': lama_inap,
                    'harga_normal': harga_normal,
                    'harga_diskon': harga_diskon,
                    'harga_total': harga_total,
                    'check_in_date': check_in_date,
                    'check_out_date': check_out_date,
                    'status': status,
                    'alasan_penolakan': alasan_penolakan,
                    'updated_at': updated_at
                }}
            )
            return redirect(url_for('admin_guest'))

        return render_template('admin/guest/edit_family_guest.html', admin_info=admin_info, guest=guest)
    else:
        return redirect(url_for('login_admin'))

if __name__ == '__main__':
    app.run("0.0.0.0", port=5000, debug=True)
