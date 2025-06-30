from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Konfigurasi koneksi database MySQL
app.config.update({
    'MYSQL_HOST': 'localhost',
    'MYSQL_USER': 'root',
    'MYSQL_PASSWORD': '',
    'MYSQL_DB': 'film'
})

mysql = MySQL(app)

# ROUTE UTAMA 
@app.route('/')
def beranda():
    # Redirect ke halaman GUI
    return redirect(url_for('tampilkan_gui'))

# HALAMAN GUI
@app.route('/gui', methods=['GET'])
def tampilkan_gui():
    # Ambil semua data film dari database
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM film")
    semua_data = cursor.fetchall()
    cursor.close()
    return render_template("index1.html", data=semua_data)

@app.route('/add_gui', methods=['GET', 'POST'])
def tambah_gui():
    if request.method == 'POST':
        # Ambil data input dari form
        judul_film = request.form['judul_film']
        sutradara = request.form['sutradara']
        tahun_rilis = request.form['tahun_rilis']
        genre = request.form['genre']

        if not all([judul_film, sutradara, tahun_rilis, genre]):
            return "Semua kolom harus diisi", 400
        
        try:
            # Simpan data ke database
            cursor = mysql.connection.cursor()
            cursor.execute(
                "INSERT INTO film (judul_film, sutradara, tahun_rilis, genre) VALUES (%s, %s, %s, %s)",
                (judul_film, sutradara, tahun_rilis, genre))
            mysql.connection.commit()
            cursor.close()
            return redirect(url_for('tampilkan_gui'))
        except Exception as err:
            return f"Terjadi error: {err}", 500
    
    return render_template('add1.html')

@app.route('/edit_gui/<int:id>', methods=['GET', 'POST'])
def edit_gui(id):
    cursor = mysql.connection.cursor()
    if request.method == 'POST':
        # Update data film berdasarkan ID
        judul_film = request.form['judul_film']
        sutradara = request.form['sutradara']
        tahun_rilis = request.form['tahun_rilis']
        genre = request.form['genre']

        cursor.execute(
            "UPDATE film SET judul_film=%s, sutradara=%s, tahun_rilis=%s, genre=%s WHERE id=%s",
            (judul_film, sutradara, tahun_rilis, genre, id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('tampilkan_gui'))
    else:
        # Ambil data film yang mau diedit
        cursor.execute("SELECT * FROM film WHERE id = %s", (id,))
        data_film = cursor.fetchone()
        cursor.close()
        return render_template('edit1.html', row=data_film)

@app.route('/delete_gui/<int:id>')
def hapus_gui(id):
    # Hapus data film berdasarkan ID
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM film WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('tampilkan_gui'))

# -------- API ENDPOINTS --------
@app.route('/film', methods=['GET'])
def semua_film():
    # API untuk ambil semua data film
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM film")
    data = cursor.fetchall()
    cursor.close()

    hasil = [{
        'id': row[0],
        'judul_film': row[1],
        'sutradara': row[2],
        'tahun_rilis': row[3],
        'genre': row[4]
    } for row in data]
    
    return jsonify(hasil)

@app.route('/film/<int:id>', methods=['GET'])
def film_berdasarkan_id(id):
    # API ambil film berdasarkan ID
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM film WHERE id = %s", (id,))
    row = cursor.fetchone()
    cursor.close()

    if row:
        return jsonify({
            'id': row[0],
            'judul_film': row[1],
            'sutradara': row[2],
            'tahun_rilis': row[3],
            'genre': row[4]
        })
    return jsonify({'error': f'Film dengan ID {id} tidak ditemukan'}), 404

@app.route('/film', methods=['POST'])
def tambah_film():
    # API tambah data film
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data JSON kosong'}), 400

    judul_film = data.get('judul_film')
    sutradara = data.get('sutradara')
    tahun_rilis = data.get('tahun_rilis')
    genre = data.get('genre')

    if not all([judul_film, sutradara, tahun_rilis, genre]):
        return jsonify({'error': 'Semua kolom wajib diisi'}), 400
    
    try:
        tahun_rilis = int(tahun_rilis)
    except ValueError:
        return jsonify({'error': 'tahun_rilis harus berupa angka'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute(
        "INSERT INTO film (judul_film, sutradara, tahun_rilis, genre) VALUES (%s, %s, %s, %s)",
        (judul_film, sutradara, tahun_rilis, genre))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': f'Film "{judul_film}" berhasil ditambahkan!'})

@app.route('/film/<int:id>', methods=['PUT'])
def update_film(id):
    # API update data film
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Data JSON kosong'}), 400

    judul_film = data.get('judul_film')
    sutradara = data.get('sutradara')
    tahun_rilis = data.get('tahun_rilis')
    genre = data.get('genre')

    if not all([judul_film, sutradara, tahun_rilis, genre]):
        return jsonify({'error': 'Semua kolom wajib diisi'}), 400
    
    try:
        tahun_rilis = int(tahun_rilis)
    except ValueError:
        return jsonify({'error': 'tahun_rilis harus angka'}), 400

    cursor = mysql.connection.cursor()
    cursor.execute(
        "UPDATE film SET judul_film=%s, sutradara=%s, tahun_rilis=%s, genre=%s WHERE id=%s",
        (judul_film, sutradara, tahun_rilis, genre, id))
    mysql.connection.commit()
    cursor.close()

    return jsonify({'message': f'Film dengan ID {id} berhasil diupdate!'})

@app.route('/film/<int:id>', methods=['DELETE'])
def hapus_film(id):
    # API hapus film berdasarkan ID
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM film WHERE id = %s", (id,))
    mysql.connection.commit()
    cursor.close()
    return jsonify({'message': f'Film dengan ID {id} berhasil dihapus!'})

if __name__ == '__main__':
    app.run(debug=True)
