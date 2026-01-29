
import sys
import os
import unittest
from datetime import datetime

# Proje kök dizinini path'e ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.repository import ActivityRepository
from models import Activity
from database.connection import init_db, get_connection

class TestDateRange(unittest.TestCase):
    def setUp(self):
        # Test için veritabanını temizle veya bellek içi kullan
        # Ancak mevcut repository connection.py üzerinden gerçek DB kullanıyor olabilir.
        # Bu test mevcut DB'yi etkileyebilir, bu yüzden dikkatli olmalıyız.
        # Güvenlik için test verilerini ekleyip sonra temizleyeceğiz.
        self.repo = ActivityRepository()
        self.created_ids = []

    def tearDown(self):
        for aid in self.created_ids:
            self.repo.delete(aid)

    def create_activity(self, name, start_date, end_date=None):
        act = Activity(None, "Test", name, start_date, "Test Comment", 5, end_date)
        self.repo.add(act)
        # ID'yi bulmak için son eklenen
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM activities")
        aid = cursor.fetchone()[0]
        conn.close()
        self.created_ids.append(aid)
        return aid

    def test_range_filtering(self):
        # Senaryo:
        # A1: 2023-01-10 (Tek Gün)
        # A2: 2023-01-20 -> 2023-02-05 (Aralık, Ocak-Şubat)
        # A3: 2023-03-01 (Mart)
        
        self.create_activity("A1", "2023-01-10")
        self.create_activity("A2", "2023-01-20", "2023-02-05")
        self.create_activity("A3", "2023-03-01")

        # Test 1: Ocak 2023 Filtresi -> A1 ve A2 gelmeli
        activities, count = self.repo.get_all_filtered(date_filter="2023-01")
        names = [a.name for a in activities if a.name in ["A1", "A2", "A3"]]
        self.assertIn("A1", names)
        self.assertIn("A2", names)
        self.assertNotIn("A3", names)
        print(f"Filter 2023-01 Results: {names}")

        # Test 2: Şubat 2023 Filtresi -> A2 gelmeli (Sadece başı ocakta ama şubata sarkıyor)
        activities, count = self.repo.get_all_filtered(date_filter="2023-02")
        names = [a.name for a in activities if a.name in ["A1", "A2", "A3"]]
        self.assertNotIn("A1", names)
        self.assertIn("A2", names) # BAŞARISIZ OLABİLİR EĞER MANTIK YANLIŞSA
        self.assertNotIn("A3", names)
        print(f"Filter 2023-02 Results: {names}")

        # Test 3: Mart 2023 Filtresi -> A3 gelmeli
        activities, count = self.repo.get_all_filtered(date_filter="2023-03")
        names = [a.name for a in activities if a.name in ["A1", "A2", "A3"]]
        self.assertNotIn("A2", names)
        self.assertIn("A3", names)
        print(f"Filter 2023-03 Results: {names}")

if __name__ == '__main__':
    unittest.main()
