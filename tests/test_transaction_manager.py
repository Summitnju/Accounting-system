# tests/test_transaction_manager.py
"""
交易管理模块单元测试
"""
import pytest
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.database import Database
from managers.transaction_manager import TransactionManager
from models.transaction import Transaction, TransactionType


@pytest.fixture
def setup_manager():
    """测试前准备：创建临时内存数据库和管理器"""
    db = Database(':memory:')  # 使用内存数据库
    manager = TransactionManager(db)
    yield manager
    db.close()


class TestTransactionManager:
    """交易管理器测试类"""
    
    def test_add_transaction_success(self, setup_manager):
        """
        测试用例 TC-TM-01：正常添加交易
        目的：验证基本的添加功能
        """
        manager = setup_manager
        trans = Transaction(
            amount=100.0,
            trans_type=TransactionType. EXPENSE,
            category_id=1,
            date=datetime.now(),
            note="测试交易"
        )
        trans_id = manager.add_transaction(trans)
        
        assert trans_id > 0, "交易ID应该大于0"
        assert len(manager.transactions) == 1, "交易列表应该有1条记录"
    
    def test_add_transaction_zero_amount(self, setup_manager):
        """
        测试用例 TC-TM-02：边界测试 - 金额为0
        """
        manager = setup_manager
        trans = Transaction(
            amount=0.0,
            trans_type=TransactionType. INCOME,
            category_id=1,
            date=datetime.now(),
            note="零金额"
        )
        trans_id = manager.add_transaction(trans)
        assert trans_id > 0
    
    def test_add_transaction_large_amount_trigger_bug(self, setup_manager):
        """
        测试用例 TC-TM-04：触发植入的空指针缺陷
        目的：验证能否检测到金额>100万时的Bug
        输入：金额=2000000
        预期：应该抛出 AttributeError（修复前）
        """
        manager = setup_manager
        trans = Transaction(
            amount=2000000.0,
            trans_type=TransactionType.INCOME,
            category_id=1,
            date=datetime.now(),
            note="大额交易"
        )
        
        # 修复前：会抛出 AttributeError:  'NoneType' object has no attribute 'to_dict'
        # 修复后：应该抛出 ValueError
        with pytest.raises((AttributeError, ValueError)) as exc_info:
            manager.add_transaction(trans)
        
        print(f"捕获到异常：{exc_info.value}")
    
    def test_delete_transaction_success(self, setup_manager):
        """
        测试用例 TC-TM-05：正常删除交易
        """
        manager = setup_manager
        trans = Transaction(
            amount=50.0,
            trans_type=TransactionType.EXPENSE,
            category_id=1,
            date=datetime.now(),
            note="待删除"
        )
        trans_id = manager.add_transaction(trans)
        
        result = manager.delete_transaction(trans_id)
        assert result == True, "删除应该返回 True"
        assert len(manager.transactions) == 0, "列表应该为空"
    
    def test_delete_nonexistent_transaction(self, setup_manager):
        """
        测试用例 TC-TM-06：删除不存在的交易
        """
        manager = setup_manager
        initial_count = len(manager.transactions)
        
        # 删除不存在的ID（可能会抛出异常，取决于实现）
        try:
            manager.delete_transaction(9999)
            # 如果没抛异常，检查列表是否不变
            assert len(manager.transactions) == initial_count
        except Exception as e:
            # 如果抛异常也是合理的
            print(f"删除不存在的记录抛出异常：{e}")
    
    def test_query_by_date_range(self, setup_manager):
        """
        测试用例 TC-TM-07：按日期范围查询
        """
        manager = setup_manager
        base_date = datetime.now()
        
        # 添加5笔不同日期的交易
        for i in range(5):
            trans = Transaction(
                amount=10.0 * (i + 1),
                trans_type=TransactionType.EXPENSE,
                category_id=1,
                date=base_date - timedelta(days=i),
                note=f"测试{i}"
            )
            manager.add_transaction(trans)
        
        # 查询最近3天的
        results = manager.query(start_date=base_date - timedelta(days=2))
        assert len(results) == 3, f"应该返回3条记录，实际返回{len(results)}条"
    
    def test_query_by_category(self, setup_manager):
        """
        测试用例 TC-TM-08：按分类查询
        """
        manager = setup_manager
        
        trans1 = Transaction(amount=50.0, trans_type=TransactionType.EXPENSE, 
                           category_id=1, date=datetime.now(), note="餐饮")
        trans2 = Transaction(amount=20.0, trans_type=TransactionType.EXPENSE, 
                           category_id=2, date=datetime.now(), note="交通")
        trans3 = Transaction(amount=80.0, trans_type=TransactionType.EXPENSE, 
                           category_id=1, date=datetime.now(), note="餐饮2")
        
        manager.add_transaction(trans1)
        manager.add_transaction(trans2)
        manager.add_transaction(trans3)
        
        results = manager.query(category_id=1)
        assert len(results) == 2, "应该返回2条分类1的记录"
    
    def test_query_by_amount_range(self, setup_manager):
        """
        测试用例 TC-TM-09：按金额范围查询
        """
        manager = setup_manager
        
        for amount in [10, 50, 100, 200, 500]: 
            trans = Transaction(
                amount=float(amount),
                trans_type=TransactionType.EXPENSE,
                category_id=1,
                date=datetime.now(),
                note=f"金额{amount}"
            )
            manager.add_transaction(trans)
        
        results = manager.query(min_amount=50, max_amount=150)
        assert len(results) == 2, f"应该返回2条记录（50和100），实际{len(results)}条"
    
    def test_query_by_keyword(self, setup_manager):
        """
        测试用例 TC-TM-10：按关键词查询
        """
        manager = setup_manager
        
        trans1 = Transaction(amount=100.0, trans_type=TransactionType.EXPENSE,
                           category_id=1, date=datetime.now(), note="午餐费用")
        trans2 = Transaction(amount=50.0, trans_type=TransactionType. EXPENSE,
                           category_id=1, date=datetime.now(), note="打车费")
        
        manager.add_transaction(trans1)
        manager.add_transaction(trans2)
        
        results = manager.query(keyword="午餐")
        assert len(results) == 1, "应该返回1条包含'午餐'的记录"