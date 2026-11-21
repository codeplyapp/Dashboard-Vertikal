# Draf Konten Presentasi Lomba (10 Slide)

Dokumen ini memuat draf naskah dan panduan konten yang disesuaikan langsung dengan template presentasi kompetisi (`19 11 2026.pptx`). Tim dapat langsung menyalin teks dan menyisipkan tangkapan layar yang telah tersedia di `docs/screenshots/`.

---

## SLIDE 01 — IDENTITAS TIM & DASHBOARD UTAMA
**Subjudul:** Lengkapi identitas tim dan tempelkan tangkapan layar dashboard utama.

- **Nama Tim:** VERTIKAL SMA 2026
- **Asal Sekolah:** SMAN 2 Taruna Bhayangkara Jawa Timur
- **Kabupaten/Kota:** Kab. Banyuwangi, Jawa Timur
- **Judul Karya:** Dashboard Pemantauan 7 Kebiasaan Anak Indonesia Hebat (7 KAIH)
- **Visual:** Tangkapan layar desktop overview (`docs/screenshots/desktop-1440.png`).

---

## SLIDE 02 — RUBRIK PENILAIAN
*(Slide pengantar rubrik lomba: 01 Analisis Data 25%, 02 Kualitas Dashboard 25%, 03 Pemanfaatan Gemini 25%, 04 Kreativitas & Inovasi 25%)*

---

## SLIDE 03 — ANALISIS DATA
**Subjudul:** Jelaskan insight berbasis data, bukan hanya menampilkan visualisasi.

### 1. Temuan Data
- **Cakupan Pengukuran:** 232 entri respons anonim dari 203 siswa unik (Kelas X: 138 entri, Kelas XI: 47 entri, Kelas XII: 47 entri) sepanjang 28 Oktober – 14 November 2026.
- **Kekuatan Utama Sekolah:** Kebiasaan **Beribadah** mencatat tingkat respons positif tertinggi sebesar **92,67%** (215 dari 232 entri menjawab *Hampir selalu* atau *Sering*), diikuti oleh **Berolahraga** (**91,38%** / 212 entri). Ini membuktikan pembiasaan religius dan kedisiplinan fisik di asrama telah mengakar kuat.
- **Titik Perhatian Kritis:** Kebiasaan **Tidur Cepat** memiliki proporsi *"perlu perhatian"* (*Jarang* + *Tidak Pernah*) tertinggi sebesar **25,86%** (60 dari 232 entri), diikuti oleh **Makan Sehat & Bergizi** sebesar **18,97%** (44 entri).

### 2. Pola dan Tren
- **Dinamika 4 Gelombang Pengisian:**
  - Gelombang 1 (5 Nov): 24 entri (10,3%).
  - Gelombang 2 (8–9 Nov): 47 entri (20,3%).
  - Gelombang 3 (11 Nov): **108 entri (46,6%)** — puncak pengisian massal pasca-evaluasi tengah periode.
  - Gelombang 4 (13–14 Nov): 50 entri (21,6%).
- **Kesenjangan Antarbatalyon:**
  - Pada kebiasaan *Tidur Cepat*, **Kelas XI** mengalami kendala istirahat tertinggi dengan **34,04%** respons perlu perhatian (16 dari 47 entri), disusul Kelas X (25,36%) dan Kelas XII (19,15%). Kesenjangan mencapai **14,9 poin persentase**.
  - Pada kebiasaan *Makan Sehat & Bergizi*, **Kelas X** mencatat perhatian tertinggi (**21,01%**), menunjukkan fase adaptasi menu dan pola makan asrama bagi taruna tingkat awal.

### 3. Kesimpulan Utama
Secara umum, indeks ketercapaian 7 KAIH mencapai **81,7 dari skala 100**. Pembiasaan ibadah, olahraga, dan sosial sudah melampaui target, namun sekolah dan asrama mendesak perlu mengintervensi **manajemen waktu kegiatan malam (istirahat/tidur)** dan **variasi gizi konsumsi**, terutama pada taruna Kelas XI dan Kelas X.

---

## SLIDE 04 — KUALITAS DASHBOARD
**Subjudul:** Jelaskan tampilan, fungsi, dan manfaat dashboard yang telah dibuat.

### 1. Preview Dashboard
*(Sisipkan `docs/screenshots/desktop-1440.png`, `docs/screenshots/tablet-1024.png`, dan `docs/screenshots/mobile-390.png`)*

### 2. Tautan Dashboard & Repositori
- **URL Dashboard Publik:** *(Tempelkan URL Streamlit Community Cloud setelah dideploy)*
- **Repository GitHub:** `https://github.com/codeplyapp/Dashboard-Vertikal`

### 3. Desain & Fungsi Unggulan
- **Single Source of Truth:** Semua metrik dihitung secara dinamis dari dataset anonim. Zero hard-coded values.
- **Filter Global Reaktif:** Pengguna dapat memilah data menurut Batalyon (X, XI, XII), rentang tanggal pengisian, atau fokus pada kebiasaan spesifik secara instan.
- **Visualisasi Multidimensi:**
  - *100% Stacked Bar* untuk proporsi 4 skala instrumen.
  - *Heatmap Matriks Batalyon* & *Grouped Bar* untuk perbandingan lintas angkatan.
  - *Priority Matrix (4 Kuadran)* memetakan kebiasaan yang butuh aksi segera vs dipertahankan.
  - *Radar Profil Batalyon* untuk membandingkan indeks karakter holistik.
- **Aksesibilitas & Kredibilitas:** Skema warna Navy & Gold Taruna Bhayangkara dengan rasio kontras WCAG AA, fitur unduh CSV data terfilter, dan kartu verifikasi integritas data (*zero missing values*).

---

## SLIDE 05 — PEMANFAATAN GEMINI: TAHAP 1
**Tahap 1: Merancang Instrumen & Struktur Data**

- **Aktivitas:** Menyusun struktur 7 pertanyaan instrumen 7 KAIH berbasis skala Likert 4 titik dan mendesain taksonomi data.
- **Prompt yang Digunakan:**
  > *"Bantu kami merumuskan indikator operasional untuk 7 Kebiasaan Anak Indonesia Hebat (Bangun Pagi, Beribadah, Berolahraga, Makan Sehat, Gemar Belajar, Bermasyarakat, Tidur Cepat) dalam format evaluasi diri taruna asrama dengan 4 pilihan skala (Hampir selalu, Sering, Jarang, Tidak Pernah)."*
- **Bukti Hasil Gemini:** Rekomendasi rumusan instrumen dengan skala 4 titik seimbang yang menghindari kecenderungan jawaban netral.
- **Peran Gemini & Kontribusi Tim:**
  - *Peran Gemini:* Menyediakan draf pertanyaan terstruktur dan format kuantifikasi skala 1–4.
  - *Kontribusi Tim:* Mengadaptasi bahasa pertanyaan agar relevan dengan budaya khas kehidupan taruna Bhayangkara dan memastikan tidak ada pertanyaan yang membingungkan.

---

## SLIDE 06 — PEMANFAATAN GEMINI: TAHAP 2
**Tahap 2: Audit Kualitas Data & Desain Privasi (Privacy by Design)**

- **Aktivitas:** Membaca ekspor lembar respons mentah, validasi inkonsistensi, dan pembentukan dataset anonim.
- **Prompt yang Digunakan:**
  > *"Tuliskan script Python untuk memvalidasi ekspor respons survei (232 baris), mendeteksi nilai kosong/duplikat, memetakan teks jawaban ke skala 1-4, serta mengekstrak dataset anonim tanpa menyertakan NIS atau data pribadi siswa."*
- **Bukti Hasil Gemini:** Modul pembersih data (`scripts/build_data.py`) yang menghasilkan `data/responses_anon.json` dan `meta.json` dengan verifikasi SHA-256.
- **Peran Gemini & Kontribusi Tim:**
  - *Peran Gemini:* Menghasilkan script otomasi validasi skema data dan kalkulasi hash checksum.
  - *Kontribusi Tim:* Memverifikasi kecocokan jumlah entri per batalyon (138/47/47) dan memastikan file sumber beridentitas siswa masuk `.gitignore`.

---

## SLIDE 07 — PEMANFAATAN GEMINI: TAHAP 3
**Tahap 3: Pemodelan Analitik & Rekayasa Formula (Analytics Engine)**

- **Aktivitas:** Merancang formula Indeks 7KAIH (skala 0–100), Priority Matrix 4-kuadran, dan generator insight dinamis.
- **Prompt yang Digunakan:**
  > *"Bagaimana cara menghitung indeks terstandarisasi 0-100 dari rata-rata skala Likert 1-4? Buat fungsi Python murni untuk mengelompokkan kategori positif (skor 3-4) vs perlu perhatian (skor 1-2) serta menentukan kuadran prioritas pembinaan."*
- **Bukti Hasil Gemini:** Logika formula `(mean_score - 1) / 3 * 100` dan algoritma pembagi kuadran matriks prioritas.
- **Peran Gemini & Kontribusi Tim:**
  - *Peran Gemini:* Mengembangkan kode fungsi analisis murni (`g7kaih/analytics.py` dan `g7kaih/insights.py`).
  - *Kontribusi Tim:* Menulis 39 unit test otomatis (`pytest`) untuk menjamin 0 kesalahan hitung (*zero mathematical discrepancy*).

---

## SLIDE 08 — PEMANFAATAN GEMINI: TAHAP 4
**Tahap 4: Pengembangan Dashboard UI & Visualisasi Interaktif**

- **Aktivitas:** Mengembangkan aplikasi Streamlit modular dengan Plotly charts dan styling CSS kustom.
- **Prompt yang Digunakan:**
  > *"Rancang antarmuka Streamlit multi-tab yang memadukan Plotly charts (100% stacked bar, heatmap, radar chart) dengan palet warna resmi Taruna Bhayangkara (Navy #0B2545 & Gold #C9A227) serta kartu KPI HTML yang responsif."*
- **Bukti Hasil Gemini:** Kerangka arsitektur UI modular (`app.py`, `charts.py`, `theme.py`, `assets/styles.css`).
- **Peran Gemini & Kontribusi Tim:**
  - *Peran Gemini:* Memberikan boilerplate antarmuka Streamlit, konfigurasi Plotly, dan CSS custom.
  - *Kontribusi Tim:* Melakukan pengujian responsivitas pada 3 breakpoint (Desktop 1440px, Tablet 1024px, Mobile 390px) serta memastikan alur interaksi filter bebas bug.

---

## SLIDE 09 — KREATIVITAS & INOVASI
**Subjudul:** Jelaskan hal yang membedakan dashboard tim dan nilai tambahnya bagi sekolah.

### 1. Apa yang Membuat Dashboard Kami Istimewa?
- **Matriks Prioritas Aksi 4 Kuadran (Actionable Priority Matrix):** Alih-alih hanya menampilkan grafik batang sederhana, dashboard kami memetakan setiap kebiasaan ke dalam kuadran: *Prioritas Tinggi*, *Pertahankan*, *Pantau*, dan *Waspada*. Hal ini langsung menjawab pertanyaan: *"Apa yang harus dibina hari ini?"*
- **Generator Narasi & Rekomendasi Dinamis:** Fitur cerdas yang otomatis menuliskan temuan dan rekomendasi terukur mengikuti filter yang dipilih pengguna. Jika pembina memfilter "Kelas XI", narasi otomatis menyesuaikan angka spesifik Kelas XI.
- **Arsitektur Modular Teruji (39 Unit Test & Ruff Linter):** Mengadopsi standar rekayasa perangkat lunak profesional dengan memisahkan logika matematika murni dari antarmuka visual.

### 2. Mengapa Sangat Bermanfaat bagi Sekolah?
- **Pengambilan Keputusan Berbasis Bukti:** Pengasuh asrama tidak lagi mengira-ngira masalah siswa, melainkan memiliki bukti konkret bahwa 34% taruna Kelas XI mengalami kendala tidur cepat.
- **Diferensiasi Pembinaan Antar-Angkatan:** Sekolah dapat memberikan perlakuan berbeda: Kelas X difokuskan pada penyesuaian gizi dan jam makan, sedangkan Kelas XI difokuskan pada evaluasi beban tugas malam.
- **Alat Pantau Berkelanjutan:** Dashboard dapat dipakai secara berkelanjutan untuk survei gelombang berikutnya guna mengukur efektivitas program perbaikan.

---

## SLIDE 10 — APA YANG DAPAT DILAKUKAN SEKOLAH?
**Subjudul:** Rumuskan aksi nyata yang dapat dilakukan sekolah berdasarkan temuan dashboard.

### 1. Temuan Data
- **Masalah 1 (Tidur Cepat):** 25,86% taruna (60 entri) melaporkan jarang/tidak pernah cukup istirahat saat bangun. Pada Kelas XI, angka ini melonjak hingga 34,04%.
- **Masalah 2 (Makan Sehat & Bergizi):** 18,97% taruna (44 entri) melaporkan kurangnya pemenuhan variasi dan kepuasan makan bergizi, dengan konsentrasi tertinggi di Kelas X (21,01%).
- **Masalah 3 (Gemar Belajar Malam):** 14,22% taruna merasa suasana belajar mandiri malam hari belum sepenuhnya kondusif.

### 2. Ide Aksi / Solusi Nyata Sekolah
1. **Program "Lights Out & Silent Hour" Terjadwal:**
   - *Aksi:* Batasi kegiatan kurikuler/tugas malam maksimal pukul 21.30 WIB untuk memberi jeda rileks minimal 45 menit sebelum jam tidur asrama pukul 22.15 WIB.
   - *Target:* Menurunkan respons "perlu perhatian" tidur cepat dari 25,8% ke bawah 15% pada evaluasi berikutnya.
2. **Evaluasi Siklus Menu Gizi Asrama bersama Tim Gizi:**
   - *Aksi:* Meninjau rotasi menu berkala, porsi protein seimbang, dan ketersediaan buah segar, terutama pada asrama taruna Kelas X yang sedang berada di fase penyesuaian fisik.
   - *Target:* Meningkatkan kepuasan makan sehat hingga di atas 85% respons positif.
3. **Pemberdayaan Taruna Tutor Sebaya (Peer Mentoring):**
   - *Aksi:* Memanfaatkan tingginya rasa solidaritas (*Bermasyarakat: 87,93% positif*) dengan membentuk kelompok belajar sebaya di asrama untuk membantu taruna yang kesulitan akademik agar tidak perlu begadang laris larut malam.
