# PRD — Dashboard Pemantauan 7 Kebiasaan Anak Indonesia Hebat (7 KAIH)

**Produk:** Dashboard evaluasi kualitas pelaksanaan 7 KAIH
**Sekolah:** SMAN 2 Taruna Bhayangkara Jawa Timur
**Dokumen:** Product Requirements Document (PRD)
**Versi:** 1.0
**Tanggal:** 21 November 2026
**Status:** Disetujui untuk implementasi
**Pemilik Produk:** Tim VERTIKAL SMA 2026
**Dokumen terkait:** [`TSD.md`](./TSD.md), [`ARCHITECTURE.md`](./ARCHITECTURE.md), [`slide-content.md`](./slide-content.md)

---

## 1. Ringkasan Eksekutif

Dashboard ini mengubah hasil survei 7 Kebiasaan Anak Indonesia Hebat (7 KAIH) menjadi alat bantu keputusan bagi sekolah dan asrama. Data mentah berupa 232 entri formulir dari tiga batalyon diolah menjadi indikator ketercapaian, perbandingan antarbatalyon, tren waktu pengisian, serta rekomendasi tindak lanjut yang dapat langsung dieksekusi.

Produk dibangun dengan **Python 3.13 + Streamlit + pandas + Plotly**, dipublikasikan sebagai aplikasi web publik sehingga dapat dibuka juri, guru pendamping, dan pengelola asrama tanpa instalasi.

**Nilai inti:** satu sumber kebenaran angka (single source of truth) — seluruh visual dan narasi dihitung ulang dari dataset mentah yang sama, tanpa angka manual.

---

## 2. Latar Belakang & Masalah

### 2.1 Konteks
Program 7 KAIH menargetkan pembiasaan: bangun pagi, beribadah, berolahraga, makan sehat dan bergizi, gemar belajar, bermasyarakat, serta tidur cepat. Sekolah telah mengumpulkan data evaluasi melalui Google Form, tetapi hasilnya masih berupa tabel respons mentah.

### 2.2 Masalah yang Diselesaikan

| # | Masalah | Dampak |
|---|---|---|
| M1 | Data 232 baris tersebar dalam skala kategorikal dan tidak teragregasi | Guru sulit melihat prioritas pembinaan |
| M2 | Tidak ada perbandingan kondisi antarbatalyon (X, XI, XII) | Intervensi cenderung seragam, tidak tepat sasaran |
| M3 | Tidak ada gambaran dinamika pengisian per tanggal/gelombang | Tren dan konsistensi pemantauan tidak terbaca |
| M4 | Rekomendasi masih berupa opini, bukan turunan data | Tindak lanjut sulit dipertanggungjawabkan |
| M5 | Kebutuhan dokumentasi kompetisi (rubrik 4 × 25%) | Diperlukan bukti analisis, kualitas dashboard, pemanfaatan Gemini, dan inovasi |

### 2.3 Peluang
Dengan satu dashboard interaktif, sekolah dapat mengidentifikasi kebiasaan prioritas (mis. kecukupan tidur) dan batalyon dengan kebutuhan pembinaan tertinggi dalam hitungan detik, lalu memverifikasi angkanya langsung pada tabel data.

---

## 3. Tujuan & Metrik Keberhasilan

### 3.1 Tujuan Produk
1. Menyajikan kondisi 7 KAIH secara akurat, ringkas, dan dapat difilter.
2. Menunjukkan prioritas pembinaan berbasis bukti (persentase respons perlu perhatian).
3. Menyediakan rekomendasi tindak lanjut yang terhubung langsung ke temuan.
4. Memenuhi seluruh komponen rubrik penilaian lomba.

### 3.2 Metrik Keberhasilan (Product KPIs)

| Kode | Metrik | Target | Cara Ukur |
|---|---|---|---|
| K1 | Akurasi angka | 100% cocok dengan tabel referensi | Uji otomatis `tests/test_aggregates.py` |
| K2 | Waktu menemukan kebiasaan prioritas | ≤ 10 detik sejak halaman dibuka | Uji kegunaan 3 pengguna |
| K3 | Kelengkapan blok dashboard | 5/5 blok (A–E) tersedia | Checklist rilis |
| K4 | Aksesibilitas tautan | 200 OK tanpa login, desktop & mobile | Uji incognito + Playwright |
| K5 | Kesesuaian rubrik | 4/4 aspek terpenuhi | Review guru pendamping |
| K6 | Privasi | 0 kemunculan NIS/nama di UI & repo | Pemindaian string |

---

## 4. Pengguna & Persona

| Persona | Kebutuhan Utama | Cara Menggunakan |
|---|---|---|
| **Guru pendamping / pembina** | Prioritas pembinaan per kebiasaan dan per batalyon | Membuka tab Ringkasan & Per Batalyon, membaca panel Insight |
| **Pengelola asrama** | Bukti untuk evaluasi jadwal tidur, konsumsi, dan kegiatan malam | Filter Batalyon + kebiasaan Tidur/Makan |
| **Kepala sekolah / juri** | Ringkasan eksekutif yang kredibel dan dapat diverifikasi | KPI, tabel rekapitulasi, tab Metodologi |
| **Tim penyusun** | Alat dokumentasi proses dan pemanfaatan Gemini | Tab Metodologi & Jejak Gemini, ekspor CSV |

---

## 5. Ruang Lingkup

### 5.1 In Scope
- Dashboard web Streamlit dengan filter global: Batalyon, rentang tanggal, fokus kebiasaan.
- KPI ringkasan cakupan pengukuran.
- Visualisasi distribusi 4 skala untuk 7 kebiasaan.
- Perbandingan antarbatalyon (heatmap + grouped bar).
- Tren jumlah respons per tanggal dan penanda gelombang pengisian.
- Tabel rekapitulasi absolut + persentase, ekspor CSV.
- Panel insight dan rekomendasi dinamis mengikuti filter.
- Fitur analitis lanjutan: Indeks 7KAIH, Priority Matrix, radar profil batalyon.
- Tab Metodologi & Jejak Gemini.
- Publikasi publik (Streamlit Community Cloud) dan dokumentasi pengumpulan.

### 5.2 Out of Scope
- Input/edit data langsung dari dashboard (data berasal dari ekspor formulir).
- Identifikasi individu, pencarian NIS, atau pelacakan per siswa.
- Autentikasi/otorisasi pengguna.
- Prediksi statistik inferensial (uji signifikansi, model prediktif).
- Integrasi API sekolah/SIS.

### 5.3 Batasan
- Dataset tidak memiliki ID unik pada file utama; satuan analisis adalah **entri**, bukan siswa.
- Statistik **203 siswa unik** hanya disajikan sebagai angka agregat, dihitung offline dari file berkode; kode tidak pernah dipublikasikan.
- Data hanya mencakup 28 Oktober–14 November 2026 dengan 9 tanggal pengisian.

---

## 6. Sumber Data & Definisi

### 6.1 Sumber
- `DATA EVALUASI G7KAIH SMAN 2 TARUNA BHAYANGKARA JAWA TIMUR.xlsx`, sheet `Form Responses 1` — 232 baris valid, 9 kolom, tanpa nilai kosong/duplikat.
- `Evaluasi Pelaksanaan Kualitas G7KAIH ... (Responses).xlsx` — hanya untuk menghitung jumlah siswa unik (203).
- `19 11 2026.pptx` — template pengumpulan karya (10 slide).

### 6.2 Skala Jawaban → Skor

| Label | Skor | Makna |
|---|---|---|
| Hampir selalu | 4 | Terpenuhi hampir setiap hari |
| Sering | 3 | Terpenuhi sebagian besar waktu |
| Jarang | 2 | Terpenuhi sesekali |
| Tidak Pernah | 1 | Tidak terpenuhi |

**Positif** = Hampir selalu + Sering. **Perlu Perhatian** = Jarang + Tidak Pernah.

### 6.3 Tujuh Kebiasaan & Kode

| Kode | Kebiasaan | Fokus pertanyaan |
|---|---|---|
| `bangun_pagi` | Bangun Pagi | Kesiapan mengikuti kegiatan pagi |
| `ibadah` | Beribadah | Ketertiban & kekhusyukan ibadah |
| `olahraga` | Berolahraga | Kesempatan bergerak aktif |
| `makan_sehat` | Makan Sehat & Bergizi | Kecukupan & variasi makanan |
| `gemar_belajar` | Gemar Belajar | Waktu & lingkungan belajar |
| `bermasyarakat` | Bermasyarakat | Dihargai & kerja sama |
| `tidur_cepat` | Tidur Cepat | Kecukupan istirahat saat bangun |

### 6.4 Batalyon

| Kode | Nama |
|---|---|
| `X` | Batalyon Bhara Abyakta Radhika (Kelas X) |
| `XI` | Batalyon Bhara Mada Wiradharma (Kelas XI) |
| `XII` | Batalyon Bhara Arsa Nawasena (Kelas XII) |

### 6.5 Angka Referensi Wajib (N = 232)

| Kebiasaan | HS | S | J | TP | Positif | Perlu Perhatian |
|---|---|---|---|---|---|---|
| Bangun Pagi | 85 | 117 | 29 | 1 | 202 (87,07%) | 30 (12,93%) |
| Beribadah | 129 | 86 | 16 | 1 | 215 (92,67%) | 17 (7,33%) |
| Berolahraga | 98 | 114 | 19 | 1 | 212 (91,38%) | 20 (8,62%) |
| Makan Sehat & Bergizi | 83 | 105 | 42 | 2 | 188 (81,03%) | 44 (18,97%) |
| Gemar Belajar | 62 | 137 | 31 | 2 | 199 (85,78%) | 33 (14,22%) |
| Bermasyarakat | 96 | 108 | 28 | 0 | 204 (87,93%) | 28 (12,07%) |
| Tidur Cepat | 82 | 90 | 50 | 10 | 172 (74,14%) | 60 (25,86%) |

---

## 7. Kebutuhan Fungsional

Prioritas memakai MoSCoW. Setiap kebutuhan memiliki kriteria penerimaan yang dapat diuji.

### FR-01 — Filter Global (Must)
Pengguna dapat memfilter seluruh dashboard berdasarkan:
- Batalyon (multi-pilih: X, XI, XII; default semua),
- rentang tanggal pengisian (28 Okt–14 Nov 2026; default semua),
- fokus kebiasaan (7 pilihan + "Semua").

**Kriteria penerimaan**
- Perubahan filter memperbarui KPI, semua grafik, tabel, dan narasi dalam ≤ 2 detik.
- Kombinasi filter tanpa data menampilkan empty state informatif, bukan error.
- Filter aktif ditampilkan sebagai ringkasan ("Menampilkan n entri · Batalyon: …").

### FR-02 — KPI Ringkasan (Must)
Menampilkan: total entri, sebaran per batalyon, kebiasaan dengan persentase positif tertinggi, kebiasaan dengan perlu perhatian tertinggi, dan jumlah siswa unik (203, statis, berlabel).

**Kriteria penerimaan**
- Nilai dihitung dari data terfilter; label satuan "entri" digunakan konsisten.
- Angka default identik dengan §6.5.

### FR-03 — Distribusi 4 Skala per Kebiasaan (Must)
100% stacked horizontal bar untuk 7 kebiasaan dengan warna konsisten dan label persentase.

**Kriteria penerimaan**
- Total tiap bar = 100%; jumlah absolut tersedia pada tooltip/tabel.
- Urutan skala selalu HS → S → J → TP.

### FR-04 — Perbandingan Antarbatalyon (Must)
Heatmap dan/atau grouped bar persentase "Perlu Perhatian" per kebiasaan × batalyon.

**Kriteria penerimaan**
- Sel menampilkan persentase dan jumlah absolut (n).
- Batalyon dengan nilai tertinggi ditandai jelas secara tekstual (bukan hanya warna).

### FR-05 — Tren Waktu (Must)
Combo chart jumlah entri per tanggal (batang) + garis kumulatif atau indeks positif, dengan penanda 4 gelombang: 5 Nov, 8–9 Nov, 11 Nov, 13 Nov.

**Kriteria penerimaan**
- 9 tanggal tampil berurutan; total batang = total entri terfilter.
- Tanggal tanpa data tidak menimbulkan garis putus yang menyesatkan.

### FR-06 — Tabel Rekapitulasi (Must)
Tabel absolut + persentase per kebiasaan dan per batalyon, dapat diurutkan dan diunduh CSV.

**Kriteria penerimaan**
- CSV memuat data terfilter dengan header yang jelas dan encoding UTF-8.
- Angka tabel = angka grafik pada filter yang sama.

### FR-07 — Insight & Rekomendasi Dinamis (Must)
Panel berisi temuan otomatis (tertinggi/terendah, kesenjangan antarbatalyon) dan rekomendasi yang dipetakan ke kebiasaan prioritas.

**Kriteria penerimaan**
- Minimal 3 temuan dan 3 rekomendasi pada filter default.
- Setiap temuan menyertakan angka dan satuan.
- Rekomendasi tidak menyebut individu dan tidak mengarang data.

### FR-08 — Indeks 7KAIH (Should)
Skor 0–100 dari rata-rata skor 1–4 yang dinormalisasi: `(mean − 1) / 3 × 100`.

**Kriteria penerimaan**
- Ditampilkan per kebiasaan dan keseluruhan; rumus dijelaskan di tab Metodologi.
- Nilai default dapat direproduksi manual dari tabel.

### FR-09 — Priority Matrix (Should)
Scatter: sumbu X = persentase positif, sumbu Y = persentase perlu perhatian, ukuran = jumlah entri; kuadran diberi label.

**Kriteria penerimaan**
- Setiap titik berlabel nama kebiasaan.
- Kuadran "prioritas tinggi" = positif rendah & perlu perhatian tinggi.

### FR-10 — Profil Radar Batalyon (Should)
Radar 7 sumbu membandingkan indeks 7KAIH antarbatalyon pada filter aktif.

**Kriteria penerimaan**
- Legenda jelas; skala 0–100; batalyon yang difilter saja yang tampil.

### FR-11 — Tab Metodologi & Jejak Gemini (Must)
Menjelaskan sumber data, pemetaan skor, rumus, batasan, serta log prompt Gemini dan peran verifikasi tim.

**Kriteria penerimaan**
- Menyebut 232 entri, 203 siswa unik, dan alasan penggunaan satuan entri.
- Tidak memuat NIS/nama.

### FR-12 — Mode Laporan/Cetak (Could)
Tombol untuk menyembunyikan kontrol dan menata layout agar layak dicetak/PDF.

### FR-13 — Ekspor Data (Must)
Unduh CSV rekapitulasi terfilter; opsional unduh ringkasan JSON.

### FR-14 — Akses Publik (Must)
Aplikasi dapat dibuka tanpa login melalui tautan publik.

---

## 8. Kebutuhan Non-Fungsional

| Kode | Kategori | Ketentuan |
|---|---|---|
| NFR-01 | Akurasi | 0 selisih terhadap tabel referensi; diuji otomatis |
| NFR-02 | Performa | Waktu muat awal ≤ 5 detik; interaksi filter ≤ 2 detik pada 232 baris |
| NFR-03 | Keandalan | Tidak ada crash pada kombinasi filter kosong; empty state ramah |
| NFR-04 | Privasi | Tanpa NIS/nama; file berkode tidak masuk repositori publik |
| NFR-05 | Aksesibilitas | Kontras WCAG AA; informasi tidak bergantung pada warna saja; navigasi keyboard Streamlit |
| NFR-06 | Responsif | Layout terbaca pada 1440, 1024, dan 390 px |
| NFR-07 | Maintainability | Tipe anotasi, docstring, lint Ruff, modul terpisah, unit test |
| NFR-08 | Portabilitas | Berjalan di Python 3.13 (Streamlit Cloud) dan 3.15 (lokal) |
| NFR-09 | Transparansi | Semua rumus dan sumber data dapat ditelusuri di UI/dokumen |
| NFR-10 | Bahasa | Seluruh UI berbahasa Indonesia; angka format Indonesia (koma desimal) |

---

## 9. Alur Pengguna Utama

1. Pengguna membuka tautan → melihat judul, cakupan data, dan KPI default.
2. Pengguna memilih batalyon (mis. XI) → KPI, grafik, tabel, dan narasi berubah.
3. Pengguna membuka tab "Per Batalyon" → melihat Tidur Cepat sebagai prioritas tertinggi.
4. Pengguna membuka "Insight & Aksi" → membaca temuan + rekomendasi operasional.
5. Pengguna memverifikasi angka di "Tabel Data" → mengunduh CSV.
6. Juri membuka "Metodologi & Jejak Gemini" → menilai kredibilitas dan proses.

---

## 10. Aturan Konten & Narasi

- Gunakan istilah **entri** untuk satuan data; **siswa unik** hanya untuk angka 203.
- Persentase satu desimal di UI; dua desimal di tabel rekapitulasi.
- Hindari klaim kausal ("tidur menyebabkan…"); gunakan "sejalan dengan", "berpotensi".
- Rekomendasi harus merujuk konteks pertanyaan survei (jadwal malam, konsumsi, jam belajar, pendampingan sebaya).
- Tidak menampilkan angka di luar dataset; target (mis. 90%) wajib dilabeli "target".

---

## 11. Asumsi, Ketergantungan, Risiko

| Kode | Risiko | Dampak | Mitigasi |
|---|---|---|---|
| R1 | Streamlit Cloud belum mendukung Python 3.15 | Deploy gagal | `runtime.txt` python-3.13; fallback Docker |
| R2 | File ber-NIS tidak sengaja terunggah | Pelanggaran privasi | `.gitignore`, hanya JSON anonim yang di-commit, pemindaian rilis |
| R3 | Angka berubah saat pengolahan ulang | Dashboard tidak kredibel | Build script ber-assert + unit test |
| R4 | Interpretasi berlebihan atas data ordinal | Kesimpulan menyesatkan | Batasi pada distribusi & perbandingan; jelaskan batasan |
| R5 | Tenggat pengumpulan 21 Nov 2026 | Karya tidak terkirim | MVP + deploy lebih dulu, polesan menyusul |

**Ketergantungan:** ketersediaan GitHub (repo publik), Streamlit Community Cloud, dan file sumber xlsx di mesin penyusun.

---

## 12. Kriteria Penerimaan Rilis (Definition of Done)

- [ ] Seluruh FR Must terimplementasi dan teruji.
- [ ] `pytest` lulus; agregat default identik dengan §6.5.
- [ ] Aplikasi berjalan headless tanpa error dan dapat diakses via URL publik.
- [ ] Tidak ada NIS/nama pada UI, data yang di-commit, maupun log.
- [ ] Tampilan diperiksa pada 3 breakpoint.
- [ ] Tab Metodologi & Jejak Gemini terisi.
- [ ] `docs/slide-content.md` memuat draf slide 3, 4, 9, 10.
- [ ] Tautan dashboard diuji pada mode incognito.

---

## 13. Rencana Rilis

| Fase | Isi | Keluaran |
|---|---|---|
| F1 | Data layer + validasi | `responses_anon.json`, `meta.json`, tes agregat |
| F2 | MVP dashboard | Filter, KPI, stacked bar, tabel, insight |
| F3 | Visual lanjutan | Heatmap, timeline, radar, matrix, indeks |
| F4 | Kualitas & deploy | QA, publikasi, screenshot |
| F5 | Dokumentasi | Slide draft, README, arsip |

---

## 14. Glosarium

| Istilah | Definisi |
|---|---|
| 7 KAIH | Tujuh Kebiasaan Anak Indonesia Hebat |
| Entri | Satu baris respons formulir |
| Positif | Jawaban Hampir selalu atau Sering |
| Perlu Perhatian | Jawaban Jarang atau Tidak Pernah |
| Indeks 7KAIH | Skor 0–100 hasil normalisasi rata-rata skor ordinal |
| Gelombang | Kelompok tanggal pengisian yang berdekatan |
| Batalyon | Kelompok taruna per tingkat kelas (X/XI/XII) |
