# db/database.py
import sqlite3
from datetime import datetime
from db import DB_PATH

class TranslationDB:
    def __init__(self, db_path=None):
        self.db_path = db_path or DB_PATH

    def save_translation(self, project, source_text, target_text, source_lang, 
                        target_lang, provider, note, user=None):
        """Save translation to database"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('''
            INSERT INTO t_translations 
            (project, service_provider, source_text, target_text, source_lang, 
             target_lang, note, created_by, updated_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (project, provider, source_text, target_text, source_lang, 
              target_lang, note, user, user))
        
        conn.commit()
        conn.close()

    def get_translations(self, project=None, limit=100):
        """Get translations with optional project filter"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if project:
            c.execute('''
                SELECT * FROM t_translations 
                WHERE project = ? 
                ORDER BY created_at DESC LIMIT ?
            ''', (project, limit))
        else:
            c.execute('''
                SELECT * FROM t_translations 
                ORDER BY created_at DESC LIMIT ?
            ''', (limit,))
        
        rows = c.fetchall()
        conn.close()
        return rows

    def update_translation(self, id, target_text, note, user=None):
        """Update existing translation"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        c.execute('''
            UPDATE t_translations 
            SET target_text = ?, note = ?, updated_by = ?, updated_at = ?
            WHERE id = ?
        ''', (target_text, note, user, current_time, id))
        
        conn.commit()
        conn.close()

    def get_projects(self):
        """Get list of all projects"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute('SELECT DISTINCT project FROM t_translations ORDER BY project')
        projects = [row[0] for row in c.fetchall()]
        
        conn.close()
        return projects