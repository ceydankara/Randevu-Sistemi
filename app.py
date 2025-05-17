from flask import Flask, request, jsonify, render_template
import pyodbc

app = Flask(__name__)

# SQL Server veritabanına bağlantı oluşturuluyor
conn = pyodbc.connect(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=localhost;"             # Veritabanı sunucusu (genellikle localhost)
    "DATABASE=RandevuDB;"           # Kullanılan veritabanı adı
    "Trusted_Connection=yes;"       # Windows kimlik doğrulaması kullanılıyor
)

@app.route('/')
def index():
    # Veritabanından tüm danışmanları al
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM Consultants")
    consultants = cursor.fetchall()

    # index.html dosyasını render et ve danışman verilerini şablona gönder
    return render_template('index.html', consultants=consultants)

@app.route('/api/appointment', methods=['POST'])
def add_appointment():
    # İstemciden gelen JSON verisi alınır
    data = request.json
    name = data.get('name')                
    date = data.get('date')                
    time = data.get('time')                
    consultant_id = data.get('consultantId')  

    # Gerekli tüm bilgiler sağlanmış mı kontrol etidilir
    if not all([name, date, time, consultant_id]):
        return jsonify({'error': 'Eksik bilgi'}), 400

    try:
        cursor = conn.cursor()

        # Aynı danışman için aynı tarih ve saatte başka bir randevu var mı kontrolu
        cursor.execute("""
            SELECT COUNT(*) FROM Appointments
            WHERE Date = ? AND Time = ? AND consultant_id = ?
        """, date, time, consultant_id)

        # Eğer varsa, kullanıcıya danışmanın bu saatte dolu olduğunu bildir
        if cursor.fetchone()[0] > 0:
            return jsonify({'error': 'Seçilen danışman bu saatte dolu.'}), 400

        # Eğer uygun ise, randevu bilgilerini veritabanına ekle
        cursor.execute("""
            INSERT INTO Appointments (FullName, Date, Time, consultant_id)
            VALUES (?, ?, ?, ?)
        """, name, date, time, consultant_id)
        conn.commit()  # Değişiklikleri kaydet

        return jsonify({'message': 'Randevu başarıyla oluşturuldu'}), 200

    except Exception as e:
        # Hata olması durumunda kullanıcıya bildirim gönder
        print("Veritabanı hatası:", e)
        return jsonify({'error': 'Veritabanı hatası'}), 500

@app.route('/api/available-times', methods=['POST'])
def available_times():
    # Kullanıcının seçtiği tarih ve danışmanı al
    data = request.json
    date = data.get('date')
    consultant_id = data.get('consultantId')

    # Çalışma saatleri 09.00 ile 17.00 arasında
    all_hours = [f"{h:02d}:00" for h in range(9, 18)]

    try:
        cursor = conn.cursor()

        # Seçilen danışmanın belirtilen tarihteki dolu saatlerini al
        cursor.execute("""
            SELECT Time FROM Appointments
            WHERE Date = ? AND consultant_id = ?
        """, date, consultant_id)

        # Dolu saatleri string olarak listele (örn: "14:00")
        taken_times = [row[0].strftime('%H:%M') for row in cursor.fetchall()]

        # Uygun saatleri bul: tüm saatlerden dolu saatleri çıkar
        available = [t for t in all_hours if t not in taken_times]

        # Uygun saatleri JSON olarak geri döndür
        return jsonify({'available_times': available})

    except Exception as e:
        # Hata durumunda mesaj döndür
        print("Saat hatası:", e)
        return jsonify({'error': 'Saatler alınamadı'}), 500

# Flask uygulamasını çalıştır 
if __name__ == '__main__':
    app.run(debug=True)



