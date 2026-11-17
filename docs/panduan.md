# Panduan Proyek

## Tujuan

IPFEST digunakan untuk:

1. mengeksplorasi data produksi harian dan kontribusi setiap sumur;
2. memeriksa distribusi litologi serta kelengkapan pengukuran log sumur; dan
3. menyediakan visualisasi awal sebagai dasar analisis lanjutan.

Proyek ini belum menyediakan pipeline pelatihan model otomatis. Notebook
starter dapat digunakan untuk eksperimen pemodelan secara interaktif.

## Alur kerja

1. Simpan data masukan di `data/raw/`.
2. Simpan data hasil transformasi yang dipakai ulang di `data/processed/`.
3. Jalankan skrip dari direktori utama proyek.
4. Periksa grafik yang dihasilkan di `outputs/`.
5. Catat perubahan struktur atau asumsi data pada dokumentasi ini.

## Skrip

### `src/visualize_production.py`

Membaca `data/processed/production_data_processed.csv`, memvalidasi kolom
produksi, lalu membuat:

- ringkasan produksi minyak, gas, dan air berdasarkan waktu;
- cakupan catatan sumur per hari; dan
- tren produksi per sumur dengan rata-rata bergerak 30 hari.

### `src/visualize_train.py`

Membaca `data/raw/train.csv` dengan pemisah titik koma. Skrip memindai jumlah
baris, sumur, kelas litologi, dan nilai yang hilang, kemudian membuat ringkasan
dataset serta profil log untuk satu sumur.

## Konvensi direktori

- `raw`: data sumber atau data masukan yang tidak diubah oleh skrip.
- `processed`: data turunan yang dipakai oleh analisis berikutnya.
- `outputs`: grafik dan hasil eksekusi yang dapat dibuat ulang.
- `notebooks`: eksperimen interaktif; kode produksi tetap berada di `src`.
