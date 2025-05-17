from flask import Flask, request, jsonify, render_template
import pyodbc

# Flask uygulamasını başlat
app = Flask(__name__)

# SQL Server veritabanı bağlantısı
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"  # Sunucu adı
    "DATABASE=RandevuDB;"  # Veritabanı adı
    "Trusted_Connection=yes;"  # Windows kimlik doğrulaması
)

# Ana sayfa endpoint'i
@app.route('/')
def index():
    cursor = conn.cursor()
    # Danışmanları veritabanından çek
    cursor.execute("SELECT id, name FROM Consultants")
    consultants = cursor.fetchall()
    # index.html şablonunu danışman verileri ile render et
    return render_template('index.html', consultants=consultants)

# Randevu ekleme endpoint'i
@app.route('/api/appointment', methods=['POST'])
def add_appointment():
    data = request.json
    name = data.get('name')
    date = data.get('date')
    time = data.get('time')
    consultant_id = data.get('consultantId')

    # Tüm alanlar dolu mu kontrol et
    if not all([name, date, time, consultant_id]):
        return jsonify({'error': 'Eksik bilgi'}), 400

    try:
        cursor = conn.cursor()

        # Seçilen danışman, tarih ve saatte zaten randevulu mu kontrol et
        cursor.execute("""
            SELECT COUNT(*) FROM Appointments
            WHERE Date = ? AND Time = ? AND consultant_id = ?
        """, date, time, consultant_id)

        # Eğer randevu varsa hata döndür
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'Seçilen danışman bu saatte dolu.'}), 400

        # Randevuyu veritabanına ekle
        cursor.execute("""
            INSERT INTO Appointments (FullName, Date, Time, consultant_id)
            VALUES (?, ?, ?, ?)
        """, name, date, time, consultant_id)
        conn.commit()  # Değişiklikleri kaydet

        return jsonify({'message': 'Randevu başarıyla oluşturuldu'}), 200

    except Exception as e:
        print("Veritabanı hatası:", e)
        return jsonify({'error': 'Veritabanı hatası'}), 500

# Uygun saatleri getiren endpoint
@app.route('/api/available-times', methods=['POST'])
def available_times():
    data = request.json
    date = data.get('date')
    consultant_id = data.get('consultantId')

    # Günlük tüm saat aralıklarını oluştur (09:00 - 17:00)
    all_hours = [f"{h:02d}:00" for h in range(9, 18)]

    try:
        cursor = conn.cursor()

        # Belirtilen danışmanın, belirtilen gündeki dolu saatlerini al
        cursor.execute("""
            SELECT Time FROM Appointments
            WHERE Date = ? AND consultant_id = ?
        """, date, consultant_id)

        # Veritabanından gelen zamanları uygun formata çevir (HH:MM)
        taken_times = [row[0].strftime('%H:%M') for row in cursor.fetchall()]

        # Tüm saatlerden dolu olanları çıkararak boş saatleri bul
        available = [t for t in all_hours if t not in taken_times]

        return jsonify({'available_times': available})
    except Exception as e:
        print("Saat hatası:", e)
        return jsonify({'error': 'Saatler alınamadı'}), 500

# Flask uygulamasını çalıştır
if __name__ == '__main__':
    app.run(debug=True)

