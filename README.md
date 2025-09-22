# 🚀 Real-time Prediction with Flask-SocketIO

Project ini menggabungkan **backend Flask-SocketIO** untuk prediksi dan simulasi real-time dengan **frontend sederhana (HTML, CSS, JS)** yang langsung di-serve dari Flask.

---

## ⚙️ Setup & Instalasi

### 1. Clone repository

```bash
git clone https://github.com/yeheskielaji/Monitoring_jaringan_xgboost.git
cd repo-name/backend
```

### 2. Buat virtual environment (opsional tapi direkomendasikan)

```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Jalankan backend (Flask-SocketIO)

```bash
python run.py
```

Jika berhasil, server akan jalan di:

```
http://localhost:5000
```

---

## 🖥️ Cara Menggunakan

1. Buka browser ke [`http://localhost:5000`](http://localhost:5000) → akan menampilkan `index.html`.
2. Frontend otomatis connect ke backend via **WebSocket**.
3. Tersedia endpoint tambahan:

   * **HTTP**:

     * `POST /predict` → kirim data `{"row_index": 0}` untuk request prediksi sekali jalan.
   * **WebSocket Events**:

     * `start_simulation` → mulai simulasi real-time.
     * `stop_simulation` → stop simulasi.
     * `prediction` → event dari backend berisi hasil prediksi.

---

## 📜 Contoh `requirements.txt`

Pastikan file ini ada `requirements.txt`:

```
flask
flask-socketio
eventlet
```
