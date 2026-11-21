# Dashboard Pemantauan 7 Kebiasaan Anak Indonesia Hebat (7 KAIH)

[![Python Version](https://img.shields.io/badge/python-3.13%20%7C%203.15-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/streamlit-1.67-FF4B4B.svg)](https://streamlit.io/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Tests](https://img.shields.io/badge/tests-39%20passed-brightgreen.svg)](https://docs.pytest.org/)

**Aplikasi Evaluasi & Pengambilan Keputusan Pembiasaan Karakter Taruna**  
SMAN 2 Taruna Bhayangkara Jawa Timur — Tim VERTIKAL SMA 2026.

Repository resmi: [https://github.com/codeplyapp/Dashboard-Vertikal](https://github.com/codeplyapp/Dashboard-Vertikal)

---

## 📌 Ringkasan Eksekutif

Dashboard ini dirancang untuk mengubah data survei evaluasi berkala pelaksanaan **7 Kebiasaan Anak Indonesia Hebat (7 KAIH)** menjadi alat bantu keputusan yang nyata bagi pimpinan sekolah, guru pamong/pembina, dan pengelola asrama.

Seluruh visualisasi, KPI, matriks prioritas, dan rekomendasi dihitung secara dinamis dari **232 entri respons anonim** (mencakup 203 siswa unik dari Batalyon X, XI, dan XII) tanpa angka manual atau rekayasa (*Single Source of Truth*).

### 7 Kebiasaan yang Dipantau
1. **Bangun Pagi** — Kesiapan taruna menyambut agenda pagi
2. **Beribadah** — Ketertiban dan kekhusyukan ibadah harian
3. **Berolahraga** — Kebugaran dan keaktifan gerak fisik
4. **Makan Sehat & Bergizi** — Kecukupan asupan dan variasi makanan
5. **Gemar Belajar** — Kondusivitas waktu dan lingkungan belajar mandiri
6. **Bermasyarakat** — Rasa saling menghargai, kerja sama, dan solidaritas
7. **Tidur Cepat** — Kecukupan waktu istirahat malam menjelang kegiatan pagi

---

## ✨ Fitur Utama Dashboard

- **Filter Global & Interaktif**:
  - Filter Batalyon (Kelas X / XI / XII).
  - Filter Rentang Tanggal Pengisian (28 Oktober – 14 November 2026).
  - Filter Fokus Kebiasaan (Menyorot kebiasaan tertentu).
  - Tombol Reset Filter instan dengan ringkasan status filter aktif.
- **7 Tab Analisis Komprehensif**:
  1. **Ringkasan**: 4 KPI utama, 100% stacked bar distribusi respons, gauge Indeks 7KAIH (0–100), radar profil batalyon, dan matriks prioritas 4 kuadran.
  2. **Distribusi 7 KAIH**: Penelusuran instrumen pertanyaan, proporsi 4 skala likert (Hampir selalu, Sering, Jarang, Tidak Pernah).
  3. **Per Batalyon**: Heatmap persentase "perlu perhatian", grouped bar chart per batalyon, tabel pivot, dan identifikasi kelompok paling membutuhkan pembinaan.
  4. **Tren Waktu**: Grafik dinamika pengisian harian, garis kumulatif, serta rekapitulasi 4 gelombang pengisian (*waves*).
  5. **Tabel Data**: Rekapitulasi frekuensi absolut dan persentase, kartu verifikasi integritas data (*zero missing values*), dan tombol **Unduh CSV**.
  6. **Insight & Aksi**: Generator narasi dinamis berbasis data (kekuatan utama, prioritas pembinaan, kesenjangan batalyon) dan kartu rekomendasi tindak lanjut operasional.
  7. **Metodologi & Jejak Gemini**: Dokumentasi transparansi data, formula perhitungan, serta jejak 4 tahap kolaborasi bersama Google Gemini beserta verifikasi tim.

---

## 🏗️ Arsitektur & Prinsip Desain

Sistem dibangun dengan arsitektur terpisah (*Separation of Concerns*):
- **Domain Layer murni (`g7kaih/`)**: Logika agregasi, filter, dan perhitungan indeks dirancang sebagai *pure functions* tanpa ketergantungan pada runtime Streamlit, sehingga 100% dapat diuji secara otomatis via `pytest`.
- **Presentation Layer (`app.py` & `theme.py`)**: UI reaktif dengan desain profesional bertema navy & gold Taruna Bhayangkara, tipografi jelas, dan kontras warna yang memenuhi standar aksesibilitas WCAG AA.
- **Privacy by Design**: Data NIS, nama, dan identitas pribadi tidak pernah dimuat ke dalam aplikasi maupun repositori publik. Seluruh analisis menggunakan dataset anonim `data/responses_anon.json`.

---

## 🚀 Panduan Menjalankan Secara Lokal

### Prasyarat
- Python 3.13 atau 3.15
- Git

### Langkah Instalasi
1. **Clone repository**:
   ```bash
   git clone https://github.com/codeplyapp/Dashboard-Vertikal.git
   cd Dashboard-Vertikal
   ```

2. **Buat virtual environment & aktifkan**:
   - Di Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .\.venv\Scripts\Activate.ps1
     ```
   - Di Linux/macOS:
     ```bash
     python3 -m venv .venv
     source .venv/bin/activate
     ```

3. **Install dependensi**:
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt   # untuk testing & linter
   ```

4. **Jalankan aplikasi Streamlit**:
   ```bash
   streamlit run app.py
   ```
   Aplikasi akan terbuka otomatis di peramban pada alamat `http://localhost:8501`.

---

## 🧪 Pengujian & Penjaminan Mutu

Proyek ini dilengkapi dengan rangkaian pengujian unit otomatis dan *golden test* untuk memastikan keakuratan 100% agregat data:

```bash
# Jalankan seluruh unit test
pytest -v

# Jalankan linter dan pemeriksaan format
ruff check .
```

Seluruh 39 kasus uji mencakup:
- Integritas data dan validasi skema (`test_data.py`).
- Agregasi analitik, perhitungan indeks, dan matriks prioritas (`test_analytics.py`).
- Generator insight dinamis dan rekomendasi operasional (`test_insights.py`).
- Pemformatan angka dan tanggal berbahasa Indonesia (`test_formatting.py`).

---

## 🐳 Deployment via Docker (Opsional)

Jika ingin menjalankan aplikasi menggunakan kontainer Docker:

```bash
# Build image
docker build -t dashboard-7kaih .

# Jalankan kontainer
docker run -d -p 8501:8501 --name dashboard-7kaih dashboard-7kaih
```

---

## 👥 Tim Pengembang

**Tim VERTIKAL SMA 2026**  
SMAN 2 Taruna Bhayangkara Jawa Timur  
*Dashboard Pemantauan 7 Kebiasaan Anak Indonesia Hebat*
