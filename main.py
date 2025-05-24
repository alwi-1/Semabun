import streamlit as st
from database import create_connection
from enum import Enum
from streamlit_option_menu import option_menu
import pandas as pd
from mysql.connector import Error
from PIL import Image


st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #A5D6A7 0%, #81C784 50%, #388E3C 100%);
        background-attachment: fixed;
        background-size: cover;
        background-repeat: no-repeat;
    }

    input, select, button, textarea {
        border-radius: 8px !important;
    }

    h1, h2, h3 {
        color: #1B5E20;
        font-family: 'Segoe UI', sans-serif;
    }

    p, label {
        color: #2E7D32;
        font-family: 'Segoe UI', sans-serif;
    }
    </style>
""", unsafe_allow_html=True)

# Koneksi ke database
try:
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    db_name = cursor.fetchone()
    cursor.close()
    conn.close()
except Exception as e:
    st.error(f"Koneksi Gagal: {e}")


# Atur halaman default
if "halaman" not in st.session_state:
    st.session_state.halaman = "Login"

# ---------- LOGIN FUNCTION ----------
def login_user(email, password):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        query = "SELECT * FROM daftar WHERE email = %s AND password = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        return user  # <--- Kembalikan data user (tuple), bukan True/False

# ---------- FORM LOGIN ---------- #
def halaman_login():
    
    # Tampilkan logo di atas
    col1, col2 = st.columns([2, 4])
    with col1:
        logo = Image.open("logo.png")
        st.image(logo, width=240)
    with col2:
        st.markdown("""
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

                .judul-app {
                    font-family: 'Poppins', sans-serif;
                    color: #2E7D32;
                    font-size: 32px;
                    font-weight: 600;
                    margin-bottom: 10px;
                }

                .deskripsi-app {
                    font-family: 'Poppins', sans-serif;
                    font-size: 15px;
                    color: #444;
                    line-height: 1.6;
                    margin-top: 0px;
                }

                .box-wrapper {
                    background-color: #F0F0F0;
                    padding: 20px;
                    border-radius: 12px;
                    box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
                }
            </style>

            <div class="box-wrapper">
                <div class="judul-app">Semabun</div>
                <div class="deskripsi-app">
                    <em>Sistem Informasi Perkebunan Semangka</em><br>
                    Aplikasi pencatatan keuangan modern untuk usaha pertanian semangka.
                </div>
            </div>
        """, unsafe_allow_html=True)



    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        user = login_user(email, password)  
        
        if user is not None:
            # Login berhasil, simpan session state
            st.session_state.user_name = user[0]  # nama
            st.session_state.user_email = user[3]  # email
            st.session_state.halaman = "home"
            
            # Tampilkan pesan sukses setelah login
            st.success("Login berhasil!")  # Pesan sukses tampil di halaman
        else:
            st.error("Email atau password salah.")


    # Tambahan: tombol daftar
    if st.button("Belum punya akun? Daftar di sini"):
        st.session_state.halaman = "Daftar"

# ---------- FORM PENDAFTARAN ----------
def halaman_daftar():
    st.title("Formulir Pendaftaran")

    nama = st.text_input("Nama")
    jenis_kelamin = st.selectbox("Jenis Kelamin", [e.value for e in JenisKelamin])
    umur = st.number_input("Umur", min_value=0, max_value=120, step=1)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    if st.button("Daftar"):
        if not (nama and email and password):
            st.warning("Semua field wajib diisi!")
        else:
            insert_data(nama, jenis_kelamin, umur, email, password)
    # Tambahan: tombol login
    if st.button("Sudah punya akun? Login di sini"):
        st.session_state.halaman = "Login"

# ---------- ENUM ----------
class JenisKelamin(Enum):
    Laki_laki = "Laki-laki"
    Perempuan = "Perempuan"

# ---------- DATABASE TABLE ----------
def create_table():
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daftar (
                nama VARCHAR(100),
                jenis_kelamin ENUM('Laki-laki', 'Perempuan'),
                umur INT,
                email VARCHAR(100) PRIMARY KEY,
                password VARCHAR(255)
            )
        """)
        connection.commit()
        cursor.close()
        connection.close()

# ---------- INSERT USER ----------
def insert_data(nama, jenis_kelamin, umur, email, password):
    connection = create_connection()
    if connection:
        cursor = connection.cursor()

        # Cek apakah email sudah terdaftar
        cursor.execute("SELECT * FROM daftar WHERE email = %s", (email,))
        existing_user = cursor.fetchone()

        if existing_user:
            st.error("Email sudah terdaftar. Silakan gunakan email lain.")
        else:
            query = """
                INSERT INTO daftar (nama, jenis_kelamin, umur, email, password)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(query, (nama, jenis_kelamin, umur, email, password))
            connection.commit()
            st.success("Pendaftaran berhasil!")

        cursor.close()
        connection.close()


# ---------- HOME ----------
def halaman_home():
    if "user_name" not in st.session_state or "user_email" not in st.session_state:
        st.warning("Silakan login terlebih dahulu.")
        st.session_state.halaman = "Login"
        return
    
    
    # --- CODE-CODE TAMPILAN DI HOME PAGE ---
    with st.sidebar:
        selected = option_menu(
        "Semabun",
        ["Tentang", "Persediaan", "Pengeluaran", "Pemasukan", 
        "Laba Rugi", "Logout"],
        icons=["cast", "box", "file-earmark-text", "book", "pencil", "box-arrow-right"],
        menu_icon="house",
        default_index=0,
        styles={
            "container": {"padding": "10px", "background-color": "#999999"},
            "icon": {"color": "black", "font-size": "18px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "2px",
                "--hover-color": "#71718D"
            },
            "nav-link-selected": {"background-color": "#4CAF50", "color": "white"},
        }
    )


# ---------- TAMPILAN DALAM SUB MENU HOME PAGE ---------- #
    halaman = selected

# ---------- TAMPILAN TENTANG ---------- #
    if selected == "Tentang":
        st.markdown("""
            <!-- Import font Poppins dari Google Fonts -->
            <link href="https://fonts.googleapis.com/css2?family=Poppins&display=swap" rel="stylesheet">

            <style>
                .judul-wrapper {
                    background-color: #F0F0F0;
                    padding: 20px 25px;
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    margin-top: 10px;
                }

                .judul-wrapper h1 {
                    color: #2E7D32;
                    font-size: 38px;
                    margin-bottom: 6px;
                    font-family: "Segoe UI", sans-serif;
                }

                .judul-wrapper p {
                    color: #388E3C;
                    font-size: 17px;
                    font-style: italic;
                    margin-bottom: 0;
                    font-family: "Segoe UI", sans-serif;
                    letter-spacing: 0.3px;
                }

                .penjelasan {
                    margin-top: 25px;
                    padding: 25px;
                    background-color: #F0F0F0;  /* samain abu2 box judul */
                    border-radius: 12px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                    font-family: 'Poppins', sans-serif;
                    color: #222;
                    font-size: 16px;
                    line-height: 1.75;
                    text-align: justify;
                }

                .kutipan {
                    text-align: center;
                    padding: 40px 20px 20px 20px;
                    font-family: "Segoe UI", sans-serif;
                }

                .kutipan p {
                    font-size: 20px;
                    font-style: italic;
                    font-weight: 600;
                    color: #C0C0C0;
                    
                    
                    margin: 0;
                }
            </style>
        """, unsafe_allow_html=True)

        # Layout kolom logo + judul
        col1, col2 = st.columns([1, 2])

        with col1:
            st.image("logo.png", width=180)

        with col2:
            st.markdown("""
                <div class="judul-wrapper">
                    <h1>Semabun</h1>
                    <p>Sistem Informasi Perkebunan Semangka</p>
                </div>
            """, unsafe_allow_html=True)

        # Penjelasan utama
        st.markdown("""
            <div class="penjelasan">
                Dengan kemajuan teknologi, kami memperkenalkan sistem perkebunan semangka inovatif yang membantu
                petani mengelola data kebun dengan lebih efisien dan akurat. Sistem ini dilengkapi fitur penginputan
                data otomatis real-time, sehingga petani dapat menghemat waktu dan tenaga, serta mengurangi risiko
                kesalahan pencatatan.
                <br><br>
                Sistem ini juga membantu petani memantau kondisi kebun secara real-time, membuat keputusan tepat
                untuk meningkatkan hasil panen dan mengurangi biaya operasional. Kami berharap sistem ini menjadi
                solusi efektif bagi petani semangka.
            </div>
        """, unsafe_allow_html=True)

        # Kutipan
        st.markdown("""
            <div class="kutipan">
                <p>
                    “Semangka manis tak tumbuh dari kemalasan, tapi dari kerja keras dan ketekunan yang luar biasa.”
                </p>
            </div>
        """, unsafe_allow_html=True)

# ---------- TAMPILAN PERSEDIAAN ---------- #
    elif selected == "Persediaan":
        st.header("Persediaan")

# ---------- Fungsi CRUD Persediaan ---------- #
        def get_persediaan():
            conn = create_connection()
            if conn:
                cursor = conn.cursor(dictionary=True)
                # Fungsi get_persediaan() dengan filter user_email
                cursor.execute("SELECT * FROM persediaan WHERE user_email = %s ORDER BY kode_barang", (st.session_state.user_email,))
                data = cursor.fetchall()
                cursor.close()
                conn.close()
                return data
            return []

        def insert_persediaan(kode, nama, kategori, satuan, stok_awal, masuk, keluar, harga_satuan, lokasi):
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                stok_akhir = stok_awal + masuk - keluar
                nilai_total = stok_akhir * harga_satuan
                # Fungsi insert_persediaan() menyimpan user_email
                cursor.execute("""
                    INSERT INTO persediaan 
                    (kode_barang, nama_barang, kategori, satuan, stok_awal, stok_masuk, stok_keluar, stok_akhir, harga_satuan, nilai_total, lokasi, user_email)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                """, (kode, nama, kategori, satuan, stok_awal, masuk, keluar, stok_akhir, harga_satuan, nilai_total, lokasi, st.session_state.user_email))
                conn.commit()
                cursor.close()
                conn.close()

        def update_persediaan(id, kode, nama, kategori, satuan, stok_awal, masuk, keluar, harga_satuan, lokasi):
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                stok_akhir = stok_awal + masuk - keluar
                nilai_total = stok_akhir * harga_satuan
                cursor.execute("""
                    UPDATE persediaan SET 
                        kode_barang=%s, nama_barang=%s, kategori=%s, satuan=%s, stok_awal=%s, stok_masuk=%s, stok_keluar=%s, stok_akhir=%s, harga_satuan=%s, nilai_total=%s, lokasi=%s
                    WHERE id=%s
                """, (kode, nama, kategori, satuan, stok_awal, masuk, keluar, stok_akhir, harga_satuan, nilai_total, lokasi, id))
                conn.commit()
                cursor.close()
                conn.close()

        def delete_persediaan(id):
            conn = create_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM persediaan WHERE id=%s", (id,))
                conn.commit()
                cursor.close()
                conn.close()

        # --- Form Tambah / Edit ---
        with st.expander("➕ Tambah / Edit Persediaan"):
            with st.form("form_persediaan", clear_on_submit=False):
                edit_mode = "edit_persediaan" in st.session_state
                edit_data = st.session_state.get("edit_persediaan", {})

                id_edit = edit_data.get("id", "") if edit_mode else ""

                kode_barang = st.text_input("Kode Barang", value=edit_data.get("kode_barang", "") if edit_mode else "")
                nama_barang = st.text_input("Nama Barang", value=edit_data.get("nama_barang", "") if edit_mode else "")
                # --- pemilihan kategori --- #
                kategori_options = ["Bibit", "Pupuk", "Pestisida", "Alat"]
                default_kategori_idx = kategori_options.index(edit_data.get("kategori")) if edit_mode and edit_data.get("kategori") in kategori_options else 0
                kategori = st.selectbox("Kategori", kategori_options, index=default_kategori_idx)

                satuan_options = ["Biji", "Kg", "Liter", "Botol / Drum / Galon", "Pack / Sachet", "Karung", "Pcs"]
                default_satuan_idx = satuan_options.index(edit_data.get("satuan")) if edit_mode and edit_data.get("satuan") in satuan_options else 1
                satuan = st.selectbox("Satuan", satuan_options, index=default_satuan_idx)

                stok_awal = st.number_input("Stok Awal", min_value=0, value=int(edit_data.get("stok_awal", 0)) if edit_mode else 0)
                stok_masuk = st.number_input("Stok Masuk", min_value=0, value=int(edit_data.get("stok_masuk", 0)) if edit_mode else 0)
                stok_keluar = st.number_input("Stok Keluar", min_value=0, value=int(edit_data.get("stok_keluar", 0)) if edit_mode else 0)

                harga_satuan = st.number_input("Harga Satuan", min_value=0.0, step=100.0, value=float(edit_data.get("harga_satuan", 0)) if edit_mode else 0.0)
                lokasi = st.text_input("Lokasi Penyimpanan", value=edit_data.get("lokasi", "") if edit_mode else "")

                submitted = st.form_submit_button("Simpan Persediaan")

                if submitted:
                    if kode_barang.strip() == "" or nama_barang.strip() == "":
                        st.warning("Kode Barang dan Nama Barang tidak boleh kosong.")
                    else:
                        if edit_mode:
                            update_persediaan(id_edit, kode_barang, nama_barang, kategori, satuan, stok_awal, stok_masuk, stok_keluar, harga_satuan, lokasi)
                            st.success("Data persediaan berhasil diperbarui.")
                            st.session_state.pop("edit_persediaan", None)
                        else:
                            insert_persediaan(kode_barang, nama_barang, kategori, satuan, stok_awal, stok_masuk, stok_keluar, harga_satuan, lokasi)
                            st.success("Data persediaan berhasil ditambahkan.")
                        st.rerun()


        # --- UI Halaman Persediaan ---
        st.subheader("")

        data = get_persediaan()
        if data:
            df = pd.DataFrame(data)

            # Tambah baris total nilai di bawah tabel
            total_nilai = df["nilai_total"].sum()
            total_row = {
                "id": "",
                "kode_barang": "",
                "nama_barang": "",
                "kategori": "",
                "satuan": "",
                "stok_awal": "",
                "stok_masuk": "",
                "stok_keluar": "",
                "stok_akhir": "",
                "harga_satuan": "TOTAL",
                "nilai_total": total_nilai,
                "lokasi": ""
            }
            df_total = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

            st.dataframe(df_total[[
                "id", "kode_barang", "nama_barang", "kategori", "satuan",
                "stok_awal", "stok_masuk", "stok_keluar", "stok_akhir",
                "harga_satuan", "nilai_total", "lokasi"]], use_container_width=True)

            st.write("---")
            st.subheader("Aksi Edit & Hapus")
            for i, row in enumerate(data):
                col1, col2 = st.columns([1, 8])
                with col1:
                    if st.button(" Edit", key=f"edit_{i}"):
                        st.session_state["edit_persediaan"] = row
                        st.rerun()
                with col2:
                    if st.button(" Hapus", key=f"delete_{i}"):
                        delete_persediaan(row["id"])
                        st.success("Data persediaan berhasil dihapus.")
                        st.rerun()
        else:
            st.warning("Belum ada data persediaan.")
#baru sampai sini
# ---------- PENGELUARAN ---------- #
    elif selected == "Pengeluaran":
        st.header("Pengeluaran")

        # ---------- Fungsi Database ----------
        def get_pengeluaran():
            connection = create_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM pengeluaran WHERE user_email = %s ORDER BY tanggal DESC", (st.session_state.user_email,))
                result = cursor.fetchall()
                cursor.close()
                connection.close()
                return result

        def insert_pengeluaran(tanggal, keterangan, kategori, jumlah, satuan, harga_satuan):
            total_harga = jumlah * harga_satuan
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    INSERT INTO pengeluaran (tanggal, keterangan, kategori, jumlah, satuan, harga_satuan, total_harga, user_email)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (tanggal, keterangan, kategori, jumlah, satuan, harga_satuan, total_harga, st.session_state.user_email))
                connection.commit()
                cursor.close()
                connection.close()

        def update_pengeluaran(id, tanggal, keterangan, kategori, jumlah, satuan, harga_satuan):
            total_harga = jumlah * harga_satuan
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("""
                    UPDATE pengeluaran SET tanggal=%s, keterangan=%s, kategori=%s, jumlah=%s,
                    satuan=%s, harga_satuan=%s, total_harga=%s WHERE id=%s
                """, (tanggal, keterangan, kategori, jumlah, satuan, harga_satuan, total_harga, id))
                connection.commit()
                cursor.close()
                connection.close()

        def delete_pengeluaran(id):
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM pengeluaran WHERE id=%s", (id,))
                connection.commit()
                cursor.close()
                connection.close()

        # ---------- Form Tambah / Edit Pengeluaran ----------
        with st.expander("➕ Tambah / Edit Pengeluaran"):
            with st.form("form_pengeluaran", clear_on_submit=False):
                edit_mode = "pengeluaran" in st.session_state
                edit_data = st.session_state.get("pengeluaran", {})

                id_update = st.text_input("ID (Kosongkan jika input baru)", value=edit_data.get("id", "") if edit_mode else "")
                tanggal = st.date_input("Tanggal", value=pd.to_datetime(edit_data.get("tanggal", pd.to_datetime("today"))))
                keterangan = st.text_input("Keterangan", value=edit_data.get("keterangan", ""))
                
                options_kategori = ["Bibit", "Pupuk", "Tenaga Kerja", "Listrik", "Air", 
                "Sewa Lahan", "Pembajakan", "BBM", "ATK", "Internet", "Lainnya"]
                default_kategori = 0
                if edit_mode and edit_data.get("kategori") in options_kategori:
                    default_kategori = options_kategori.index(edit_data["kategori"])
                kategori = st.selectbox("Kategori", options=options_kategori, index=default_kategori)

                jumlah = st.number_input("Jumlah", min_value=1, value=int(edit_data.get("jumlah", 1)))

                options_satuan = ["Orang", "Bulan", "Pack","Hari", "Liter", "Botol", "Unit", "Lainnya"]
                default_satuan = 0
                if edit_mode and edit_data.get("satuan") in options_satuan:
                    default_satuan = options_satuan.index(edit_data["satuan"])
                satuan = st.selectbox("Satuan", options=options_satuan, index=default_satuan)

                harga_satuan = st.number_input("Harga Satuan", min_value=0.0, step=100.0, value=float(edit_data.get("harga_satuan", 0)))

                submitted = st.form_submit_button("Simpan Pengeluaran")

                if submitted:
                    if keterangan == "":
                        st.warning("Keterangan tidak boleh kosong.")
                    elif id_update == "":
                        insert_pengeluaran(tanggal, keterangan, kategori, jumlah, satuan, harga_satuan)
                        st.success("Pengeluaran berhasil ditambahkan.")
                    else:
                        update_pengeluaran(id_update, tanggal, keterangan, kategori, jumlah, satuan, harga_satuan)
                        st.success("Pengeluaran berhasil diperbarui.")
                    
                    st.session_state.pop("pengeluaran", None)
                    st.rerun()

        # ---------- Tabel Pengeluaran ----------
        st.subheader("")

        data = get_pengeluaran()
        if data:
            df = pd.DataFrame(data)

            total_harga = df["total_harga"].sum()
            total_row = {
                "id": "",
                "tanggal": "",
                "keterangan": "",
                "kategori": "",
                "jumlah": "",
                "satuan": "",
                "harga_satuan": "TOTAL",
                "total_harga": total_harga
            }
            df_total = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

            st.dataframe(df_total[["id", "tanggal", "keterangan", "kategori", "jumlah", "satuan", "harga_satuan", "total_harga"]], use_container_width=True)

            st.write("---")
            st.subheader("Aksi Edit & Hapus")
            for i, row in enumerate(data):
                col1, col2 = st.columns([1, 8])
                with col1:
                    if st.button(" Edit", key=f"pengeluaran_{i}"):
                        st.session_state["pengeluaran"] = row
                        st.rerun()
                with col2:
                    if st.button(" Hapus", key=f"delete_pengeluaran_{i}"):
                        delete_pengeluaran(row["id"])
                        st.success("Data pengeluaran berhasil dihapus.")
                        st.rerun()
        else:
            st.warning("Belum ada data pengeluaran.")


# ---------- PEMASUKAN ---------- #

    if selected == "Pemasukan":
        st.subheader("Pemasukan")

        # ---------- Fungsi Database ----------
        def get_pemasukan():
            connection = create_connection()
            if connection:
                cursor = connection.cursor(dictionary=True)
                cursor.execute(
                    "SELECT * FROM pemasukan WHERE user_email = %s ORDER BY tanggal DESC",
                    (st.session_state.user_email,)
                )
                result = cursor.fetchall()
                cursor.close()
                connection.close()
                return result

        def insert_pemasukan(tanggal, keterangan, kategori, jumlah, satuan, harga_satuan, total_harga):
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute(
                    "INSERT INTO pemasukan (tanggal, keterangan, kategori, jumlah, satuan, harga_satuan, total_harga, user_email) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (tanggal, keterangan, kategori, jumlah, satuan, harga_satuan, total_harga, st.session_state.user_email)
                )
                connection.commit()
                cursor.close()
                connection.close()

        def update_pemasukan(id, tanggal, keterangan, kategori, jumlah, satuan, harga_satuan, total_harga):
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute(
                    "UPDATE pemasukan SET tanggal=%s, keterangan=%s, kategori=%s, jumlah=%s, satuan=%s, harga_satuan=%s, total_harga=%s WHERE id=%s",
                    (tanggal, keterangan, kategori, jumlah, satuan, harga_satuan, total_harga, id)
                )
                connection.commit()
                cursor.close()
                connection.close()

        def delete_pemasukan(id):
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("DELETE FROM pemasukan WHERE id=%s", (id,))
                connection.commit()
                cursor.close()
                connection.close()

        # ---------- Form Tambah / Edit pemasukan ----------
        with st.expander("➕ Tambah / Edit Pemasukan"):
            with st.form("form_pemasukan", clear_on_submit=False):
                edit_mode = "edit_pemasukan" in st.session_state
                edit_data = st.session_state.get("edit_pemasukan", {})

                id_update = st.text_input("ID (Kosongkan jika input baru)", value=edit_data.get("id", "") if edit_mode else "")
                tanggal = st.date_input("Tanggal", value=pd.to_datetime(edit_data.get("tanggal", pd.to_datetime("today"))))
                keterangan = st.text_input("Keterangan", value=edit_data.get("keterangan", ""))
                # --- pemilihan kategori --- #
                kategori_options = ["Penjualan", "Pemasukan Lain", "Hibah", "Lainnya"]
                default_idx = kategori_options.index(edit_data.get("kategori")) if edit_data.get("kategori") in kategori_options else 0
                kategori = st.selectbox("Kategori", options=kategori_options, index=default_idx)

                
                satuan = st.selectbox("Satuan", options=["Kg", "Buah", "Unit", "Lainnya"], index=0 if edit_data.get("satuan", "Kg") == "Kg" else 3)
                jumlah = st.number_input("Jumlah", min_value=1, value=int(edit_data.get("jumlah", 1)))
                harga_satuan = st.number_input("Harga Satuan", min_value=0.0, value=float(edit_data.get("harga_satuan", 0.0)), format="%.2f")

                total_harga = jumlah * harga_satuan

                submitted = st.form_submit_button("Simpan Pemasukan")

                if submitted:
                    if keterangan == "":
                        st.warning("Keterangan tidak boleh kosong.")
                    else:
                        if id_update == "":
                            insert_pemasukan(tanggal, keterangan, kategori, jumlah, satuan, harga_satuan, total_harga)
                            st.success("Pemasukan berhasil ditambahkan.")
                        else:
                            update_pemasukan(id_update, tanggal, keterangan, kategori, jumlah, satuan, harga_satuan, total_harga)
                            st.success("Pemasukan berhasil diperbarui.")

                        st.session_state.pop("edit_pemasukan", None)
                        st.rerun()

        # ---------- TABEL PEMASUKAN ----------
        st.subheader("")

        data = get_pemasukan()
        if data:
            df = pd.DataFrame(data)

            total_semua = df["total_harga"].sum()

            total_row = {col: "" for col in df.columns}
            total_row["total_harga"] = total_semua
            total_row["keterangan"] = "TOTAL"

            df_total = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

            st.dataframe(df_total[[
                "id", "tanggal", "keterangan", "kategori", "satuan", "jumlah", "harga_satuan", "total_harga"
            ]], use_container_width=True)

            st.write("---")
            st.subheader("Aksi Edit & Hapus")
            for i, row in enumerate(data):
                col1, col2 = st.columns([1, 8])
                with col1:
                    if st.button(" Edit", key=f"edit_{i}"):
                        st.session_state["edit_pemasukan"] = row
                        st.rerun()
                with col2:
                    if st.button(" Hapus", key=f"delete_{i}"):
                        delete_pemasukan(row["id"])
                        st.success("Pemasukan berhasil dihapus.")
                        st.rerun()
        else:
            st.warning("Belum ada data pemasukan.")


# ---------- LABA RUGI ---------- #

    elif selected == "Laba Rugi":
        st.header("Laporan Laba / Rugi")

        # ---------- Tambahkan CSS Tabel Custom ----------
        st.markdown("""
            <style>
                table.custom-lr-table {
                    font-family: 'Poppins', sans-serif;
                    border-collapse: collapse;
                    width: 100%;
                    margin-top: 20px;
                    background-color: #F9F9F9;
                    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.05);
                    border-radius: 12px;
                    overflow: hidden;
                }

                table.custom-lr-table th, table.custom-lr-table td {
                    text-align: left;
                    padding: 12px 16px;
                    border-bottom: 1px solid #ddd;
                    font-size: 15px;
                }

                table.custom-lr-table th {
                    background-color: #E0F2F1;
                    color: #004D40;
                    font-weight: 600;
                }

                table.custom-lr-table td:last-child {
                    text-align: right;
                    font-weight: 500;
                }

                table.custom-lr-table tr:last-child td {
                    font-weight: bold;
                    background-color: #F1F8E9;
                }
            </style>
        """, unsafe_allow_html=True)

        # ---------- Fungsi Ambil Total ----------
        def get_total_pengeluaran():
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT SUM(total_harga) FROM pengeluaran WHERE user_email = %s", (st.session_state.user_email,))
                total = cursor.fetchone()[0]
                cursor.close()
                connection.close()
                return total if total else 0
            return 0

        def get_total_pemasukan():
            connection = create_connection()
            if connection:
                cursor = connection.cursor()
                cursor.execute("SELECT SUM(total_harga) FROM pemasukan WHERE user_email = %s", (st.session_state.user_email,))
                total = cursor.fetchone()[0]
                cursor.close()
                connection.close()
                return total if total else 0
            return 0

        # ---------- Hitung Laba / Rugi ----------
        total_pengeluaran = get_total_pengeluaran()
        total_pemasukan = get_total_pemasukan()
        laba_rugi = total_pemasukan - total_pengeluaran

        # ---------- Tampilkan Tabel Custom ----------
        html_table = f"""
        <table class="custom-lr-table">
            <thead>
                <tr>
                    <th>Keterangan</th>
                    <th>Total (Rp)</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>pengeluaran</td>
                    <td>{total_pengeluaran:,.2f}</td>
                </tr>
                <tr>
                    <td>pemasukan</td>
                    <td>{total_pemasukan:,.2f}</td>
                </tr>
                <tr>
                    <td><strong>{"Laba" if laba_rugi >= 0 else "Rugi"}</strong></td>
                    <td><strong>{abs(laba_rugi):,.2f}</strong></td>
                </tr>
            </tbody>
        </table>
        """

        st.markdown(html_table, unsafe_allow_html=True)

        # ---------- Notifikasi bawah tabel ----------
        if laba_rugi >= 0:
            st.success(f"Keuntungan bersih: Rp {laba_rugi:,.2f}")
        else:
            st.error(f"Kerugian bersih: Rp {abs(laba_rugi):,.2f}")

# ----------- LOGOUT ---------- #
    if selected == "Logout":
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.session_state.halaman = "Login"
        st.rerun()

        # ---------- TAMPILKAN HALAMAN ----------
def tampilkan_halaman():
    
    if st.session_state.halaman == "Login":
        halaman_login()
    elif st.session_state.halaman == "home":
        halaman_home()

# ---------- MAIN ----------
if __name__ == "__main__":
    create_table()

    halaman = st.session_state.get("halaman", "Login")

    if halaman == "Daftar":
        halaman_daftar()
    elif halaman == "Login":
        halaman_login()
    elif halaman == "home":
        halaman_home()