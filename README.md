# 📝 Note-Taking App — Struktur Data

Implementasi struktur data untuk aplikasi **note-taking** menggunakan Python murni (tanpa library eksternal), mencakup tiga fitur utama sesuai requirement.

---

## 🗂️ Fitur & Struktur Data

| Fitur | Struktur Data | Keterangan |
|---|---|---|
| Multiple tags per note | **Hash Map** (`dict`) | Tiap tag memetakan ke daftar note terkait |
| Chronological & alphabetical views | **Doubly Linked List** | Node dengan pointer `prev` & `next` |
| Sync status tracking | **Circular Buffer** | Menyimpan N perubahan terbaru secara siklis |

---

## 📁 Struktur File

```
note_taking.py
├── NoteNode          # Node untuk Doubly Linked List
├── Note              # Objek utama (id, title, content, tags, sync status)
├── DoublyLinkedList  # Chronological & alphabetical view
├── CircularBuffer    # Sync status tracking (recent changes)
└── NoteManager       # Pengelola utama — menggabungkan semua struktur
```

---

## 🔧 Cara Menjalankan

```bash
python note_taking.py
```

Tidak memerlukan instalasi library tambahan. Cukup Python 3.x.

---

## 🧩 Penjelasan Struktur Data

### 1. Hash Map — Multiple Tags per Note

```python
tag_index = {
    "python":    [note1, note4, note5],
    "belajar":   [note1, note2],
    "algoritma": [note2, note5],
}
```

- Satu note dapat memiliki **banyak tag** sekaligus.
- Tiap tag menunjuk ke **daftar note** yang memilikinya.
- Pencarian note berdasarkan tag berjalan dalam **O(1)**.

---

### 2. Doubly Linked List — Chronological & Alphabetical View

```
HEAD <-> [Linked List] <-> [API REST Design] <-> [Database MySQL] <-> ... <-> TAIL
```

- Note terbaru ditambahkan di **depan** (prepend).
- Traversal maju = urutan **kronologis** (terbaru → terlama).
- Fungsi `alphabetical()` mengurutkan semua node berdasarkan **judul A-Z**.
- Penghapusan node efisien karena setiap node mengetahui `prev` dan `next`-nya.

---

### 3. Circular Buffer — Sync Status Tracking

```
Buffer kapasitas 5:
[ DELETE:id=2 | SYNC:id=3 | SYNC:id=1 | ADD:id=5 | ADD:id=4 ]
      ↑ paling baru                                  paling lama ↑
```

- Menyimpan **5 perubahan terbaru** (ADD / DELETE / SYNC).
- Ketika buffer penuh, event paling lama **otomatis tertimpa**.
- Berguna untuk fitur **undo**, **audit log**, dan **sync queue**.

---

## 🖥️ Contoh Output

```
📅 CHRONOLOGICAL VIEW (terbaru → terlama):
  1. [5] 'Linked List'     | tags: [algoritma, python] | sync: ✗
  2. [4] 'API REST Design' | tags: [python, api]        | sync: ✗
  3. [3] 'Database MySQL'  | tags: [database, sql]      | sync: ✓
  4. [1] 'Belajar Python'  | tags: [python, belajar]    | sync: ✓

🔤 ALPHABETICAL VIEW (A → Z):
  1. [4] 'API REST Design'
  2. [1] 'Belajar Python'
  3. [3] 'Database MySQL'
  4. [5] 'Linked List'

🏷️  NOTES dengan tag 'python' (3 note):
  1. [1] 'Belajar Python'
  2. [4] 'API REST Design'
  3. [5] 'Linked List'

🔁 RECENT CHANGES (Circular Buffer):
  1. [04:44:08] DELETE | id=2 | 'Algoritma Sort'
  2. [04:44:08] SYNC   | id=3 | 'Database MySQL'
  3. [04:44:08] SYNC   | id=1 | 'Belajar Python'
  4. [04:44:08] ADD    | id=5 | 'Linked List'
  5. [04:44:08] ADD    | id=4 | 'API REST Design'
```

---

## ⚙️ Kompleksitas Waktu

| Operasi | Kompleksitas |
|---|---|
| Tambah note | O(T) — T = jumlah tag |
| Hapus note | O(T + N) — N = traversal DLL |
| Cari per tag | O(1) — hash map lookup |
| Chronological view | O(N) |
| Alphabetical view | O(N log N) |
| Tambah ke circular buffer | O(1) |
| Baca recent changes | O(K) — K = kapasitas buffer |

---

## 👨‍💻 Teknologi

- **Bahasa**: Python 3.x
- **Library**: Hanya standard library (`datetime`, `time`)
- **Paradigma**: Object-Oriented Programming (OOP)
