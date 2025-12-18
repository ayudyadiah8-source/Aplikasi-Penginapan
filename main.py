# Import fungsi dari file db_config
from config.db_connect import get_connection

def jalan_program():
    try:
        # Panggil fungsi koneksi
        db = get_connection()
        cursor = db.cursor()

        # Contoh test koneksi
        cursor.execute("SELECT DATABASE();")
        record = cursor.fetchone()
        print(f"Berhasil terhubung ke database: {record[0]}")

    except Exception as e:
        print(f"Gagal konek: {e}")
    
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    jalan_program()