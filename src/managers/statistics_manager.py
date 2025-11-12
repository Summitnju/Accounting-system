"""统计管理器 - 对应UML类图中的StatisticsManager类"""
from models.statistics import Statistics
from datetime import datetime


class StatisticsManager:
    """统计管理器 - 对应UML组件图中的统计管理组件"""
    
    def __init__(self, transaction_manager):
        """
        初始化管理器
        
        Args:
            transaction_manager: TransactionManager实例
        """
        self.transaction_manager = transaction_manager
    
    def calculate_monthly(self, year, month):
        """
        计算月度统计 - 对应UML中的calculateMonthly()方法
        
        Args:
            year: 年份
            month: 月份
        
        Returns:
            Statistics对象
        """
        from datetime import timedelta
        
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # 通过TransactionManager查询数据
        transactions = self.transaction_manager.query(
            start_date=start_date,
            end_date=end_date
        )
        
        # 创建Statistics对象并计算
        stats = Statistics()
        stats.calculate(transactions)
        
        return stats
    
    def generate_chart(self):
        """
        生成图表 - 对应UML中的generateChart()方法
        
        Returns:
            图表数据
        """
        # 简化实现，返回图表数据字典
        return {"type": "chart", "data": []}