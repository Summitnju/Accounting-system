# tests/test_integration.py
"""
集成测试
"""
import pytest
from datetime import datetime
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database.database import Database
from managers.transaction_manager import TransactionManager
from managers.category_manager import CategoryManager
from managers.export_manager import ExportManager
from models.transaction import Transaction, TransactionType


class TestIntegration:
    """集成测试类"""
    
    def test_integration_full_workflow(self):
        """
        集成测试 IT-01：完整工作流测试
        """
        # 步骤1：初始化
        db = Database(':memory:')
        manager = TransactionManager(db)
        
        # 步骤2：添加交易
        trans = Transaction(
            amount=100.0,
            trans_type=TransactionType.EXPENSE,
            category_id=1,
            date=datetime.now(),
            note="集成测试"
        )
        trans_id = manager.add_transaction(trans)
        assert trans_id > 0, "添加失败"
        print(f"✓ 步骤1通过：成功添加交易，ID={trans_id}")
        
        # 步骤3：查询验证
        results = manager.query(keyword="集成测试")
        assert len(results) == 1, "查询结果数量不对"
        assert results[0]. amount == 100.0, "查询到的金额不对"
        print(f"✓ 步骤2通过：成功查询到交易")
        
        # 步骤4：删除
        result = manager.delete_transaction(trans_id)
        assert result == True, "删除失败"
        assert len(manager.transactions) == 0, "删除后列表应为空"
        print(f"✓ 步骤3通过：成功删除交易")
        
        # 步骤5：再次查询确认
        results = manager.query(keyword="集成测试")
        assert len(results) == 0, "删除后仍能查到数据"
        print(f"✓ 步骤4通过：确认删除成功")
        
        db.close()
        print("\n✅ 集成测试1：完整工作流 - 通过")
    
    def test_integration_export_and_verify(self):
        """
        集成测试 IT-02：数据导出与验证
        """
        import csv
        
        # 步骤1：准备数据
        db = Database(':memory:')
        trans_mgr = TransactionManager(db)
        cat_mgr = CategoryManager(db)
        export_mgr = ExportManager(trans_mgr, cat_mgr)
        
        test_data = [
            (50.0, "早餐"),
            (20.0, "打车"),
            (200.0, "买衣服")
        ]
        
        for amount, note in test_data: 
            trans = Transaction(
                amount=amount,
                trans_type=TransactionType.EXPENSE,
                category_id=1,
                date=datetime.now(),
                note=note
            )
            trans_mgr. add_transaction(trans)
        
        assert len(trans_mgr.transactions) == 3, "数据准备失败"
        print(f"✓ 步骤1通过：准备了3笔测试数据")
        
        # 步骤2：导出到 CSV
        export_filename = 'test_integration_export.csv'
        result = export_mgr.export_to_csv(export_filename, trans_mgr.transactions)
        assert result == True, "导出失败"
        print(f"✓ 步骤2通过：成功导出到 {export_filename}")
        
        # 步骤3：验证文件存在
        assert os.path. exists(export_filename), "导出文件不存在"
        print(f"✓ 步骤3通过：文件存在")
        
        # 步骤4：读取并验证数据
        with open(export_filename, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 3, f"文件中应该有3行数据，实际{len(rows)}行"
        print(f"✓ 步骤4通过：文件包含3行数据")
        
        # 步骤5：清理
        os.remove(export_filename)
        db.close()
        print("\n✅ 集成测试2：导出验证 - 通过")
    
    def test_integration_statistics_with_real_data(self):
        """
        集成测试 IT-03：真实数据的统计计算
        """
        from models.statistics import Statistics
        
        # 步骤1：构建真实场景数据
        db = Database(':memory:')
        manager = TransactionManager(db)
        
        # 模拟一个月的收支
        monthly_data = [
            (TransactionType.INCOME, 8000.0, "工资"),
            (TransactionType.EXPENSE, 2000.0, "房租"),
            (TransactionType. EXPENSE, 1500.0, "餐饮"),
            (TransactionType. EXPENSE, 500.0, "交通"),
            (TransactionType.INCOME, 2000.0, "兼职"),
            (TransactionType.EXPENSE, 800.0, "娱乐"),
        ]
        
        for trans_type, amount, note in monthly_data:
            trans = Transaction(
                amount=amount,
                trans_type=trans_type,
                category_id=1,
                date=datetime.now(),
                note=note
            )
            manager.add_transaction(trans)
        
        print(f"✓ 步骤1通过：添加了{len(monthly_data)}笔交易")
        
        # 步骤2：执行统计
        stats = Statistics()
        stats.calculate(manager.transactions)
        
        # 步骤3：验证统计结果
        expected_income = 10000.0
        expected_expense = 4800.0
        expected_balance = 5200.0
        
        assert stats.total_income == expected_income, f"收入统计错误"
        assert stats.total_expense == expected_expense, f"支出统计错误"
        assert stats.balance == expected_balance, f"余额计算错误"
        
        print(f"✓ 步骤2通过：统计结果正确")
        print(f"  收入：{stats.total_income}")
        print(f"  支出：{stats.total_expense}")
        print(f"  余额：{stats.balance}")
        
        db.close()
        print("\n✅ 集成测试3：统计计算 - 通过")