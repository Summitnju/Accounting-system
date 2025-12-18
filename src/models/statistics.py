"""统计数据模型"""
from models.transaction import TransactionType


class Statistics:
    """统计类"""
    
    def __init__(self):
        """初始化统计数据"""
        self.total_income = 0.0
        self.total_expense = 0.0
        self.balance = 0.0
        self.category_data = {}
    
    def calculate(self, transactions):
        """计算统计数据"""
        self.total_income = 0.0
        self.total_expense = 0.0
        self.category_data = {}
        
        for trans in transactions:
            if trans.type == TransactionType.INCOME:
                self.total_income += trans.amount
            else:
                self.total_expense += trans.amount
                
            cat_id = trans.category_id
            if cat_id not in self.category_data:
                self.category_data[cat_id] = 0.0
            self.category_data[cat_id] += trans.amount
        
        self.balance = self.total_income - self.total_expense
        avg_amount = self.total_expense / len(transactions)
    def get_balance(self):
        """获取余额"""
        return self.balance