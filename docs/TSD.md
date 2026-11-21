# TSD — Technical Specification Document

**Produk:** Dashboard Pemantauan 7 KAIH — SMAN 2 Taruna Bhayangkara Jawa Timur
**Dokumen:** Technical Specification Document (TSD)
**Versi:** 1.0
**Tanggal:** 21 November 2026
**Status:** Disetujui
**Prasyarat:** [`PRD.md`](./PRD.md) · **Rujukan arsitektur:** [`ARCHITECTURE.md`](./ARCHITECTURE.md)

---

## 1. Tujuan Dokumen

Menjabarkan bagaimana kebutuhan pada PRD diimplementasikan: stack, struktur repositori, kontrak data, kontrak modul, algoritma, spesifikasi UI/grafik, penanganan error, pengujian, dan deployment. Dokumen ini adalah acuan tunggal bagi penulis kode.

---

## 2. Tech Stack

| Lapisan | Teknologi | Versi | Alasan |
|---|---|---|---|
| Bahasa | Python | 3.13 (deploy), 3.15 (lokal) | Tersedia di Streamlit Cloud & mesin pengembang |
| UI framework | Streamlit | 1.67.x | Cepat, Python-native, gratis untuk app publik |
| Pengolahan data | pandas | 3.1.x | Agregasi tabular ringkas dan teruji |
| Visualisasi | Plotly | 7.1.x | Interaktif, tema konsisten, ekspor PNG |
| Pembacaan Excel | openpyxl | 3.1.x | Membaca `.xlsx` tanpa Excel |
| Validasi skema | `dataclasses` + `typing` | stdlib | Tanpa dependency tambahan |
| Pengujian | pytest | 9.x | Standar industri |
| Lint/format | Ruff | 0.15.x | Cepat, konfigurasi tunggal di `pyproject.toml` |
| Hosting | Streamlit Community Cloud | — | Publik, gratis, terhubung GitHub |
| Version control | Git + GitHub | — | Sumber deploy |

**Prinsip:** logika analitik murni (tanpa import Streamlit) agar dapat diuji tanpa runtime UI; Streamlit hanya ada di lapisan presentasi.

---

## 3. Struktur Repositori

```text
Dashboard/
├─ app.py                       # Entry point Streamlit (composition root)
├─ g7kaih/
│  ├─ __init__.py
│  ├─ constants.py              # Taksonomi 7 KAIH, skala, batalyon, path
│  ├─ data.py                   # Loader + Filter + validasi skema
│  ├─ analytics.py             # Agregasi & indeks (pure functions)
│  ├─ insights.py              # Generator temuan & rekomendasi
│  ├─ charts.py                # Factory Plotly
│  ├─ theme.py                 # Palet, CSS, komponen HTML
│  └─ formatting.py            # Format angka/persentase Indonesia
├─ data/
│  ├─ responses_anon.json      # 232 record anonim (committed)
│  └─ meta.json                # Metadata & checksum (committed)
├─ scripts/build_data.py       # xlsx → JSON + assertion
├─ tests/
│  ├─ conftest.py
│  ├─ test_data.py
│  ├─ test_analytics.py
│  └─ test_insights.py
├─ assets/styles.css
├─ docs/{PRD,TSD,ARCHITECTURE,slide-content}.md
├─ .streamlit/config.toml
├─ pyproject.toml
├─ requirements.txt
├─ runtime.txt
├─ .gitignore
└─ README.md
```

**Aturan impor:** `app.py` → `g7kaih.*`; modul `g7kaih/` tidak boleh mengimpor `app` atau `streamlit`.

---

## 4. Kontrak Data

### 4.1 `data/responses_anon.json`

Array objek; setiap objek adalah satu entri.

```json
{
  "entry_id": 1,
  "timestamp": "2026-10-28T15:26:03+07:00",
  "battalion": "X",
  "answers": {
    "bangun_pagi": 4,
    "ibadah": 4,
    "olahraga": 4,
    "makan_sehat": 4,
    "gemar_belajar": 4,
    "bermasyarakat": 4,
    "tidur_cepat": 4
  }
}
```

| Field | Tipe | Aturan |
|---|---|---|
| `entry_id` | int | Unik, 1..232, urut timestamp |
| `timestamp` | string ISO-8601 | Waktu lokal +07:00 |
| `battalion` | enum `X`/`XI`/`XII` | Wajib |
| `answers.*` | int 1–4 | Wajib, 7 kunci lengkap |

**Larangan:** tidak boleh memuat NIS, nama, email, atau kolom bebas.

### 4.2 `data/meta.json`

```json
{
  "schema_version": 1,
  "total_entries": 232,
  "unique_students": 203,
  "date_min": "2026-10-28",
  "date_max": "2026-11-14",
  "battalion_counts": {"X": 138, "XI": 47, "XII": 47},
  "source_file": "DATA EVALUASI G7KAIH ... .xlsx",
  "source_sha256": "<64 hex>",
  "generated_at": "2026-11-21T00:00:00+07:00"
}
```

### 4.3 DataFrame Runtime (`load_dataset`)

| Kolom | dtype | Keterangan |
|---|---|---|
| `entry_id` | int64 | ID entri |
| `timestamp` | datetime64[ns, UTC+07:00] | Waktu pengisian |
| `date` | datetime64[ns] | Tanggal (tanpa jam) untuk grouping |
| `battalion` | category | `X`, `XI`, `XII` |
| `bangun_pagi` … `tidur_cepat` | int8 | Skor 1–4 |
| `total_score` | int16 | Jumlah 7 skor (4–28) |
| `index` | float64 | `(total_score − 7) / 21 × 100` |

---

## 5. Kontrak Modul

### 5.1 `constants.py`

```python
@dataclass(frozen=True, slots=True)
class Habit:
    key: str
    label: str
    short_label: str
    question: str

HABITS: tuple[Habit, ...]                 # urutan baku 1..7
HABIT_BY_KEY: Mapping[str, Habit]
SCALE_LABELS: tuple[str, ...]             # ("Hampir selalu", "Sering", "Jarang", "Tidak Pernah")
SCALE_SCORES: Mapping[str, int]           # label -> 4..1
POSITIVE_SCORES: frozenset[int]           # {4, 3}
ATTENTION_SCORES: frozenset[int]          # {2, 1}
POSITIVE_LABELS / ATTENTION_LABELS
BATTALIONS: Mapping[str, Battalion]       # code -> (name, short_name)
DATA_DIR / PROJECT_ROOT: Path
```

### 5.2 `data.py`

```python
@dataclass(frozen=True, slots=True)
class Filters:
    battalions: tuple[str, ...] = ()      # kosong = semua
    start: date | None = None
    end: date | None = None
    habit: str | None = None              # None = semua

def load_meta(path: Path | None = None) -> dict[str, Any]
def load_dataset(path: Path | None = None) -> pd.DataFrame
def apply_filters(df: pd.DataFrame, filters: Filters) -> pd.DataFrame
def validate_dataset(df: pd.DataFrame) -> None   # raise DataValidationError
def active_filter_label(df: pd.DataFrame, filters: Filters) -> str
```

**Aturan:** `load_dataset` melempar `DataValidationError` bila skema tidak sesuai; `apply_filters` tidak memutasi input; filter `habit` hanya memengaruhi tampilan fokus, bukan menghapus kolom.

### 5.3 `analytics.py`

```python
def distribution(df: pd.DataFrame) -> pd.DataFrame
def summary_table(df: pd.DataFrame) -> pd.DataFrame
def battalion_summary(df: pd.DataFrame) -> pd.DataFrame
def timeline(df: pd.DataFrame) -> pd.DataFrame
def wave_summary(df: pd.DataFrame) -> pd.DataFrame
def index_by_habit(df: pd.DataFrame) -> pd.DataFrame
def overall_index(df: pd.DataFrame) -> float
def priority_matrix(df: pd.DataFrame) -> pd.DataFrame
def kpi_snapshot(df: pd.DataFrame, meta: dict) -> KpiSnapshot
def top_and_bottom(df: pd.DataFrame) -> tuple[Row, Row]
```

Semua fungsi **pure** (tanpa I/O, tanpa state), menerima DataFrame tervalidasi, mengembalikan DataFrame baru.

### 5.4 `insights.py`

```python
@dataclass(frozen=True, slots=True)
class Insight:
    title: str
    detail: str
    tone: Literal["positive", "attention", "neutral"]

@dataclass(frozen=True, slots=True)
class Recommendation:
    priority: int
    title: str
    action: str
    evidence: str
    impact: str

def build_insights(df, meta) -> list[Insight]
def build_recommendations(df) -> list[Recommendation]
```

### 5.5 `charts.py`

```python
def stacked_distribution(summary: pd.DataFrame) -> go.Figure
def battalion_heatmap(summary: pd.DataFrame) -> go.Figure
def battalion_grouped(summary: pd.DataFrame) -> go.Figure
def timeline_chart(timeline_df: pd.DataFrame) -> go.Figure
def radar_chart(summary: pd.DataFrame) -> go.Figure
def priority_matrix_chart(matrix: pd.DataFrame) -> go.Figure
def index_gauge(value: float) -> go.Figure
def apply_theme(fig: go.Figure, *, height: int = 380) -> go.Figure
```

### 5.6 `formatting.py`

```python
def pct(value: float, decimals: int = 1) -> str      # 12.345 -> "12,3%"
def num(value: int | float) -> str                    # 1000 -> "1.000"
def ratio(count: int, total: int, decimals: int = 1) -> str
def date_id(value: date) -> str                       # "5 Nov 2026"
```

### 5.7 `theme.py`

```python
COLORS: Mapping[str, str]          # navy, gold, surface, ink, muted, grid
SCALE_COLORS: Mapping[str, str]    # per label skala
def inject_css() -> None           # st.markdown(<style>)
def kpi_card(label, value, caption, accent) -> str
def section_title(title, subtitle) -> str
def badge(text, tone) -> str
```

---

## 6. Algoritma & Rumus

### 6.1 Distribusi
Untuk setiap kebiasaan `h` dan kategori `c`:
`count(h,c) = |{r : answers[r,h] = score(c)}|`, `pct = count / n × 100`.

### 6.2 Positif / Perlu Perhatian
`positive = count(HS) + count(S)`; `attention = count(J) + count(TP)`.
`attention_pct = attention / n × 100`.

### 6.3 Indeks 7KAIH
`index = (mean_score − 1) / 3 × 100`, dengan `mean_score` rata-rata skor 1–4.
Ekuivalen per entri: `(total_score − 7) / 21 × 100`. Rentang 0–100; 100 = selalu pada semua kebiasaan.

### 6.4 Priority Matrix
- X = `positive_pct`, Y = `attention_pct`, ukuran = jumlah entri.
- Ambang kuadran: `X = 85%`, `Y = 15%` (dapat dikonfigurasi di `constants.py`).
- Kuadran: **Prioritas Tinggi** (X < 85, Y ≥ 15), **Pantau** (X < 85, Y < 15), **Pertahankan** (X ≥ 85, Y < 15), **Waspada** (X ≥ 85, Y ≥ 15).

### 6.5 Gelombang Pengisian
Pemetaan tanggal → gelombang:
- G1: 2026-11-05
- G2: 2026-11-08 … 2026-11-09
- G3: 2026-11-11
- G4: 2026-11-13 … 2026-11-14
- Luar gelombang: 2026-10-28, 2026-11-06, 2026-11-12 (ditandai "lain-lain").

### 6.6 Insight Otomatis
1. Kebiasaan dengan `positive_pct` tertinggi → kekuatan.
2. Kebiasaan dengan `attention_pct` tertinggi → prioritas.
3. Batalyon dengan `attention_pct` tertinggi pada kebiasaan prioritas → target pembinaan.
4. Kesenjangan maksimum antar-batalyon pada satu kebiasaan (selisih poin persentase).
5. Bila filter menyisakan < 10 entri → tampilkan peringatan interpretasi.

Semua narasi memakai angka hasil hitung, bukan konstanta.

---

## 7. Spesifikasi UI

### 7.1 Layout

```text
┌──────────────────────────────────────────────────────────────┐
│ Header: judul, subjudul, badge periode & cakupan             │
├───────────────┬──────────────────────────────────────────────┤
│ Sidebar       │ Ringkasan filter aktif                       │
│ - Batalyon    │ [KPI][KPI][KPI][KPI]                         │
│ - Tanggal     │ Tabs:                                        │
│ - Kebiasaan   │  Ringkasan | Distribusi | Per Batalyon |     │
│ - Reset       │  Tren | Tabel | Insight & Aksi | Metodologi  │
│ - Sumber data │                                              │
└───────────────┴──────────────────────────────────────────────┘
```

### 7.2 Palet

| Token | Nilai | Pemakaian |
|---|---|---|
| `navy` | `#0B2545` | Header, teks utama |
| `gold` | `#C9A227` | Aksen, garis, badge |
| `surface` | `#F7F8FA` | Latar kartu |
| `ink` | `#10233F` | Teks |
| `muted` | `#5B6B82` | Teks sekunder |
| `hs` | `#14532D` | Hampir selalu |
| `s` | `#22A06B` | Sering |
| `j` | `#E0A100` | Jarang |
| `tp` | `#C0392B` | Tidak Pernah |

Kontras teks pada kartu ≥ 4.5:1. Setiap grafik menyertakan label/legenda tekstual.

### 7.3 Spesifikasi Grafik

| Grafik | Tipe | Sumbu/Encode | Interaksi |
|---|---|---|---|
| Distribusi | 100% stacked horizontal bar | Y = kebiasaan, X = persen, warna = skala | Hover: n & % |
| Perbandingan | Heatmap | X = kebiasaan, Y = batalyon, nilai = attention % | Hover: n & % |
| Alternatif | Grouped bar | X = kebiasaan, warna = batalyon | Hover |
| Tren | Bar + line (secondary axis) | X = tanggal, Y1 = entri, Y2 = kumulatif | Hover, unified |
| Radar | Scatterpolar | 7 sumbu = indeks, warna = batalyon | Hover |
| Matrix | Scatter | X = positif %, Y = perhatian %, size = n | Hover, label |
| Indeks | Gauge | 0–100 | Angka tengah |

Semua grafik memakai `apply_theme` (font, grid, margin, modebar disembunyikan) dan `height` konsisten.

### 7.4 Komponen KPI
Kartu HTML kustom (bukan `st.metric`) agar dapat menampilkan label, nilai besar, caption, dan aksen. Dirender dengan `st.markdown(..., unsafe_allow_html=True)`; seluruh nilai di-escape.

### 7.5 State & Caching
- Filter disimpan di widget Streamlit (session state otomatis).
- `@st.cache_data` pada `load_dataset` dan `load_meta` (key: path + mtime).
- Fungsi agregasi tidak di-cache (murah, 232 baris) agar bebas bug state.
- Tombol **Reset filter** mengembalikan default.

### 7.6 Empty State
Bila `len(df) == 0`: tampilkan kartu informasi "Tidak ada entri pada kombinasi filter ini", sertakan tombol reset, dan hentikan rendering grafik (`st.stop()` setelah pesan).

---

## 8. Penanganan Error & Logging

| Kondisi | Perilaku |
|---|---|
| File data hilang | `FileNotFoundError` dengan pesan jalur; UI menampilkan instruksi `python scripts/build_data.py` |
| Skema JSON tidak valid | `DataValidationError`; UI menampilkan ringkasan kolom yang gagal |
| Filter kosong | Empty state, bukan exception |
| Nilai di luar 1–4 | Ditolak saat build & load |
| Error tak terduga | `st.error` generik + log `logging.exception` (tanpa PII) |

Logging memakai `logging` stdlib level `INFO`; tidak mencatat isi respons.

---

## 9. Pengujian

| Jenis | Cakupan | Alat |
|---|---|---|
| Unit — data | Skema, tipe, rentang skor, jumlah baris | pytest |
| Unit — analytics | Distribusi, positif/perhatian, indeks, matriks, timeline | pytest |
| Golden test | 232 baris → seluruh angka §6.5 PRD | pytest (parameterized) |
| Unit — insights | Tidak ada angka hard-code; empty guard | pytest |
| Smoke UI | App start headless, HTTP 200, tanpa traceback | `streamlit run` + HTTP check |
| E2E/manual | Filter, tab, unduh CSV, 3 breakpoint | Playwright/manual |

Perintah:

```bash
pytest -q
ruff check .
streamlit run app.py --server.headless true --server.port 8501
```

Ambang kelulusan: 100% tes lulus, 0 error Ruff, 0 selisih golden test.

---

## 10. Build Data

`scripts/build_data.py`:

1. Baca sheet `Form Responses 1` via pandas/openpyxl.
2. Buang baris tanpa timestamp; validasi 232 baris.
3. Petakan label → skor; validasi domain 1–4 dan 7 kolom lengkap.
4. Petakan nama batalyon → kode; validasi 138/47/47.
5. Hitung `unique_students` dari file berkode **hanya bila tersedia** (opsional, tidak pernah ditulis ke output).
6. Tulis `responses_anon.json` (indent 2, UTF-8, tanpa NIS) dan `meta.json` + SHA-256 sumber.
7. Assert seluruh hitungan referensi; gagal → exit code 1.

Idempoten: output deterministik kecuali `generated_at`.

---

## 11. Deployment

### 11.1 Streamlit Community Cloud
1. Repositori GitHub **publik** berisi kode + `data/*.json` (tanpa xlsx berkode).
2. New app → branch `main`, main file `app.py`.
3. Python dari `runtime.txt` (`python-3.13`).
4. Tidak ada secrets yang diperlukan.
5. Uji URL di mode incognito; tempel ke slide 4.

### 11.2 Lokal
```bash
py -3.13 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python scripts/build_data.py
streamlit run app.py
```

### 11.3 Fallback
Dockerfile berbasis `python:3.13-slim` untuk Render/Railway bila Cloud bermasalah.

---

## 12. Keamanan & Privasi

- Hanya data agregat/anonim yang di-commit; xlsx sumber masuk `.gitignore`.
- Tidak ada input pengguna yang disimpan.
- Tidak ada remote telemetry kustom.
- HTML kustom di-escape (`html.escape`) untuk mencegah injeksi.
- Tautan publik bersifat read-only; tidak ada operasi tulis.

---

## 13. Matriks Keterlacakan (PRD → Implementasi)

| FR | Modul/Fungsi | Tes |
|---|---|---|
| FR-01 | `app.py` sidebar, `data.apply_filters` | `test_data.py` |
| FR-02 | `analytics.kpi_snapshot`, `theme.kpi_card` | `test_analytics.py` |
| FR-03 | `analytics.distribution`, `charts.stacked_distribution` | golden test |
| FR-04 | `analytics.battalion_summary`, `charts.battalion_heatmap` | golden test |
| FR-05 | `analytics.timeline`, `charts.timeline_chart` | `test_analytics.py` |
| FR-06 | `analytics.summary_table`, tab Tabel | golden test |
| FR-07 | `insights.build_insights`, `build_recommendations` | `test_insights.py` |
| FR-08 | `analytics.overall_index`, `index_by_habit` | `test_analytics.py` |
| FR-09 | `analytics.priority_matrix`, `charts.priority_matrix_chart` | `test_analytics.py` |
| FR-10 | `charts.radar_chart` | smoke |
| FR-11 | tab Metodologi | review |
| FR-12 | toggle mode laporan | manual |
| FR-13 | `st.download_button` CSV | manual |
| FR-14 | Streamlit Cloud | uji URL |

---

## 14. Definisi Selesai Teknis

- [ ] `pytest` hijau dan golden test 0 selisih.
- [ ] `ruff check` bersih.
- [ ] App start headless tanpa traceback; HTTP 200.
- [ ] Tidak ada impor Streamlit di `g7kaih` selain `theme.inject_css`.
- [ ] Dokumentasi modul dan tipe lengkap.
- [ ] Data anonim terverifikasi (pemindaian NIS).
