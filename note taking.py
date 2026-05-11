"""
Struktur Data Aplikasi Note-Taking
===================================
Fitur:
1. Multiple tags per note      -> Hash Map (dict) + linked list per tag
2. Chronological & alphabetical views -> Doubly Linked List (sorted)
3. Sync status tracking        -> Circular Buffer untuk recent changes
"""

from datetime import datetime
import time


# ─────────────────────────────────────────────
# 1. NODE untuk Doubly Linked List
# ─────────────────────────────────────────────
class NoteNode:
    def __init__(self, note):
        self.note = note
        self.prev = None  # pointer ke note sebelumnya
        self.next = None  # pointer ke note berikutnya


# ─────────────────────────────────────────────
# 2. NOTE (objek utama)
# ─────────────────────────────────────────────
class Note:
    _id_counter = 1

    def __init__(self, title, content, tags=None):
        self.id        = Note._id_counter
        Note._id_counter += 1
        self.title     = title
        self.content   = content
        self.tags      = tags if tags else []   # multiple tags per note
        self.created   = datetime.now()
        self.synced    = False

    def __repr__(self):
        tag_str = ", ".join(self.tags) if self.tags else "-"
        sync    = "✓" if self.synced else "✗"
        return (f"[{self.id}] '{self.title}' | tags: [{tag_str}] "
                f"| sync: {sync} | {self.created.strftime('%Y-%m-%d %H:%M:%S')}")


# ─────────────────────────────────────────────
# 3. DOUBLY LINKED LIST — Chronological View
# ─────────────────────────────────────────────
class DoublyLinkedList:
    """Menyimpan note berurutan sesuai waktu insert (paling baru di depan)."""

    def __init__(self):
        self.head = None
        self.tail = None
        self.size  = 0

    def prepend(self, note):
        """Tambah note baru di depan (paling baru)."""
        node = NoteNode(note)
        if self.head is None:
            self.head = self.tail = node
        else:
            node.next  = self.head
            self.head.prev = node
            self.head  = node
        self.size += 1

    def remove(self, note_id):
        """Hapus node berdasarkan note id."""
        cur = self.head
        while cur:
            if cur.note.id == note_id:
                if cur.prev:
                    cur.prev.next = cur.next
                else:
                    self.head = cur.next
                if cur.next:
                    cur.next.prev = cur.prev
                else:
                    self.tail = cur.prev
                self.size -= 1
                return True
            cur = cur.next
        return False

    def to_list(self):
        result, cur = [], self.head
        while cur:
            result.append(cur.note)
            cur = cur.next
        return result

    def alphabetical(self):
        """Kembalikan list note diurutkan berdasarkan judul (A-Z)."""
        return sorted(self.to_list(), key=lambda n: n.title.lower())


# ─────────────────────────────────────────────
# 4. CIRCULAR BUFFER — Sync Status Tracking
# ─────────────────────────────────────────────
class CircularBuffer:
    """Menyimpan N perubahan terbaru (recent changes) untuk sync tracking."""

    def __init__(self, capacity=5):
        self.capacity = capacity
        self.buffer   = [None] * capacity
        self.head     = 0   # indeks tulis berikutnya
        self.count    = 0   # jumlah item aktif

    def push(self, event):
        """Tambah event perubahan; otomatis menimpa yang paling lama."""
        self.buffer[self.head] = event
        self.head  = (self.head + 1) % self.capacity
        self.count = min(self.count + 1, self.capacity)

    def get_recent(self):
        """Kembalikan event dari yang paling baru ke paling lama."""
        result = []
        start  = (self.head - 1) % self.capacity
        for i in range(self.count):
            idx = (start - i) % self.capacity
            result.append(self.buffer[idx])
        return result


# ─────────────────────────────────────────────
# 5. NOTE MANAGER — menggabungkan semua struktur
# ─────────────────────────────────────────────
class NoteManager:
    def __init__(self, buffer_size=5):
        self.notes     = {}               # id -> Note  (hash map)
        self.tag_index = {}               # tag -> [Note, ...]  (multi-linked by tag)
        self.dll       = DoublyLinkedList()
        self.sync_log  = CircularBuffer(buffer_size)

    # ── Tambah note ──────────────────────────
    def add_note(self, title, content, tags=None):
        note = Note(title, content, tags)
        self.notes[note.id] = note

        # index per tag (multi-linked)
        for tag in note.tags:
            self.tag_index.setdefault(tag, []).append(note)

        # tambah ke doubly linked list (kronologis)
        self.dll.prepend(note)

        # catat ke circular buffer
        self.sync_log.push({
            "action": "ADD",
            "note_id": note.id,
            "title": note.title,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        print(f"  ✅ Note ditambahkan: {note}")
        return note

    # ── Hapus note ───────────────────────────
    def delete_note(self, note_id):
        note = self.notes.pop(note_id, None)
        if not note:
            print(f"  ❌ Note id={note_id} tidak ditemukan.")
            return
        for tag in note.tags:
            self.tag_index[tag] = [n for n in self.tag_index[tag] if n.id != note_id]
        self.dll.remove(note_id)
        self.sync_log.push({
            "action": "DELETE",
            "note_id": note_id,
            "title": note.title,
            "time": datetime.now().strftime("%H:%M:%S")
        })
        print(f"  🗑️  Note dihapus: '{note.title}'")

    # ── Tandai note sebagai synced ────────────
    def mark_synced(self, note_id):
        note = self.notes.get(note_id)
        if note:
            note.synced = True
            self.sync_log.push({
                "action": "SYNC",
                "note_id": note_id,
                "title": note.title,
                "time": datetime.now().strftime("%H:%M:%S")
            })
            print(f"  🔄 Note id={note_id} berhasil di-sync.")

    # ── View: Kronologis ─────────────────────
    def view_chronological(self):
        print("\n📅 CHRONOLOGICAL VIEW (terbaru → terlama):")
        for i, note in enumerate(self.dll.to_list(), 1):
            print(f"  {i}. {note}")

    # ── View: Alfabetis ──────────────────────
    def view_alphabetical(self):
        print("\n🔤 ALPHABETICAL VIEW (A → Z):")
        for i, note in enumerate(self.dll.alphabetical(), 1):
            print(f"  {i}. {note}")

    # ── View: Per Tag ────────────────────────
    def view_by_tag(self, tag):
        notes = self.tag_index.get(tag, [])
        print(f"\n🏷️  NOTES dengan tag '{tag}' ({len(notes)} note):")
        if not notes:
            print("  (tidak ada note)")
        for i, note in enumerate(notes, 1):
            print(f"  {i}. {note}")

    # ── View: Sync Log ───────────────────────
    def view_sync_log(self):
        print("\n🔁 RECENT CHANGES (Circular Buffer):")
        events = self.sync_log.get_recent()
        if not events:
            print("  (belum ada perubahan)")
        for i, e in enumerate(events, 1):
            print(f"  {i}. [{e['time']}] {e['action']:6s} | id={e['note_id']} | '{e['title']}'")


# ─────────────────────────────────────────────
# DEMO / PENGUJIAN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 60)
    print("   DEMO APLIKASI NOTE-TAKING")
    print("=" * 60)

    nm = NoteManager(buffer_size=5)

    print("\n--- Menambahkan Notes ---")
    n1 = nm.add_note("Belajar Python",   "List, dict, class",         ["python", "belajar"])
    time.sleep(0.01)
    n2 = nm.add_note("Algoritma Sort",   "Bubble, merge, quick sort", ["algoritma", "belajar"])
    time.sleep(0.01)
    n3 = nm.add_note("Database MySQL",   "SELECT, JOIN, INDEX",       ["database", "sql"])
    time.sleep(0.01)
    n4 = nm.add_note("API REST Design",  "GET POST PUT DELETE",       ["python", "api"])
    time.sleep(0.01)
    n5 = nm.add_note("Linked List",      "Node, pointer, traversal",  ["algoritma", "python"])

    nm.view_chronological()
    nm.view_alphabetical()

    print("\n--- Cari Berdasarkan Tag ---")
    nm.view_by_tag("python")
    nm.view_by_tag("belajar")

    print("\n--- Sync Notes ---")
    nm.mark_synced(n1.id)
    nm.mark_synced(n3.id)

    print("\n--- Hapus Note ---")
    nm.delete_note(n2.id)

    nm.view_sync_log()

    print("\n--- Chronological Setelah Hapus ---")
    nm.view_chronological()

    print("\n" + "=" * 60)
    print("   SELESAI")
    print("=" * 60)