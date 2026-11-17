# Kamus Data Ringkas

## Data log sumur

| Kolom | Keterangan |
| --- | --- |
| `WELL` | Identitas sumur |
| `DEPTH_MD` | Kedalaman terukur |
| `GR` | Gamma ray |
| `RDEP`, `RMED`, `RSHA` | Resistivitas pada konfigurasi pengukuran berbeda |
| `RHOB` | Densitas bulk |
| `NPHI` | Porositas neutron |
| `DTC` | Waktu tempuh sonik |
| `PEF` | Faktor fotoelektrik |
| `FORCE_2020_LITHOFACIES_LITHOLOGY` | Kode litologi |

`train.csv` menggunakan pemisah `;`. Berkas `train_part1.csv` sampai
`train_part4.csv` merupakan bagian data masukan yang terpisah.

## Data produksi

| Kolom | Keterangan |
| --- | --- |
| `DATEPRD` | Tanggal produksi |
| `WELL_BORE_CODE` | Kode sumur |
| `BORE_OIL_VOL` | Volume minyak |
| `BORE_GAS_VOL` | Volume gas |
| `BORE_WAT_VOL` | Volume air |

Satuan dan makna kolom tambahan mengikuti sumber data Volve. Jangan mengubah
makna satuan tanpa mencatatnya di dokumentasi atau metadata dataset.
