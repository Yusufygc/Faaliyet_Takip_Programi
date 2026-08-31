# tests/test_bridges.py
import sys
import os
import unittest
from datetime import datetime

# Proje dizinini ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.connection import init_db, get_db
from database.repository import ActivityRepository
from bridges.activity_bridge import ActivityBridge
from bridges.stats_bridge import StatsBridge
from bridges.plan_bridge import PlanBridge
from bridges.compare_bridge import CompareBridge
from bridges.settings_bridge import SettingsBridge


class TestBridges(unittest.TestCase):
    def setUp(self):
        init_db()
        self.repo = ActivityRepository()
        self.repo.check_and_migrate_schema()
        self.created_activity_ids = []

    def tearDown(self):
        for aid in self.created_activity_ids:
            self.repo.delete(aid)

    def test_activity_bridge_crud_and_model(self):
        bridge = ActivityBridge()
        
        # 1. Faaliyet Ekle
        success = bridge.addActivity("Film", "Bridge Test Film", "2026-08-31", "Test Comment", 8.5, "2026-09-01")
        self.assertTrue(success)

        with get_db() as conn:
            aid = conn.execute("SELECT id FROM activities WHERE name='Bridge Test Film'").fetchone()[0]
            self.created_activity_ids.append(aid)

        # 2. Get By ID
        data = bridge.getActivityById(aid)
        self.assertEqual(data["name"], "Bridge Test Film")
        self.assertEqual(data["type"], "Film")
        self.assertEqual(data["rating"], 8.5)
        self.assertEqual(data["endDate"], "2026-09-01")

        # 3. Güncelle
        upd_success = bridge.updateActivity(aid, "Film", "Bridge Test Film Updated", "2026-08-31", "Updated Comment", 9.5)
        self.assertTrue(upd_success)
        upd_data = bridge.getActivityById(aid)
        self.assertEqual(upd_data["name"], "Bridge Test Film Updated")
        self.assertEqual(upd_data["rating"], 9.5)

        # 4. Otomatik Tamamlama
        suggestions = bridge.getNameSuggestions("Bridge")
        self.assertIn("Bridge Test Film Updated", suggestions)

        # 5. Silme
        del_success = bridge.deleteActivity(aid)
        self.assertTrue(del_success)
        self.assertIsNone(bridge.getActivityById(aid).get("id"))
        self.created_activity_ids.remove(aid)

    def test_stats_bridge(self):
        bridge = ActivityBridge()
        stats_bridge = StatsBridge()

        # Test verisi ekle
        bridge.addActivity("Kitap", "Stats Test Kitap", "2026-08-10", "", 7.0)
        with get_db() as conn:
            aid = conn.execute("SELECT id FROM activities WHERE name='Stats Test Kitap'").fetchone()[0]
            self.created_activity_ids.append(aid)

        stats_bridge.loadStats("2026-08", False, False)
        self.assertGreaterEqual(stats_bridge.kpiTotal, 1)
        self.assertGreater(len(stats_bridge.categoryDistribution), 0)

        # Trend analizi testi
        stats_bridge.loadTrend(2026, "Hepsi")
        self.assertGreaterEqual(stats_bridge.trendTotal, 1)
        self.assertEqual(len(stats_bridge.trendData), 12)

        month_details = stats_bridge.getMonthDetails("2026-08", "Hepsi")
        self.assertGreaterEqual(len(month_details), 1)

        # Sayfa boyutu testi
        bridge.setItemsPerPage(30)
        self.assertEqual(bridge.pageSize, 30)

        pdf_path = stats_bridge.getDefaultPdfPath("2026-08")
        self.assertTrue(pdf_path.endswith(".pdf"))

    def test_plan_bridge(self):
        plan_bridge = PlanBridge()
        
        # Klasör ekle
        f_success = plan_bridge.addFolder("Test Klasörü")
        self.assertTrue(f_success)
        
        folders = [f for f in plan_bridge.folders if f["name"] == "Test Klasörü"]
        self.assertTrue(len(folders) > 0)
        folder_id = folders[0]["id"]

        # Plan ekle
        p_success = plan_bridge.addPlan("Test Hedefi", "Açıklama", "monthly", 2026, 8, "high", folder_id)
        self.assertTrue(p_success)

        # Plan güncelle
        plans = plan_bridge._repo.get_plans(folder_id=folder_id)
        self.assertTrue(len(plans) > 0)
        plan_id = plans[0].id

        plan_bridge.updateProgress(plan_id, 100)
        p_updated = plan_bridge.getPlanById(plan_id)
        self.assertEqual(p_updated["status"], "completed")
        self.assertEqual(p_updated["progress"], 100)

        # Temizle
        plan_bridge.deletePlan(plan_id)
        plan_bridge.deleteFolder(folder_id)

    def test_settings_bridge(self):
        settings_bridge = SettingsBridge()
        
        t_success = settings_bridge.addType("TestOzelKategori")
        self.assertTrue(t_success)
        self.assertIn("TestOzelKategori", settings_bridge.typesList)

        d_success = settings_bridge.deleteType("TestOzelKategori")
        self.assertTrue(d_success)
        self.assertNotIn("TestOzelKategori", settings_bridge.typesList)


if __name__ == '__main__':
    unittest.main()
