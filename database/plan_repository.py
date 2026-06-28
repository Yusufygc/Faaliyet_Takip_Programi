# database/plan_repository.py
from .connection import get_db
from models import Plan, Folder
from logger_setup import logger


class PlanRepository:
    """Plan, hedef ve klasör işlemleri için veritabanı sınıfı."""

    def __init__(self):
        self.ensure_folders_table_exists()
        self.ensure_plans_table_exists()

    # --- Klasör (Folder) İşlemleri ---

    def ensure_folders_table_exists(self):
        """Folders tablosunu oluşturur."""
        sql = '''
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        '''
        try:
            with get_db() as conn:
                conn.execute(sql)
        except Exception as e:
            logger.error(f"Hata (PlanRepository.ensure_folders_table_exists): {e}")

    def get_folders(self) -> list:
        """Tüm klasörleri getirir."""
        sql = "SELECT id, name, created_at FROM folders ORDER BY name"
        try:
            with get_db() as conn:
                return [Folder.from_row(row) for row in conn.execute(sql).fetchall()]
        except Exception as e:
            logger.error(f"Hata (PlanRepository.get_folders): {e}")
            return []

    def add_folder(self, name: str) -> bool:
        """Yeni klasör ekler."""
        try:
            with get_db() as conn:
                conn.execute("INSERT INTO folders (name) VALUES (?)", (name,))
            return True
        except Exception as e:
            logger.error(f"Hata (PlanRepository.add_folder): {e}")
            return False

    def update_folder(self, folder_id: int, name: str) -> bool:
        """Klasör ismini günceller."""
        try:
            with get_db() as conn:
                conn.execute("UPDATE folders SET name=? WHERE id=?", (name, folder_id))
            return True
        except Exception as e:
            logger.error(f"Hata (PlanRepository.update_folder): {e}")
            return False

    def delete_folder(self, folder_id: int) -> bool:
        """Klasörü siler. İçindeki planların folder_id'si NULL olur (ON DELETE SET NULL)."""
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM folders WHERE id=?", (folder_id,))
            return True
        except Exception as e:
            logger.error(f"Hata (PlanRepository.delete_folder): {e}")
            return False

    # --- Plan / Hedef İşlemleri ---

    def ensure_plans_table_exists(self):
        """Plans tablosunu oluşturur."""
        sql = '''
            CREATE TABLE IF NOT EXISTS plans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                scope TEXT NOT NULL,
                year INTEGER NOT NULL,
                month INTEGER,
                status TEXT DEFAULT 'planned',
                progress INTEGER DEFAULT 0,
                priority TEXT DEFAULT 'medium',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                folder_id INTEGER REFERENCES folders(id) ON DELETE SET NULL
            )
        '''
        try:
            with get_db() as conn:
                conn.execute(sql)
        except Exception as e:
            logger.error(f"Hata (PlanRepository.ensure_plans_table_exists): {e}")

    def add_plan(self, plan: Plan) -> bool:
        """Yeni plan ekler."""
        sql = '''
            INSERT INTO plans (title, description, scope, year, month, status, progress, priority, created_at, folder_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        try:
            with get_db() as conn:
                conn.execute(sql, (
                    plan.title, plan.description, plan.scope, plan.year, plan.month,
                    plan.status, plan.progress, plan.priority, plan.created_at, plan.folder_id
                ))
            return True
        except Exception as e:
            logger.error(f"Hata (PlanRepository.add_plan): {e}")
            return False

    def update_plan(self, plan: Plan) -> bool:
        """Planı günceller."""
        sql = '''
            UPDATE plans
            SET title=?, description=?, status=?, progress=?, priority=?, folder_id=?
            WHERE id=?
        '''
        try:
            with get_db() as conn:
                conn.execute(sql, (
                    plan.title, plan.description, plan.status,
                    plan.progress, plan.priority, plan.folder_id, plan.id
                ))
            return True
        except Exception as e:
            logger.error(f"Hata (PlanRepository.update_plan): {e}")
            return False

    def update_plan_progress(self, plan_id: int, progress: int, status: str) -> bool:
        """Sadece ilerleme ve durumu günceller."""
        try:
            with get_db() as conn:
                conn.execute("UPDATE plans SET progress=?, status=? WHERE id=?", (progress, status, plan_id))
            return True
        except Exception as e:
            logger.error(f"Hata (PlanRepository.update_plan_progress): {e}")
            return False

    def delete_plan(self, plan_id: int) -> bool:
        """Planı siler."""
        try:
            with get_db() as conn:
                conn.execute("DELETE FROM plans WHERE id=?", (plan_id,))
            return True
        except Exception as e:
            logger.error(f"Hata (PlanRepository.delete_plan): {e}")
            return False

    def get_plans(self, scope: str, year: int, month: int = None) -> list:
        """Filtreye göre planları getirir."""
        query = (
            "SELECT id, title, description, scope, year, month, status, progress, priority, created_at, folder_id "
            "FROM plans WHERE scope=? AND year=?"
        )
        params = [scope, year]

        if scope == 'monthly' and month is not None:
            query += " AND month=?"
            params.append(month)

        query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END, id DESC"

        try:
            with get_db() as conn:
                return [Plan.from_row(row) for row in conn.execute(query, params).fetchall()]
        except Exception as e:
            logger.error(f"Hata (PlanRepository.get_plans): {e}")
            return []
