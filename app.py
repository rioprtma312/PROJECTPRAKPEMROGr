# Import library yang dibutuhkan
from flask import Flask, request, jsonify, render_template, redirect, url_for  # Flask dan modul-modulnya
from flask_mysqldb import MySQL  # Untuk koneksi ke MySQL
from flask_cors import CORS  # Mengizinkan CORS (akses lintas domain)

app = Flask(__name__)  # Inisialisasi aplikasi Flask
CORS(app)  # Aktifkan CORS

# Konfigurasi koneksi MySQL untuk XAMPP
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'film'

mysql = MySQL(app)  # Inisialisasi objek MySQL

#ROUTE AWAL
@app.route('/')
def home():
    # Redirect ke halaman GUI
    return redirect(url_for('gui'))

#GUI
@app.route('/gui', methods=['GET'])
def gui():
    # Ambil semua data film dari database dan render ke template HTML
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM film")
    data = cur.fetchall()
    cur.close()
    return render_template("index.html", data=data)

@app.route('/add_gui', methods=['GET', 'POST'])
def add_gui():
    # Tambahkan data film dari form GUI
    if request.method == 'POST':
        # Ambil data dari form HTML
        judul_film = request.form['judul_film']
        sutradara = request.form['sutradara']
        tahun_rilis = request.form['tahun_rilis']
        genre = request.form['genre']

        # Validasi input wajib diisi
        if not all([judul_film, sutradara, tahun_rilis, genre]):
            return "Semua field wajib diisi", 400

        try:
            # Masukkan data ke database
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO film (judul_film, sutradara, tahun_rilis, genre) VALUES (%s, %s, %s, %s)",
                        (judul_film, sutradara, tahun_rilis, genre))
            mysql.connection.commit()
            cur.close()
            return redirect(url_for('gui'))  # Redirect ke halaman GUI
        except Exception as e:
            return f"Terjadi kesalahan: {str(e)}", 500

    # Jika GET, tampilkan form tambah film
    return render_template('add.html')

@app.route('/edit_gui/<int:id>', methods=['GET', 'POST'])
def edit_gui(id):
    cur = mysql.connection.cursor()
    if request.method == 'POST':
        # Ambil data baru dari form
        judul_film = request.form['judul_film']
        sutradara = request.form['sutradara']
        tahun_rilis = request.form['tahun_rilis']
        genre = request.form['genre']

        # Update data di database berdasarkan ID
        cur.execute("""UPDATE film SET judul_film=%s, sutradara=%s, tahun_rilis=%s, genre=%s WHERE id=%s""",
                    (judul_film, sutradara, tahun_rilis, genre, id))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('gui'))  # Redirect ke GUI
    else:
        # Ambil data film yang akan diedit
        cur.execute("SELECT * FROM film WHERE id = %s", (id,))
        data = cur.fetchone()
        cur.close()
        return render_template('edit.html', row=data)

@app.route('/delete_gui/<int:id>')
def delete_gui(id):
    # Hapus data film berdasarkan ID dan redirect ke GUI
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM film WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('gui'))

# ---------- API ----------
@app.route('/film', methods=['GET'])
def get_all():
    # Ambil semua data film dan kembalikan dalam format JSON
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM film")
    data = cur.fetchall()
    cur.close()

    # Ubah data ke bentuk list of dict
    result = []
    for row in data:
        result.append({
            'id': row[0],
            'judul_film': row[1],
            'sutradara': row[2],
            'tahun_rilis': row[3],
            'genre': row[4]
        })
    return jsonify(result)

@app.route('/film/<int:id>', methods=['GET'])
def get_by_id(id):
    # Ambil data film berdasarkan ID
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM film WHERE id = %s", (id,))
    data = cur.fetchone()
    cur.close()

    # Kembalikan data dalam bentuk JSON jika ditemukan
    if data:
        return jsonify({
            'id': data[0],
            'judul_film': data[1],
            'sutradara': data[2],
            'tahun_rilis': data[3],
            'genre': data[4]
        })
    else:
        return jsonify({'error': f'Film dengan ID {id} tidak ditemukan'}), 404

@app.route('/film', methods=['POST'])
def create():
    # Tambahkan data film lewat API
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data JSON tidak ditemukan'}), 400

    # Ambil data dari JSON
    judul_film = data.get('judul_film')
    sutradara = data.get('sutradara')
    tahun_rilis = data.get('tahun_rilis')
    genre = data.get('genre')

    # Validasi data
    if not all([judul_film, sutradara, tahun_rilis, genre]):
        return jsonify({'error': 'Semua field wajib diisi'}), 400

    try:
        tahun_rilis = int(tahun_rilis)
    except ValueError:
        return jsonify({'error': 'tahun_rilis harus angka'}), 400

    # Simpan ke database
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO film (judul_film, sutradara, tahun_rilis, genre) VALUES (%s, %s, %s, %s)",
                (judul_film, sutradara, tahun_rilis, genre))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': f'Film "{judul_film}" berhasil ditambahkan!'})

@app.route('/film/<int:id>', methods=['PUT'])
def update(id):
    # Perbarui data film lewat API
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data JSON tidak ditemukan'}), 400

    # Ambil data dari JSON
    judul_film = data.get('judul_film')
    sutradara = data.get('sutradara')
    tahun_rilis = data.get('tahun_rilis')
    genre = data.get('genre')

    # Validasi data
    if not all([judul_film, sutradara, tahun_rilis, genre]):
        return jsonify({'error': 'Semua field wajib diisi'}), 400

    try:
        tahun_rilis = int(tahun_rilis)
    except ValueError:
        return jsonify({'error': 'tahun_rilis harus angka'}), 400

    # Update data di database
    cur = mysql.connection.cursor()
    cur.execute("""UPDATE film SET judul_film=%s, sutradara=%s, tahun_rilis=%s, genre=%s WHERE id=%s""",
                (judul_film, sutradara, tahun_rilis, genre, id))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': f'Film dengan ID {id} berhasil diupdate!'})

@app.route('/film/<int:id>', methods=['DELETE'])
def delete(id):
    # Hapus data film berdasarkan ID lewat API
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM film WHERE id = %s", (id,))
    mysql.connection.commit()
    cur.close()
    return jsonify({'message': f'Film dengan ID {id} berhasil dihapus!'})

# Jalankan aplikasi Flask jika file ini dieksekusi langsung
if __name__ == '__main__':
    app.run(debug=True)
