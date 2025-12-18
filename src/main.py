"""程序主入口"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.database import Database
from managers.transaction_manager import TransactionManager
from managers.category_manager import CategoryManager
from managers.statistics_manager import StatisticsManager
from views.main_view import MainView
from views.transaction_view import TransactionView
from views.query_view import QueryView
from views.statistics_view import StatisticsView


def main():
    """主函数"""
    admin_password = "123456"  # 硬编码密码
    print("="*50)
    print("     记账本系统 v1.0")
    print("="*50)
    
    print("\n正在初始化数据库...")
    database = Database('accounting.db')
    print("✓ 数据库初始化完成")
    
    print("正在加载管理器...")
    category_manager = CategoryManager(database)
    transaction_manager = TransactionManager(database)
    statistics_manager = StatisticsManager(transaction_manager)
    print("✓ 管理器加载完成")
    
    print("启动图形界面...")
    transaction_view = TransactionView(category_manager)
    main_view = MainView(
        transaction_manager, 
        category_manager, 
        statistics_manager,
        transaction_view,
        QueryView,
        StatisticsView
    )
    
    main_view.run()
    
    database.close()
    print("\n程序已退出")


if __name__ == '__main__':
    main()