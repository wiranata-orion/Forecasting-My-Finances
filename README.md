## Fitur Utama

1. **Penyimpanan Database SQLite Nyata**
   - Basis data menggunakan file SQLite lokal di [`backend/finance.db`](file:///c:/Users/Xufruz/OneDrive/Documents/Locked%20In/Forcasting%20Keuangan/backend/finance.db).
   - Seluruh data dummy telah dihapus; aplikasi siap digunakan langsung untuk mencatat keuangan nyata Anda.

2. **Tampilan Tenang Tanpa Navbar yang Mengganggu**
   - Header atas dibuat minimalis dan ringkas terintegrasi langsung di dasbor.
   - Tombol **+ Tambah Transaksi** dan **+ Kemungkinan Pengeluaran** dapat diakses langsung dengan mudah.

3. **Grafik Bundar Donat (Donut Allocation Chart)**
   - Pemasukan memperbesar nilai total donat sebagai kapasitas kas.
   - Alokasi dibagi menjadi: **Sisa Tabungan Bersih**, **Pengeluaran Riil**, dan **Kemungkinan Pengeluaran**.
   - Bagian tengah donat menampilkan nominal **Sisa Uang yang Bisa Ditabung**.

4. **Analitik Batang Pertanggal (Daily Bar Analytics)**
   - Menampilkan batang **Hijau (Pemasukan)** dan **Merah (Pengeluaran)** per setiap tanggal.
   - Dilengkapi filter 7 hari, 14 hari, atau semua tanggal serta rata-rata pengeluaran harian.

5. **Kemungkinan Pengeluaran Bulan Ini (Planned Expenses)**
   - Catat rencana pengeluaran atau estimasi biaya tak terduga dengan bobot kepastian (%).
   - Analisa dampak langsung ke sisa uang yang bisa ditabung bulan ini.
   - Tombol **Realisasi** untuk langsung mengubah rencana menjadi pengeluaran aktual.

6. **Forcasting Bulan Depan (Python Machine Learning)**
   - Berjalan di backend menggunakan **Python (`scikit-learn`, `numpy`, `pandas`)**.
   - Menghitung proyeksi pengeluaran bulan depan, estimasi sisa tabungan, rasio tabungan (%), batas belanja harian aman (*Safe Daily Limit*), dan saran keuangan pintar.

7. **Log Aktivitas Transaksi**
   - Riwayat mutasi kas pemasukan dan pengeluaran.
   - Pencarian instan, filter tab (*Semua*, *Pemasukan*, *Pengeluaran*), dan aksi hapus.
