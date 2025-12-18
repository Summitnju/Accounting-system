"""数据库管理模块 - 对应UML组件图中的Database组件"""
import sqlite3
import os

class Database:
    """数据库类 - 对应UML类图中的Database类"""
    
    def __init__(self, db_path='accounting.db'):
        """初始化数据库连接"""
        self.db_path = db_path
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """初始化数据库表"""
        db_path = self.db_path.strip()
        
        if db_path == ':memory:':
            # 内存数据库
            self.conn = sqlite3.connect(':memory:')
        else:
            # 文件数据库，确保目录存在
            db_dir = os.path.dirname(db_path)
            if db_dir and not os.path. exists(db_dir):
                os.makedirs(db_dir)
            self.conn = sqlite3.connect(db_path)
        
        cursor = self.conn.cursor()
        
        # 创建交易表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                category_id INTEGER,
                date TEXT NOT NULL,
                note TEXT
            )
        ''')
        
        # 创建分类表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                icon TEXT,
                type TEXT,
                is_predefined INTEGER DEFAULT 0
            )
        ''')
        
        self.conn.commit()
        self._init_predefined_categories()
    
    def _init_predefined_categories(self):
        """初始化预定义分类"""
        cursor = self.conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM categories')
        if cursor.fetchone()[0] == 0:
            predefined = [
                ('餐饮', '🍜', '支出', 1),
                ('交通', '🚇', '支出', 1),
                ('购物', '🛒', '支出', 1),
                ('娱乐', '🎬', '支出', 1),
                ('医疗', '🏥', '支出', 1),
                ('工资', '💰', '收入', 1),
                ('奖金', '🎁', '收入', 1),
            ]
            cursor.executemany(
                'INSERT INTO categories (name, icon, type, is_predefined) '
                'VALUES (?, ?, ?, ?)',
                predefined
            )
            self.conn.commit()
    
    def save(self, table, data):
        """
        保存数据 - 对应UML中的save()方法
        
        Args:
            table: 表名
            data: 数据字典
        
        Returns:
            插入的记录ID
        """
        cursor = self.conn.cursor()
        
        if table == 'transactions':
            cursor.execute(
                'INSERT INTO transactions (amount, type, category_id, date, note) '
                'VALUES (?, ?, ?, ?, ?)',
                (data['amount'], data['type'], data['category_id'], 
                 data['date'], data.get('note', ''))
            )
        elif table == 'categories':
            cursor.execute(
                'INSERT INTO categories (name, icon, type, is_predefined) '
                'VALUES (?, ?, ?, ?)',
                (data['name'], data.get('icon', ''), 
                 data.get('type'), data.get('is_predefined', 0))
            )
        
        self.conn.commit()
        return cursor.lastrowid
    
    def load(self, table, condition=None):
        """
        加载数据 - 对应UML中的load()方法
        
        Args:
            table: 表名
            condition: 查询条件（可选）
        
        Returns:
            查询结果列表
        """
        cursor = self.conn.cursor()
        
        if condition:
            query = f'SELECT * FROM {table} WHERE {condition}'
        else:
            query = f'SELECT * FROM {table}'
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        results = []
        
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
        
        return results
    def delete(self, table, record_id):
        """删除记录"""
        cursor = self.conn.cursor()
        sql = f"DELETE FROM {table} WHERE id = {record_id}" 
        cursor.execute(sql)
        self.conn.commit()
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()