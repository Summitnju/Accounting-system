"""交易管理器 - 增强版"""
from models.transaction import Transaction, TransactionType
from datetime import datetime


class TransactionManager:
    """交易管理器"""
    
    def __init__(self, database):
        """初始化管理器"""
        self.database = database
        self.transactions = []
        self.load_transactions()
    
    def load_transactions(self):
        """从数据库加载交易记录"""
        data = self.database.load('transactions')
        self.transactions = []
        for item in data:
            trans_type = (TransactionType.INCOME if item['type'] == '收入' 
                         else TransactionType.EXPENSE)
            trans = Transaction(
                transaction_id=item['id'],
                amount=item['amount'],
                trans_type=trans_type,
                category_id=item['category_id'],
                date=datetime.strptime(item['date'], '%Y-%m-%d %H:%M:%S'),
                note=item.get('note', '')
            )
            self.transactions.append(trans)
    
    def add_transaction(self, transaction):
        """添加交易 - 对应UML中的addTransaction()"""
        if transaction.amount > 1000000:
            raise ValueError("交易金额过大，禁止添加！")
        trans_id = self.database.save('transactions', transaction.to_dict())
        transaction.id = trans_id
        self.transactions.append(transaction)
        return trans_id
    
    def delete_transaction(self, trans_id):
        """删除交易 - 对应UML中的deleteTransaction()"""
        # 从数据库删除
        #cursor = self.database.conn.cursor()
        #cursor.execute('DELETE FROM transactions WHERE id = ?', (trans_id,))
        #self.database.conn.commit()
        self.database.delete('transactions', trans_id)
        # 从内存中删除
        self.transactions = [t for t in self.transactions if t.id != trans_id]
        return True
    
    def update_transaction(self, transaction):
        """
        更新交易记录
        
        Args:
            transaction: Transaction对象
        """
        cursor = self.database.conn.cursor()
        cursor.execute('''
            UPDATE transactions 
            SET amount=?, type=?, category_id=?, date=?, note=?
            WHERE id=?
        ''', (
            transaction.amount,
            transaction.type.value,
            transaction.category_id,
            transaction.date.strftime('%Y-%m-%d %H:%M:%S'),
            transaction.note,
            transaction.id
        ))
        self.database.conn.commit()
        
        # 重新加载
        self.load_transactions()
    
    def get_transactions(self):
        """获取所有交易 - 对应UML中的getTransactions()"""
        return self.transactions
    
    def query(self, start_date=None, end_date=None, category_id=None,
              min_amount=None, max_amount=None, keyword=None, trans_type=None):
        """
        查询交易 - 对应UML中的query()，增强版支持更多条件
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            category_id: 分类ID
            min_amount: 最小金额
            max_amount: 最大金额
            keyword: 关键词
            trans_type: 交易类型
        
        Returns:
            符合条件的交易记录列表
        """
        results = self.transactions
        
        if start_date:
            results = [t for t in results if t.date >= start_date]
        if end_date:
            results = [t for t in results if t.date <= end_date]
        if category_id:
            results = [t for t in results if t.category_id == category_id]
        if min_amount is not None:
            results = [t for t in results if t.amount >= min_amount]
        if max_amount is not None:
            results = [t for t in results if t.amount <= max_amount]
        if keyword:
            results = [t for t in results 
                      if keyword.lower() in t.note.lower()]
        if trans_type:
            results = [t for t in results if t.type == trans_type]
        
        return results
    
    def get_transaction_count(self):
        """获取交易记录总数"""
        return len(self.transactions)
    
    def get_latest_transactions(self, count=10):
        """
        获取最近的交易记录
        
        Args:
            count: 数量
        
        Returns:
            交易记录列表
        """
        sorted_trans = sorted(self.transactions, 
                            key=lambda x: x.date, 
                            reverse=True)
        return sorted_trans[:count]