# db/schema.py
import sqlite3
from datetime import datetime
from db import DB_PATH

def init_db():
    """Initialize SQLite database and create table if it doesn't exist"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create the translations table with new schema
    c.execute('''
        CREATE TABLE IF NOT EXISTS t_translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project TEXT NOT NULL,
            service_provider TEXT NOT NULL,
            source_text TEXT NOT NULL,
            target_text TEXT, 
            source_lang TEXT,
            target_lang TEXT,
            note TEXT,
            created_by TEXT,
            updated_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Create index on project for faster lookups
    c.execute('''
        CREATE INDEX IF NOT EXISTS idx_translations_project 
        ON t_translations(project)
    ''')
    
    conn.commit()
    conn.close()

# def migrate_existing_data():
#     """Migrate data from old schema to new schema if needed"""
#     conn = sqlite3.connect('trans.sqlite3')
#     c = conn.cursor()
    
#     # Check if old data exists (without project column)
#     c.execute("PRAGMA table_info(t_translations)")
#     columns = [col[1] for col in c.fetchall()]
    
#     if 'project' not in columns:
#         # Backup old data
#         c.execute('''
#             CREATE TABLE IF NOT EXISTS t_translations_backup AS 
#             SELECT * FROM t_translations
#         ''')
        
#         # Drop old table
#         c.execute('DROP TABLE t_translations')
        
#         # Create new table
#         init_db()
        
#         # Migrate data with default project name
#         c.execute('''
#             INSERT INTO t_translations (
#                 project, service_provider, source_text, target_text, 
#                 source_lang, target_lang, note, created_at
#             )
#             SELECT 
#                 'Default Project' as project,
#                 service_provider,
#                 source_text,
#                 target_text,
#                 source_lang,
#                 target_lang,
#                 note,
#                 created_at
#             FROM t_translations_backup
#         ''')
        
#         conn.commit()
    
#     conn.close()