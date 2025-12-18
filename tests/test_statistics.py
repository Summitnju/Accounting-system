# tests/test_statistics.py
"""
统计模块单元测试
"""
import pytest
from datetime import datetime
import sys
import os

sys. path.insert(0, os. path.join(os.path. dirname(__file__), '..', 'src'))

from models.statistics import Statistics
from models. transaction import Transaction, TransactionType


class TestStatistics:
    """统计模块测试类"""
    
    def test_statistics_empty_list_trigger_bug(self):
        """
        测试用例 TC-ST-01：触发植入的除以零缺陷
        目的：验证能否检测到空列表的 Bug
        输入：空列表
        预期：应该抛出 ZeroDivisionError（修复前）
        """
        stats = Statistics()
        
        # 修复前：会抛出 ZeroDivisionError
        # 修复后：应该正常处理，返回默认值
        try:
            stats.calculate([])
            # 修复后应该到这里
            assert stats.total_expense == 0.0
            assert stats.total_income == 0.0
            print("✓ 缺陷已修复：空列表被正确处理")
        except ZeroDivisionError: 
            # 修复前会到这里
            pytest.fail("检测到除以零错误，这是植入的缺陷，需要修复")
    
    def test_statistics_single_transaction(self):
        """
        测试用例 TC-ST-02：单笔交易统计
        """
        stats = Statistics()
        trans = Transaction(
            amount=100.0,
            trans_type=TransactionType.EXPENSE,
            category_id=1,
            date=datetime.now(),
            note="测试"
        )
        stats.calculate([trans])
        
        assert stats.total_expense == 100.0, "支出应该是100"
        assert stats.total_income == 0.0, "收入应该是0"
    
    def test_statistics_mixed_transactions(self):
        """
        测试用例 TC-ST-03：混合收支统计
        """
        stats = Statistics()
        trans_list = [
            Transaction(amount=5000.0, trans_type=TransactionType.INCOME, 
                       category_id=1, date=datetime.now(), note="工资"),
            Transaction(amount=2000.0, trans_type=TransactionType.EXPENSE, 
                       category_id=2, date=datetime.now(), note="房租"),
            Transaction(amount=500.0, trans_type=TransactionType.EXPENSE, 
                       category_id=3, date=datetime.now(), note="餐饮")
        ]
        stats.calculate(trans_list)
        
        assert stats. total_income == 5000.0
        assert stats.total_expense == 2500.0
        assert stats.balance == 2500.0
    
    def test_statistics_only_income(self):
        """
        测试用例 TC-ST-04：仅收入统计
        """
        stats = Statistics()
        trans_list = [
            Transaction(amount=3000.0, trans_type=TransactionType.INCOME,
                       category_id=1, date=datetime.now(), note="工资"),
            Transaction(amount=5000.0, trans_type=TransactionType.INCOME,
                       category_id=1, date=datetime.now(), note="奖金"),
            Transaction(amount=2000.0, trans_type=TransactionType.INCOME,
                       category_id=1, date=datetime.now(), note="其他")
        ]
        stats.calculate(trans_list)
        
        assert stats.total_income == 10000.0
        assert stats. total_expense == 0.0
        assert stats.balance == 10000.0
    
    def test_statistics_only_expense(self):
        """
        测试用例 TC-ST-05：仅支出统计
        """
        stats = Statistics()
        trans_list = [
            Transaction(amount=100.0, trans_type=TransactionType.EXPENSE,
                       category_id=i, date=datetime.now(), note=f"支出{i}")
            for i in range(1, 6)
        ]
        stats.calculate(trans_list)
        
        assert stats. total_expense == 500.0
        assert stats.total_income == 0.0
        assert stats.balance == -500.0
    
    def test_statistics_large_amount(self):
        """
        测试用例 TC-ST-06：大额交易统计
        """
        stats = Statistics()
        trans = Transaction(amount=1000000.0, trans_type=TransactionType.INCOME,
                          category_id=1, date=datetime.now(), note="大额")
        stats.calculate([trans])
        
        assert stats.total_income == 1000000.0
    
    def test_statistics_small_decimal(self):
        """
        测试用例 TC-ST-07：小数精度测试
        """
        stats = Statistics()
        trans = Transaction(amount=0.01, trans_type=TransactionType.EXPENSE,
                          category_id=1, date=datetime.now(), note="测试")
        stats.calculate([trans])
        
        assert abs(stats.total_expense - 0.01) < 0.0001
    
    def test_statistics_category_data(self):
        """
        测试用例 TC-ST-08：分类统计
        """
        stats = Statistics()
        trans_list = [
            Transaction(amount=50.0, trans_type=TransactionType.EXPENSE,
                       category_id=1, date=datetime.now(), note="餐饮1"),
            Transaction(amount=80.0, trans_type=TransactionType.EXPENSE,
                       category_id=1, date=datetime.now(), note="餐饮2"),
            Transaction(amount=120.0, trans_type=TransactionType.EXPENSE,
                       category_id=2, date=datetime.now(), note="交通")
        ]
        stats.calculate(trans_list)
        
        assert stats.category_data. get(1) == 130.0, "分类1应该是130"
        assert stats.category_data. get(2) == 120.0, "分类2应该是120"
    
    def test_statistics_performance_large_dataset(self):
        """
        测试用例 TC-ST-09：性能测试
        """
        import time
        stats = Statistics()
        
        trans_list = [
            Transaction(amount=float(i), trans_type=TransactionType.EXPENSE,
                       category_id=1, date=datetime.now(), note=f"测试{i}")
            for i in range(1, 1001)
        ]
        
        start_time = time.time()
        stats.calculate(trans_list)
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 1.0, f"处理时间过长：{elapsed_time}秒"
        assert stats.total_expense == sum(range(1, 1001))