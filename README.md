# IPFEST

Proyek ini berisi eksplorasi dan visualisasi data produksi lapangan Volve serta
data log sumur untuk kebutuhan analisis dan pemodelan.

## Struktur proyek

```text
.
├── data/
│   ├── raw/          # Data asli dan data masukan
│   └── processed/    # Data turunan yang sudah diproses
├── docs/             # Dokumentasi proyek berbahasa Indonesia
├── notebooks/        # Notebook eksplorasi dan eksperimen
├── outputs/          # Grafik dan artefak hasil analisis
├── src/              # Skrip analisis yang dapat dijalankan
├── .gitattributes
├── LICENSE-VOLVE-DATA.md
└── requirements.txt
```

## Persiapan

Gunakan Python 3.10 atau yang lebih baru, lalu pasang dependensi:

```bash
python -m pip install -r requirements.txt
```

## Menjalankan analisis

Semua perintah berikut dijalankan dari direktori utama proyek.

```bash
python src/visualize_production.py --no-show
python src/visualize_train.py --no-show
```

Hasil PNG akan disimpan ke `outputs/`. Untuk memilih berkas data atau sumur
tertentu, gunakan opsi `--data`, `--output`, `--well-output`, `--well`, dan
`--output-dir`. Jalankan `--help` untuk melihat seluruh opsi.

Notebook tersedia di `notebooks/starter_notebook.ipynb`. Jika notebook dibuka
dari folder `notebooks`, jalur data relatifnya sudah disiapkan.

## Data

Data sumber berada di `data/raw/`, sedangkan `data/processed/` berisi artefak
turunan. Data Volve tunduk pada ketentuan lisensi dan atribusi Equinor; baca
[`LICENSE-VOLVE-DATA.md`](LICENSE-VOLVE-DATA.md) sebelum menggunakan atau
mendistribusikan data.

Penjelasan berkas, kolom penting, dan alur kerja tersedia di
[`docs/panduan.md`](docs/panduan.md) serta
[`docs/kamus-data.md`](docs/kamus-data.md).
