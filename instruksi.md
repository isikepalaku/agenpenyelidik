# Instruksi Workflow Analisa Kasus

## Pendahuluan
Workflow ini dirancang untuk mengatur proses analisa kasus oleh tim yang terdiri dari agen dan manajer. Agen bertugas mengumpulkan data, melakukan analisis awal, dan memberikan hasil kepada manajer. Manajer kemudian menyusun laporan akhir berdasarkan data yang terkumpul dan memberikan paparan hasil analisis kepada user.

---

## Struktur Workflow

### **1. Inisialisasi Kasus**
1. **Input**: Informasi kasus diberikan oleh user.
2. **Langkah-langkah**:
   - Manajer mendistribusikan tugas kepada agen.
   - Setiap agen memahami konteks awal terkait kasus.

---

### **2. Tugas Agen**
Setiap agen bertanggung jawab atas tugas berikut:

#### **a. Klasifikasi Objek dan Elemen Kasus**
- **Langkah-langkah**:
  1. Identifikasi objek yang relevan:
     - Saksi-saksi.
     - Benda-benda.
     - Petunjuk-petunjuk.
     - Barang bukti lainnya.
  2. Klasifikasikan elemen-elemen tersebut berdasarkan relevansinya dengan kasus.
- **Output**: Daftar elemen kasus yang terklasifikasi.

#### **b. Analisis Perbuatan Pidana dan Modus Operandi**
- **Langkah-langkah**:
  1. Analisis fakta-fakta untuk menyimpulkan perbuatan pidana.
  2. Identifikasi dan deskripsikan modus operandi.
- **Output**: Ringkasan perbuatan pidana dan modus operandi.

#### **c. Pencarian Pasal dan Undang-Undang (via Web)**
- **Langkah-langkah**:
  1. Gunakan Google Search untuk menemukan pasal dan undang-undang yang relevan.
  2. Dokumentasikan sumber dan konten yang ditemukan.
- **Output**: Daftar pasal dan undang-undang yang relevan.

#### **d. Pencarian Relevansi Putusan Pengadilan (via Vector Database)**
- **Langkah-langkah**:
  1. Gunakan vector database seperti Supabase untuk mencari putusan pengadilan yang relevan.
  2. Dokumentasikan putusan yang ditemukan.
- **Output**: Daftar putusan pengadilan yang relevan.

#### **e. Pencarian Web untuk Tinjauan Yuridis**
- **Langkah-langkah**:
  1. Lakukan riset web untuk menyusun tinjauan yuridis terkait tindak pidana.
  2. Dokumentasikan sumber dan konten yang ditemukan.
- **Output**: Ringkasan tinjauan yuridis.

---

### **3. Pengumpulan dan Analisis Data oleh Manajer**
1. **Input**: Semua hasil dari agen.
2. **Langkah-langkah**:
   - Mengintegrasikan hasil dari setiap agen.
   - Melakukan analisis berdasarkan konteks dan data yang diberikan.
   - Menyusun narasi dan rangkuman kesimpulan.

---

### **4. Pembuatan Laporan Hasil Analisis**
1. **Tugas**:
   - Menyusun laporan akhir berdasarkan format berikut:
     - **Pendahuluan**:
       - Deskripsi kasus.
       - Tujuan analisis.
     - **Klasifikasi Objek dan Elemen Kasus**:
       - Daftar objek, saksi, barang bukti, dan petunjuk.
     - **Kesimpulan Perbuatan Pidana dan Modus Operandi**:
       - Deskripsi tindak pidana.
       - Modus operandi.
     - **Pasal dan Undang-Undang yang Diterapkan**:
       - Daftar pasal dan undang-undang relevan.
     - **Relevansi Putusan Pengadilan**:
       - Rangkuman putusan yang mendukung.
     - **Tinjauan Yuridis**:
       - Penjelasan hukum terkait.
     - **Kesimpulan dan Rekomendasi**:
       - Rekomendasi tindakan atau strategi berdasarkan analisis.
2. **Output**: Laporan akhir dalam format yang telah ditentukan.

---

### **5. Paparan Hasil Analisis**
1. **Langkah-langkah**:
   - Laporan diserahkan kepada user.
   - Manajer memberikan presentasi hasil analisis jika diperlukan.
2. **Output**: Laporan dan presentasi yang mudah dipahami oleh user.

---

## Catatan Tambahan
- Semua agen harus mendokumentasikan hasil kerja mereka secara jelas dan lengkap.
- Hasil kerja agen harus dikompilasi dan diperiksa oleh manajer untuk memastikan kualitas dan kesesuaian dengan kebutuhan kasus.

---
