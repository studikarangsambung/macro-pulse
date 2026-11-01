# Ringkasan Komprehensif Sistem: MACRO PULSE · Natural Horizon Terminal

Dokumen ini merangkum seluruh arsitektur, basis data, hasil analisis empiris, backtest kuadran makro, perbandingan model machine learning, serta status repositori **Git** dari sistem **MACRO PULSE · Natural Horizon Terminal**.

---

## 1. Identitas Proyek & Konfigurasi Git

| Parameter | Keterangan / Nilai |
| :--- | :--- |
| **Nama Proyek** | MACRO PULSE · Natural Horizon Terminal |
| **Direktori Kerja Lokal** | `d:\SAHAM\chart` |
| **Repositori Remote (GitHub)** | `https://github.com/studikarangsambung/macro-pulse.git` |
| **Branch Aktif** | `main` (Up to date dengan `origin/main`) |
| **Live Web URL** | [https://studikarangsambung.github.io/macro-pulse/](https://studikarangsambung.github.io/macro-pulse/) |
| **Status Working Tree** | `clean` (Tidak ada perubahan yang tertunda) |
| **Hash Commit Terkini** | `f172487` |
| **Zona Waktu Standar** | Asia/Jakarta (WIB / UTC+7) |

---

## 2. Riwayat Commit Git (Git Log & Tracking)

Berikut adalah riwayat commit terbaru pada branch `main` yang merefleksikan evolusi pengembangan sistem:

```text
* f172487 - (HEAD -> main, origin/main) feat: calibrate spot gold XAUUSD, replace kawat berita with sentimen, and implement Finviz-style live news stream (2 days ago)
* 0d32a0b - feat: real-time asset-specific news sentiment engine linking price drops to live drivers for gold, btc, oil, dollar, tech, and ihsg (2 days ago)
* b2d69d7 - fix: harmonize sector scorecard hybrid logic, add hero IHSG spot, ews formula notes, and disclaimer (2 days ago)
* c51bdb3 - fix: economic calendar official dates and DST, dynamic narrative validator, accurate IHSG spot, and clean crypto wire labels (2 days ago)
* 546b8b2 - feat: institutional Global Market Review whatsapp broadcast with arrows and clean Fed liquidity (3 days ago)
* e0fdd8c - fix: dynamically filter calendar catalysts to prioritize today and upcoming events, adding status badges and past-release recap (3 days ago)
* 8a71b3a - feat: implement intra-week morning briefing broadcast with sentiment chain, US stock sectors, crypto wire, calendar impacts, and verified sources; set 06:00 WIB cron (3 days ago)
* 835ae50 - fix: resolve stale cache, expand news wires to geopolitics & crypto, add automated market driver attribution, and tighten cron schedule (3 days ago)
* 79be914 - feat: add 4-quadrant macro visualizer, net liquidity impact, geopolitical transmission radar, and dynamic news source attribution (3 days ago)
* 3ae55fd - style: simplify footer to concise source line and remove landscape toggle controls (3 days ago)
* 9f866ba - feat: add dynamic rotating natural landscapes, trusted data sources footer, and fix WIB timezone in github actions (3 days ago)
* d9f0fd6 - style: apply natural landscape theme inspired by Canva Open Sauce & Wildlife Watch palette (3 days ago)
* 536f403 - feat: implement retro classic terminal, flow projection, weekly economic calendar with scenario impacts, and live price streaming (3 days ago)
* fd226b4 - feat: complete Phase 3 with Event-Study Backtesting Engine and 5D Historical Macro Analog Matrix (3 days ago)
* b625b8f - feat: add XAUUSD, USD/IDR, verified news feed with sources, and Indonesia macro transmission (3 days ago)
```

---

## 3. Otomasi CI/CD & Pipeline GitHub Actions

Pipeline deployment otomatis diatur melalui `.github/workflows/deploy.yml` yang berjalan berbasis jadwal sesi bursa global dan *event trigger*:

* **Jadwal Eksekusi Terjadwal (Cron UTC & WIB):**
  * `06:00 WIB` (`23:00 UTC`): *Morning Briefing* harian pasca-penutupan Wall Street.
  * `07:00 WIB` (`00:00 UTC`): Persiapan pasar Asia & data pagi.
  * `09:00 WIB` (`02:00 UTC`): Pembukaan Sesi 1 Bursa Efek Indonesia (IHSG).
  * `11:30 WIB` (`04:30 UTC`): Rehat siang IHSG.
  * `13:30 WIB` (`06:30 UTC`): Sesi 2 IHSG & pembukaan bursa Eropa/London.
  * `16:00 WIB` (`09:00 UTC`): Penutupan pasar domestik (IHSG).
  * `18:30 WIB` (`11:30 UTC`): Sesi sore Eropa & *pre-market* bursa New York.
  * `20:30 WIB` (`13:30 UTC`): Waktu rilis data makro ekonomi AS (CPI, PCE, NFP, Jobless Claims).
  * `22:30 WIB` (`15:30 UTC`): Sesi aktif penuh perdagangan Wall Street.
  * `04:00 WIB` (`21:00 UTC`): Penutupan Wall Street & pembaruan rilis neraca H.4.1 The Fed (khusus Kamis malam US).
  * `Akhir Pekan (Sabtu-Minggu)`: Monitoring pasar kripto 24/7 setiap 6 jam (`00:00, 06:00, 12:00, 18:00 UTC`).
* **Trigger Tambahan:**
  * `workflow_dispatch`: Eksekusi manual instan melalui antarmuka web GitHub Actions.
  * `push` pada branch `main` / `master`.
* **Proses Pipeline:** Menyiapkan lingkungan Python 3.12, menginstal dependensi, mengeksekusi `python main.py`, mengompilasi artefak ke direktori `public/`, dan menerbitkan halaman ke **GitHub Pages**.

---

## 4. Arsitektur Berkas & Komponen Kode

### Rincian Modul Inti:
1. **`data_fetcher.py`**:
   * Mengambil data harga 13 instrumen pasar makro via `yfinance`.
   * Mengambil rilis indikator neraca The Fed dan suku bunga via FRED API.
   * `fetch_spot_gold()`: Mengambil kurs spot London (XAUUSD) secara murni via FXRatesAPI untuk mengeliminasi deviasi *futures basis* ($3,990 vs $4,002).
   * Mengagregasi 7 feed RSS berita terverifikasi (Kripto, Emas, Minyak, Dollar, Tech, Indonesia, Global).
2. **`analytics_engine.py`**:
   * Menghitung The Fed Net Liquidity ($\text{WALCL} - \text{TGA} - \text{RRP}$).
   * Menentukan rezim 4-kuadran (Growth Momentum vs Inflation Momentum).
   * Memproses matriks korelasi lintas aset rolling 30-hari.
   * Mengkalkulasi Early Warning System (EWS) score.
   * Menghitung transmisi makro global ke volatilitas domestik (USD/IDR & IHSG).
3. **`calendar_engine.py`**:
   * Menangani kalender rilis ekonomi AS & Indonesia.
   * Menyesuaikan jam rilis dengan *Daylight Saving Time* (EDT vs EST) secara presisi dalam zona waktu WIB.
4. **`narrative_generator.py`**:
   * Menghasilkan teks broadcast WhatsApp yang bersih, berbobot institusional, dan dilengkapi disclaimer resmi.
   * *Dynamic Narrative Validator*: Memastikan arah teks narasi selaras 100% dengan pergerakan matematis harga aset.
5. **`html_generator.py`**:
   * Menghasilkan dashboard web interaktif berpalet *Natural Horizon* (Linen paper `#fbf8f3`, deep forest `#1b2b22`, aksen emas `#d97706`).
   * Mengintegrasikan tabel Finviz-style Live Sentiment Stream dengan filter interaktif berbasis JavaScript.
6. **`config.py`**:
   * Berisi konfigurasi ticker, API Key FRED, threshold EWS, pemetaan 11 sektor S&P 500, dan path database.
7. **`main.py`**:
   * Orkestrator utama yang menjalankan fetcher, analitik, generator narasi, rendering HTML, dan pencatatan log.

---

## 5. Skema & Isi Data Vault (SQLite `data/macro_vault.db`)

Basis data lokal SQLite menyimpan seluruh histori dan observasi terkini:

| Nama Tabel | Jumlah Rekor | Deskripsi & Isi Kolom Utama |
| :--- | :---: | :--- |
| `market_prices` | **810** baris | Histori 90 hari harga penutupan & return harian (`ticker`, `date`, `close`, `change_1d_pct`). |
| `fred_observations` | **710** baris | Rilis berkala data FRED (`series_id`, `date`, `value`). |
| `net_liquidity` | **90** baris | Riwayat harian kalkulasi likuiditas bersih The Fed (`date`, `walcl`, `tga`, `rrp`, `net_liquidity_bil`, `change_4w_bil`). |
| `macro_news` | **123** baris | Agregasi berita terverifikasi (`id`, `category`, `title`, `source`, `link`, `pub_date`, `created_at`). |

---

## 6. Snapshot Indikator Pasar & Data Terkini

### A. Instrumen Pasar Finansial (Market Prices)
| Aset / Ticker | Nama Instrumen | Harga Terakhir | Perubahan 1D | Implikasi Pasar |
| :--- | :--- | :---: | :---: | :--- |
| **GC=F (Spot)** | Emas Spot London (XAUUSD) | **$3,981.15** | -0.17% | Konsolidasi di dekat resistensi psikologis spot $4,000. |
| **CL=F** | Minyak Mentah WTI | **$104.20** | +2.16% | Tekanan inflasi energi persisten; risiko geopolitik. |
| **DX-Y.NYB** | US Dollar Index (DXY) | **101.66** | -0.37% | Pelemahan moderat memberi ruang napas bagi valuta berkembang. |
| **^VIX** | CBOE Volatility Index | **18.54** | +7.79% | Kenaikan kecemasan volatilitas di bawah batas kritis 20.0. |
| **USDIDR=X** | Kurs Rupiah per USD | **Rp 18,120.00** | +0.30% | Tekanan depresiasi nilai tukar rupiah; intervensi Bank Indonesia. |
| **^JKSE** | Indeks Harga Saham Gabungan (IHSG) | **5,057.05** | -0.80% | Aksi ambil untung dan penyesuaian arus modal asing. |
| **HG=F** | Tembaga Berjangka (Copper) | **$6.51** | -1.08% | Sinyal perlambatan aktivitas manufaktur global. |
| **BTC-USD** | Bitcoin | **$77,491.27** | -0.36% | Fase konsolidasi likuiditas tinggi di area support $77k. |
| **ETH-USD** | Ethereum | **$2,237.50** | -0.53% | Rasio ETH/BTC melemah; konsolidasi ekosistem smart contract. |
| **SOL-USD** | Solana | **$96.88** | +1.45% | Penguatan rotasi modal spesifik jaringan. |

### B. Indikator Likuiditas & Neraca The Fed (FRED Data)
* **Fed Total Assets (`WALCL`):** US$ 6,745,635 Juta (~US$ 6.75 Triliun)
* **Treasury General Account (`WTREGEN`):** US$ 999,727 Juta (~US$ 1.00 Triliun)
* **Overnight Reverse Repo (`RRPONTSYD`):** US$ 0.353 Miliar (~US$ 353 Juta)
* **The Fed Net Liquidity:** **US$ 5,745.55 Miliar** (~US$ 5.75 Triliun)
  * *Perubahan 4-Minggu (4W Net Delta):* **-US$ 37.26 Miliar** (Kontraksi likuiditas neto)
* **10-Year Real Interest Rate TIPS (`DFII10`):** **2.67%** (Kondisi moneter ketat / *restrictive territory*)
* **High Yield Option-Adjusted Spread (`BAMLH0A0HYM2`):** **3.14%** (314 bps, risiko gagal bayar korporasi relatif tenang)
* **Chicago Fed National Financial Conditions Index (`NFCI`):** **-0.487** (Kondisi finansial longgar secara agregat)

### C. Inventaris Berita & Sentimen per Kategori
* `indonesia`: 41 berita | `global`: 22 berita | `crypto`: 21 berita | `geopolitics`: 11 berita | `gold`: 8 berita | `tech`: 8 berita | `oil`: 6 berita | `dollar`: 6 berita | **Total: 123 berita**

---

## 7. Kerangka Teoretis & Klasifikasi 4-Kuadran Makro

* **Sumbu X:** Pertumbuhan Ekonomi (*Growth Momentum*)
* **Sumbu Y:** Inflasi (*Inflation Momentum*)

1. **Kuadran I: Reflasi** (Growth ↑, Inflasi ↑) → Komoditas, Energi, Material, Finansial.
2. **Kuadran II: Disinflasi Boom** (Growth ↑, Inflasi ↓) → Teknologi, Konsumer Siklikal, Kripto.
3. **Kuadran III: Stagflasi Energi** (Growth ↓, Inflasi ↑) → **Posisi Saat Ini** (Emas, Kas, Minyak Mentah, Defensif).
4. **Kuadran IV: Deflasi Kontraksi** (Growth ↓, Inflasi ↓) → Obligasi Negara, T-Bills, Utilitas.

---

## 8. Hasil Backtest Historis S&P 500 (1970–2024 / 665 Bulan Data)

| Kuadran Makro | Total Bulan | Proporsi Waktu | Rata-rata Durasi | Median Durasi | Durasi Terpanjang | Return Tahunan S&P 500 | Win Rate Bulanan | Volatilitas Tahunan |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Kuadran I: Reflasi** | 160 | 24.1% | 2.5 bulan | 2 bulan | 11 bulan | **+2.2%** | 58.1% | 14.6% |
| **Kuadran II: Disinflasi Boom** | 160 | 24.1% | 2.5 bulan | 2 bulan | 13 bulan | **+16.7%** | 63.1% | 13.9% |
| **Kuadran III: Stagflasi** | 166 | 25.0% | 2.8 bulan | 2 bulan | 17 bulan | **+3.8%** | 56.0% | 15.0% |
| **Kuadran IV: Deflasi Kontraksi**| 179 | 26.9% | 2.7 bulan | 2 bulan | 11 bulan | **+15.2%** | 63.1% | 16.6% |

---

## 9. Evaluasi & Komparasi Model Machine Learning Rezim Makro

| Model / Metode | OOS Accuracy | Macro Precision | Macro Recall | Macro F1-Score | Annualized Return | Sharpe Ratio | Max Drawdown (MDD) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Supervised ML (Random Forest)** | **98.9%** | **98.9%** | **98.9%** | **98.9%** | +6.7% | 0.40 | -30.7% |
| **Linear Baseline (Logistic Reg.)** | 87.6% | 87.5% | 87.4% | 87.4% | +6.6% | 0.38 | -30.7% |
| **Rule-Based Heuristik (Thresholds)**| 58.5% | 63.0% | 56.0% | 54.4% | **+7.1%** | **0.43** | **-27.1%** |
| **Unsupervised ML (GMM Clustering)** | 35.6% | 23.2% | 31.0% | 21.2% | +5.2% | 0.28 | -32.2% |
| *Benchmark: Buy & Hold S&P 500* | *N/A* | *N/A* | *N/A* | *N/A* | *+10.7%* | *0.51* | *-52.6%* |

---

## 10. Fitur Antarmuka Pengguna & Finviz Sentimen Stream

1. **Palet Retro Classic Natural Horizon:** Linen Paper (`#fbf8f3`), Forest Green, Soft Sage borders.
2. **Finviz-Style Live Sentiment Stream (Tab 1):** Agregasi berita dan sentimen menghubungkan harga instrumen dengan katalis driver berita, dilengkapi filter interaktif client-side (`Semua`, `Kripto`, `Emas`, `Minyak`, `Dollar`, `Tech`, `IHSG`).
3. **Penyelarasan Istilah:** Seluruh istilah *"kawat berita"* diubah menjadi **"Sentimen"** / **"Sentimen Pasar"**.
4. **Kalender Ekonomi & DST:** Menyesuaikan jam rilis ekonomi AS & Indonesia terhadap *Daylight Saving Time* (WIB).
5. **Format WhatsApp Broadcast Generator:** Komponen siap salin dengan atribusi resmi `Disusun oleh studikarangsambung-market pulse engine`.

---

## 11. Daftar Berkas Visual Tersedia

* `macro_quadrants_sp500_backtest.png`: Grafik 4 kuadran historis S&P 500 (1970–2024) dan durasi kuadran.
* `ml_regime_detection_chart.png`: Proyeksi 2D PCA posisi kuadran makro terkini vs historis.
* `regime_accuracy_comparison.png`: Grafik perbandingan metrik evaluasi model Machine Learning.
* `macro_quadrants_interactive.html`: Visualisasi interaktif berbasis Plotly.

---
*Laporan ini disusun oleh **studikarangsambung-market pulse engine***
