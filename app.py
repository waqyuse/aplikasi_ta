from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Pastikan ini adalah kunci rahasia yang aman

# Konfigurasi database menggunakan SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Folder untuk menyimpan file audio yang diupload
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50 MB

# Definisi model User untuk menyimpan data pengguna
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150), nullable=False)

# Membuat tabel di database
with app.app_context():
    db.create_all()

# Simpan daftar audio
recorded_audios = []

# Fungsi untuk memuat daftar file audio dari folder 'uploads'
def load_audios():
    global recorded_audios
    if os.path.exists(app.config['UPLOAD_FOLDER']):
        recorded_audios = os.listdir(app.config['UPLOAD_FOLDER'])

# Rute login
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['username'] = username
            return redirect(url_for('index'))  # Jika login berhasil
        else:
            flash('Login gagal. Periksa username atau password Anda.')
    return render_template('login.html')

# Rute registrasi
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Periksa apakah username sudah ada di database
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username sudah digunakan. Coba username lain.')
        else:
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            new_user = User(username=username, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registrasi berhasil. Silakan login.')
            return redirect(url_for('login'))
    return render_template('register.html')

# Halaman utama setelah login
@app.route('/index')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    load_audios()  # Muat ulang daftar audio setiap kali halaman diakses
    return render_template('index.html', audios=recorded_audios)

# Rute logout
@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

# Rute Tentang Peneliti
@app.route('/tentang_peneliti')
def tentang_peneliti():
    return render_template('tentang_peneliti.html')

# Rute untuk menyimpan audio yang diunggah
@app.route('/save_audio', methods=['POST'])
def save_audio():
    if request.method == 'POST':
        file = request.files.get('file')
        if file and file.filename.endswith('.wav'):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            # Simpan ke dalam daftar audio
            recorded_audios.append(filename)
            return jsonify({"message": "Audio saved successfully!", "filename": filename})
        else:
            return jsonify({"message": "Invalid file type. Only .wav files are allowed."}), 400
    return jsonify({"message": "Failed to save audio."}), 400

# Endpoint untuk melayani audio yang disimpan
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Rute untuk menghapus audio
@app.route('/delete_audio/<filename>', methods=['POST'])
def delete_audio(filename):
    global recorded_audios
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))  # Hapus file fisik
        recorded_audios = [audio for audio in recorded_audios if audio != filename]  # Hapus dari daftar
        return jsonify({"message": "Audio deleted successfully!"})
    except FileNotFoundError:
        return jsonify({"message": "File not found!"}), 404

# Memuat daftar audio saat server dimulai
if __name__ == '__main__':
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs(app.config['UPLOAD_FOLDER'])
    load_audios()  # Muat daftar audio ketika server dimulai
    app.run(debug=True)
