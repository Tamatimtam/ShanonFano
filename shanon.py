# -*- coding: utf-8 -*-
import os
import pickle # Digunakan HANYA untuk menyimpan/membaca dictionary kode & data terkompresi ke file, BUKAN untuk algoritma inti.
import heapq # Digunakan untuk priority queue, alternatif untuk sorting manual, bisa diganti sorting biasa jika mau lebih dasar lagi.
from collections import defaultdict, Counter

# ================================================
# Bagian Inti Algoritma Shannon-Fano
# ================================================

def hitung_frekuensi_byte(data_bytes):
    """
    Menghitung frekuensi kemunculan setiap nilai byte (0-255) dalam data.
    Input: data_bytes (objek bytes)
    Output: dictionary {nilai_byte: frekuensi}
    """
    print("   [*] Menghitung frekuensi byte...")
    # Counter adalah cara efisien untuk menghitung frekuensi
    frekuensi = Counter(data_bytes)
    print(f"   [*] Ditemukan {len(frekuensi)} byte unik.")
    return dict(frekuensi)

def urutkan_frekuensi(dict_frekuensi):
    """
    Mengurutkan dictionary frekuensi berdasarkan frekuensi (descending).
    Input: dictionary {nilai_byte: frekuensi}
    Output: list of tuples [(frekuensi, nilai_byte), ...]
    """
    list_terurut = sorted(dict_frekuensi.items(), key=lambda item: (-item[1], item[0]))
    return list_terurut # Output: [(nilai_byte, frekuensi), ...]

def cari_titik_pisah(list_frekuensi_terurut):
    """
    Mencari indeks untuk membagi list terurut menjadi dua bagian
    dengan total frekuensi seimbang mungkin.
    Input: list of tuples [(nilai_byte, frekuensi), ...]
    Output: indeks titik pisah (int)
    """
    total_frekuensi = sum([item[1] for item in list_frekuensi_terurut])
    akumulasi_frekuensi = 0
    selisih_terbaik = total_frekuensi # Inisialisasi dengan selisih maksimum
    indeks_pisah = 0

    # Iterasi untuk mencari titik pisah terbaik
    for i, item in enumerate(list_frekuensi_terurut):
        akumulasi_frekuensi += item[1]
        # Frekuensi grup 1: akumulasi_frekuensi
        # Frekuensi grup 2: total_frekuensi - akumulasi_frekuensi
        selisih_saat_ini = abs(akumulasi_frekuensi - (total_frekuensi - akumulasi_frekuensi))

        # Jika selisih saat ini lebih baik (lebih kecil)
        if selisih_saat_ini <= selisih_terbaik:
             selisih_terbaik = selisih_saat_ini
             indeks_pisah = i + 1 # Titik pisahnya adalah SETELAH indeks i
        else:
             # Jika selisih mulai membesar lagi, berarti titik pisah terbaik sudah terlewat
             # Titik pisah terbaik adalah 'indeks_pisah' yang sudah tersimpan
             break # Optimasi: tidak perlu iterasi terus jika selisih sudah membesar

    # Pastikan tidak memisah list dengan 1 elemen
    if len(list_frekuensi_terurut) <= 1:
        return 0
    # Jika indeks pisah = panjang list, mundurkan satu agar grup kedua tidak kosong
    if indeks_pisah == len(list_frekuensi_terurut):
        indeks_pisah -= 1
    # Jika indeks pisah 0 (artinya elemen pertama frekuensinya > 50%),
    # paksakan pisah setelah elemen pertama agar proses rekursif jalan.
    if indeks_pisah == 0 and len(list_frekuensi_terurut) > 1:
        indeks_pisah = 1

    return indeks_pisah

def bangun_pohon_kode_rekursif(list_frekuensi_terurut, kode_saat_ini="", dict_kode={}):
    """
    Fungsi rekursif untuk membangun dictionary kode Shannon-Fano.
    Input:
        list_frekuensi_terurut: list of tuples [(nilai_byte, frekuensi), ...]
        kode_saat_ini: string kode biner yang sedang dibangun
        dict_kode: dictionary hasil {nilai_byte: kode_biner_string}
    Output: dictionary dict_kode yang sudah terisi
    """
    # Basis Rekursif: Jika list hanya berisi 1 elemen, simpan kodenya
    if len(list_frekuensi_terurut) == 1:
        nilai_byte = list_frekuensi_terurut[0][0]
        # Handle kasus jika hanya ada 1 simbol unik di seluruh file
        if not kode_saat_ini:
             dict_kode[nilai_byte] = "0" # Atau "1", konsisten saja
        else:
             dict_kode[nilai_byte] = kode_saat_ini
        return dict_kode

    # Langkah Rekursif:
    # 1. Cari titik pisah
    indeks_pisah = cari_titik_pisah(list_frekuensi_terurut)

    # 2. Bagi list menjadi dua
    grup_kiri = list_frekuensi_terurut[0:indeks_pisah]
    grup_kanan = list_frekuensi_terurut[indeks_pisah:]

    # 3. Panggil rekursif untuk grup kiri (tambahkan '0' ke kode)
    bangun_pohon_kode_rekursif(grup_kiri, kode_saat_ini + "0", dict_kode)

    # 4. Panggil rekursif untuk grup kanan (tambahkan '1' ke kode)
    bangun_pohon_kode_rekursif(grup_kanan, kode_saat_ini + "1", dict_kode)

    return dict_kode


# ================================================
# Bagian Encoding & Decoding
# ================================================

def encode_data(data_bytes, dict_kode):
    """
    Mengubah data byte asli menjadi string bit berdasarkan dictionary kode.
    Input:
        data_bytes: objek bytes asli
        dict_kode: dictionary {nilai_byte: kode_biner_string}
    Output: string bit hasil encode (contoh: "0110101001...")
    """
    print("   [*] Encoding data ke bit string...")
    encoded_string = ""
    for byte in data_bytes:
        encoded_string += dict_kode[byte]
    print(f"   [*] Panjang bit string hasil encode: {len(encoded_string)}")
    return encoded_string

def bits_ke_bytes(string_bit):
    """
    Mengubah string bit menjadi objek bytes.
    Menambahkan padding '0' di akhir jika panjang string bit tidak kelipatan 8.
    Output: tuple (objek_bytes, jumlah_bit_padding)
    """
    print("   [*] Mengubah bit string ke bytes...")
    sisa_bagi = len(string_bit) % 8
    bit_padding = 0
    if sisa_bagi != 0:
        bit_padding = 8 - sisa_bagi
        string_bit += '0' * bit_padding # Tambahkan padding '0'

    # Konversi per 8 bit
    list_byte = []
    for i in range(0, len(string_bit), 8):
        byte_chunk_string = string_bit[i:i+8]
        nilai_integer = int(byte_chunk_string, 2) # Konversi string biner ke integer
        list_byte.append(nilai_integer)

    objek_bytes = bytes(list_byte) # Konversi list integer ke objek bytes
    print(f"   [*] Jumlah bit padding ditambahkan: {bit_padding}")
    print(f"   [*] Ukuran data terkompresi (bytes): {len(objek_bytes)}")
    return objek_bytes, bit_padding

def bytes_ke_bits(objek_bytes, bit_padding):
    """
    Mengubah objek bytes kembali menjadi string bit, menghapus padding.
    Input:
        objek_bytes: data byte terkompresi
        bit_padding: jumlah bit padding yang ditambahkan saat encode
    Output: string bit asli (tanpa padding)
    """
    print("   [*] Mengubah bytes kembali ke bit string...")
    string_bit_hasil = ""
    for byte in objek_bytes:
        # format(byte, '08b') -> ubah integer ke string biner 8 digit (termasuk leading zero)
        string_bit_hasil += format(byte, '08b')

    # Hapus padding
    if bit_padding > 0:
        string_bit_hasil = string_bit_hasil[:-bit_padding] # Slice untuk buang padding di akhir

    print(f"   [*] Bit padding dihapus: {bit_padding}")
    print(f"   [*] Panjang bit string setelah padding dihapus: {len(string_bit_hasil)}")
    return string_bit_hasil

def decode_data(string_bit_encoded, dict_kode):
    """
    Mengubah string bit ter-encode kembali ke data byte asli.
    Input:
        string_bit_encoded: string bit yang akan di-decode
        dict_kode: dictionary {nilai_byte: kode_biner_string}
    Output: objek bytes hasil decode
    """
    print("   [*] Decoding bit string ke data asli...")
    # Balik dictionary kode untuk mempermudah pencarian: {kode_biner_string: nilai_byte}
    dict_kode_terbalik = {kode: byte for byte, kode in dict_kode.items()}

    list_byte_hasil = []
    kode_sementara = ""
    for bit in string_bit_encoded:
        kode_sementara += bit
        if kode_sementara in dict_kode_terbalik:
            # Jika kode sementara ditemukan di dictionary, tambahkan byte-nya ke hasil
            nilai_byte = dict_kode_terbalik[kode_sementara]
            list_byte_hasil.append(nilai_byte)
            kode_sementara = "" # Reset kode sementara

    objek_bytes_hasil = bytes(list_byte_hasil)
    print(f"   [*] Ukuran data setelah dekompresi (bytes): {len(objek_bytes_hasil)}")
    return objek_bytes_hasil

# ================================================
# Fungsi Kompresi & Dekompresi File
# ================================================

def kompresi_file(path_file_input, path_file_output):
    """
    Fungsi utama untuk melakukan kompresi file.
    """
    print(f"Memulai kompresi untuk file: {path_file_input}")
    ukuran_asli = os.path.getsize(path_file_input)
    print(f"Ukuran file asli: {ukuran_asli} bytes")

    # 1. Baca data byte dari file input
    try:
        with open(path_file_input, 'rb') as f_in:
            data_asli_bytes = f_in.read()
    except FileNotFoundError:
        print(f"Error: File input '{path_file_input}' tidak ditemukan.")
        return
    except Exception as e:
        print(f"Error saat membaca file input: {e}")
        return

    if not data_asli_bytes:
        print("Error: File input kosong.")
        return

    # 2. Hitung frekuensi
    dict_frekuensi = hitung_frekuensi_byte(data_asli_bytes)

    # 3. Urutkan frekuensi
    list_frekuensi_terurut = urutkan_frekuensi(dict_frekuensi)

    # 4. Bangun dictionary kode Shannon-Fano
    print("   [*] Membangun dictionary kode Shannon-Fano...")
    dict_kode = bangun_pohon_kode_rekursif(list_frekuensi_terurut)
    print("   [*] Dictionary kode berhasil dibuat.")
    # print("   [*] Kode yang dihasilkan:", dict_kode) # Uncomment untuk debug

    # 5. Encode data asli menjadi string bit
    string_bit_encoded = encode_data(data_asli_bytes, dict_kode)

    # 6. Ubah string bit menjadi bytes (dengan padding)
    data_terkompresi_bytes, bit_padding = bits_ke_bytes(string_bit_encoded)
    ukuran_terkompresi = len(data_terkompresi_bytes)

    # 7. Simpan dictionary kode dan data terkompresi ke file output
    #    Menggunakan pickle untuk menyederhanakan penyimpanan objek Python
    data_untuk_disimpan = {
        'kode': dict_kode,
        'padding': bit_padding,
        'data': data_terkompresi_bytes
    }

    try:
        with open(path_file_output, 'wb') as f_out:
            pickle.dump(data_untuk_disimpan, f_out)
        print(f"   [*] File terkompresi berhasil disimpan ke: {path_file_output}")
    except Exception as e:
        print(f"Error saat menyimpan file output: {e}")
        return

    # 8. Tampilkan hasil
    rasio_kompresi = (ukuran_terkompresi / ukuran_asli) * 100 if ukuran_asli > 0 else 0
    faktor_kompresi = ukuran_asli / ukuran_terkompresi if ukuran_terkompresi > 0 else float('inf')
    print("-" * 30)
    print("HASIL KOMPRESI:")
    print(f"Ukuran Asli         : {ukuran_asli} bytes")
    print(f"Ukuran Terkompresi  : {ukuran_terkompresi} bytes (data inti, belum termasuk dict kode)")
    print(f"Ukuran File Output  : {os.path.getsize(path_file_output)} bytes (termasuk dict kode & padding info)")
    print(f"Rasio Kompresi     : {rasio_kompresi:.2f}% (Ukuran Terkompresi / Ukuran Asli)")
    print(f"Faktor Kompresi    : {faktor_kompresi:.2f} (Ukuran Asli / Ukuran Terkompresi)")
    print("-" * 30)


def dekompresi_file(path_file_input, path_file_output):
    """
    Fungsi utama untuk melakukan dekompresi file.
    """
    print(f"Memulai dekompresi untuk file: {path_file_input}")

    # 1. Baca data terkompresi dan dictionary kode dari file input
    try:
        with open(path_file_input, 'rb') as f_in:
            data_dibaca = pickle.load(f_in)
        dict_kode = data_dibaca['kode']
        bit_padding = data_dibaca['padding']
        data_terkompresi_bytes = data_dibaca['data']
        print("   [*] Data dari file terkompresi berhasil dibaca.")
        # print("   [*] Kode yang dibaca:", dict_kode) # Uncomment untuk debug
        # print(f"   [*] Padding yang dibaca: {bit_padding}") # Uncomment untuk debug
    except FileNotFoundError:
        print(f"Error: File input '{path_file_input}' tidak ditemukan.")
        return
    except (pickle.UnpicklingError, KeyError, EOFError) as e:
        print(f"Error: File input '{path_file_input}' sepertinya bukan file kompresi yang valid atau rusak. ({e})")
        return
    except Exception as e:
        print(f"Error saat membaca file input terkompresi: {e}")
        return

    # 2. Ubah data bytes terkompresi kembali ke string bit (hapus padding)
    string_bit_encoded = bytes_ke_bits(data_terkompresi_bytes, bit_padding)

    # 3. Decode string bit menjadi data byte asli
    data_hasil_decode_bytes = decode_data(string_bit_encoded, dict_kode)

    # 4. Simpan data hasil decode ke file output
    try:
        with open(path_file_output, 'wb') as f_out:
            f_out.write(data_hasil_decode_bytes)
        print(f"   [*] File hasil dekompresi berhasil disimpan ke: {path_file_output}")
    except Exception as e:
        print(f"Error saat menyimpan file output hasil dekompresi: {e}")
        return

    # 5. Tampilkan hasil
    print("-" * 30)
    print("HASIL DEKOMPRESI:")
    print(f"Ukuran File Input  : {os.path.getsize(path_file_input)} bytes")
    print(f"Ukuran File Output : {os.path.getsize(path_file_output)} bytes")
    print("-" * 30)


# ================================================
# Bagian Eksekusi Utama
# ================================================
if __name__ == "__main__":
    print("================================================")
    print("  Demo Kompresi/Dekompresi Shannon-Fano Sederhana ")
    print("================================================")

    while True:
        mode = input("Pilih mode (kompresi/dekompresi/keluar): ").strip().lower()

        if mode == "keluar":
            break
        elif mode == "kompresi":
            file_input = input("Masukkan path file audio WAV yang akan dikompresi: ").strip()
            file_output = input("Masukkan path untuk menyimpan file hasil kompresi (misal: audio.shnf): ").strip()
            if not file_output.endswith(".shnf"):
                 print("Warning: Nama file output disarankan berakhiran .shnf")
            kompresi_file(file_input, file_output)
            print("\n")
        elif mode == "dekompresi":
            file_input = input("Masukkan path file .shnf yang akan didekompresi: ").strip()
            file_output = input("Masukkan path untuk menyimpan file hasil dekompresi (misal: audio_hasil.wav): ").strip()
            if not file_input.endswith(".shnf"):
                 print("Warning: File input dekompresi biasanya berakhiran .shnf")
            dekompresi_file(file_input, file_output)
            print("\n")
        else:
            print("Mode tidak valid. Silakan pilih 'kompresi', 'dekompresi', atau 'keluar'.")

    print("Program selesai.")