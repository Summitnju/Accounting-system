"""交易记录模型"""
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    """交易类型枚举"""
    INCOME = "收入"
    EXPENSE = "支出"


class Transaction:
    """交易记录类 - 对应UML类图中的Transaction类"""
    
    def __init__(self, transaction_id=None, amount=0.0, 
                 trans_type=TransactionType.EXPENSE,
                 category_id=None, date=None, note=""):
        """
        初始化交易记录
        
        Args:
            transaction_id: 交易ID
            amount: 金额
            trans_type: 交易类型
            category_id: 分类ID
            date: 日期
            note: 备注
        """
        self.id = transaction_id
        self.amount = amount
        self.type = trans_type
        self.category_id = category_id
        self.date = date or datetime.now()
        self.note = note
    
    def get_amount(self):
        """获取金额 - 对应UML中的getAmount()方法"""
        return self.amount
    
    def get_type(self):
        """获取类型 - 对应UML中的getType()方法"""
        return self.type
    
    def get_date(self):
        """获取日期 - 对应UML中的getDate()方法"""
        return self.date
    
    def to_dict(self):
        """转换为字典用于数据库存储"""
        return {
            'id': self.id,
            'amount': self.amount,
            'type': self.type.value,
            'category_id': self.category_id,
            'date': self.date.strftime('%Y-%m-%d %H:%M:%S'),
            'note': self.note
        }