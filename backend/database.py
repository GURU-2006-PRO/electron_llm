"""
SQLite Database for Chat History Storage
Stores queries, responses, and metadata persistently
"""

import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Optional
import os


class ChatDatabase:
    """SQLite database manager for chat history"""
    
    def __init__(self, db_path='data/chat_history.db'):
        """Initialize database connection and create tables"""
        # Ensure data directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        self.create_tables()
        print(f"[OK] Chat database initialized: {db_path}")
    
    def create_tables(self):
        """Create database tables if they don't exist"""
        cursor = self.conn.cursor()
        
        # Chat history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT NOT NULL,
                response TEXT,
                model TEXT,
                advanced_mode BOOLEAN DEFAULT 0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                bookmarked BOOLEAN DEFAULT 0,
                data_rows INTEGER DEFAULT 0,
                chart_type TEXT,
                execution_time REAL
            )
        ''')
        
        # Conversation sessions table (for grouping related queries)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_name TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                last_activity DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tags table (for categorizing queries)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                history_id INTEGER,
                tag TEXT,
                FOREIGN KEY (history_id) REFERENCES chat_history(id)
            )
        ''')
        
        # Create indexes for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON chat_history(timestamp DESC)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_bookmarked ON chat_history(bookmarked)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_model ON chat_history(model)')
        
        self.conn.commit()
        print("[OK] Database tables created/verified")
    
    def add_query(self, query: str, response: str = None, model: str = None, 
                  advanced_mode: bool = False, data_rows: int = 0, 
                  chart_type: str = None, execution_time: float = None) -> int:
        """
        Add a new query to chat history
        
        Args:
            query: User's query text
            response: AI response text
            model: Model used (deepseek-r1, gemini-flash, etc.)
            advanced_mode: Whether advanced mode was enabled
            data_rows: Number of data rows returned
            chart_type: Type of chart generated (if any)
            execution_time: Query execution time in seconds
        
        Returns:
            ID of inserted record
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO chat_history 
            (query, response, model, advanced_mode, data_rows, chart_type, execution_time)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (query, response, model, advanced_mode, data_rows, chart_type, execution_time))
        
        self.conn.commit()
        return cursor.lastrowid
    
    def get_history(self, limit: int = 50, offset: int = 0, 
                    bookmarked_only: bool = False) -> List[Dict]:
        """
        Get chat history with pagination
        
        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip
            bookmarked_only: Only return bookmarked queries
        
        Returns:
            List of history records as dictionaries
        """
        cursor = self.conn.cursor()
        
        query = '''
            SELECT id, query, response, model, advanced_mode, 
                   timestamp, bookmarked, data_rows, chart_type, execution_time
            FROM chat_history
        '''
        
        if bookmarked_only:
            query += ' WHERE bookmarked = 1'
        
        query += ' ORDER BY timestamp DESC LIMIT ? OFFSET ?'
        
        cursor.execute(query, (limit, offset))
        rows = cursor.fetchall()
        
        return [dict(row) for row in rows]
    
    def get_recent_history(self, limit: int = 10) -> List[Dict]:
        """Get most recent queries (for quick access)"""
        return self.get_history(limit=limit)
    
    def search_history(self, search_term: str, limit: int = 50) -> List[Dict]:
        """
        Search chat history by query text
        
        Args:
            search_term: Text to search for in queries
            limit: Maximum results to return
        
        Returns:
            List of matching history records
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, query, response, model, advanced_mode, 
                   timestamp, bookmarked, data_rows, chart_type, execution_time
            FROM chat_history
            WHERE query LIKE ? OR response LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{search_term}%', f'%{search_term}%', limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def toggle_bookmark(self, history_id: int) -> bool:
        """
        Toggle bookmark status for a query
        
        Args:
            history_id: ID of the history record
        
        Returns:
            New bookmark status (True/False)
        """
        cursor = self.conn.cursor()
        
        # Get current status
        cursor.execute('SELECT bookmarked FROM chat_history WHERE id = ?', (history_id,))
        row = cursor.fetchone()
        
        if row is None:
            return False
        
        new_status = not row['bookmarked']
        
        # Update status
        cursor.execute('UPDATE chat_history SET bookmarked = ? WHERE id = ?', 
                      (new_status, history_id))
        self.conn.commit()
        
        return new_status
    
    def delete_query(self, history_id: int) -> bool:
        """
        Delete a query from history
        
        Args:
            history_id: ID of the history record
        
        Returns:
            True if deleted, False if not found
        """
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM chat_history WHERE id = ?', (history_id,))
        self.conn.commit()
        
        return cursor.rowcount > 0
    
    def clear_history(self, keep_bookmarked: bool = True) -> int:
        """
        Clear chat history
        
        Args:
            keep_bookmarked: If True, keep bookmarked queries
        
        Returns:
            Number of records deleted
        """
        cursor = self.conn.cursor()
        
        if keep_bookmarked:
            cursor.execute('DELETE FROM chat_history WHERE bookmarked = 0')
        else:
            cursor.execute('DELETE FROM chat_history')
        
        self.conn.commit()
        return cursor.rowcount
    
    def get_statistics(self) -> Dict:
        """
        Get usage statistics
        
        Returns:
            Dictionary with statistics
        """
        cursor = self.conn.cursor()
        
        stats = {}
        
        # Total queries
        cursor.execute('SELECT COUNT(*) as total FROM chat_history')
        stats['total_queries'] = cursor.fetchone()['total']
        
        # Bookmarked queries
        cursor.execute('SELECT COUNT(*) as total FROM chat_history WHERE bookmarked = 1')
        stats['bookmarked_queries'] = cursor.fetchone()['total']
        
        # Queries by model
        cursor.execute('''
            SELECT model, COUNT(*) as count 
            FROM chat_history 
            WHERE model IS NOT NULL
            GROUP BY model
        ''')
        stats['queries_by_model'] = {row['model']: row['count'] for row in cursor.fetchall()}
        
        # Average execution time
        cursor.execute('SELECT AVG(execution_time) as avg_time FROM chat_history WHERE execution_time IS NOT NULL')
        avg_time = cursor.fetchone()['avg_time']
        stats['avg_execution_time'] = round(avg_time, 2) if avg_time else 0
        
        # Most recent query
        cursor.execute('SELECT timestamp FROM chat_history ORDER BY timestamp DESC LIMIT 1')
        row = cursor.fetchone()
        stats['last_query_time'] = row['timestamp'] if row else None
        
        return stats
    
    def export_history(self, filepath: str = 'chat_history_export.json'):
        """
        Export chat history to JSON file
        
        Args:
            filepath: Path to export file
        """
        history = self.get_history(limit=10000)  # Export all
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
        
        return len(history)
    
    def import_from_localstorage(self, localstorage_data: List[Dict]) -> int:
        """
        Import history from localStorage format
        
        Args:
            localstorage_data: List of history items from localStorage
        
        Returns:
            Number of records imported
        """
        count = 0
        for item in localstorage_data:
            try:
                self.add_query(
                    query=item.get('query', ''),
                    response=None,
                    model=None,
                    advanced_mode=False,
                    data_rows=0
                )
                
                # Set timestamp if provided
                if 'timestamp' in item:
                    cursor = self.conn.cursor()
                    cursor.execute(
                        'UPDATE chat_history SET timestamp = ? WHERE id = ?',
                        (datetime.fromtimestamp(item['timestamp'] / 1000), cursor.lastrowid)
                    )
                
                # Set bookmark if provided
                if item.get('bookmarked', False):
                    cursor = self.conn.cursor()
                    cursor.execute(
                        'UPDATE chat_history SET bookmarked = 1 WHERE id = ?',
                        (cursor.lastrowid,)
                    )
                
                count += 1
            except Exception as e:
                print(f"[WARNING] Failed to import item: {e}")
                continue
        
        self.conn.commit()
        return count
    
    def close(self):
        """Close database connection"""
        self.conn.close()
        print("[OK] Database connection closed")


# Singleton instance
_db_instance = None

def get_database() -> ChatDatabase:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = ChatDatabase()
    return _db_instance
