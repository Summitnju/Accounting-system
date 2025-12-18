"""导出管理器 - 对应UML组件图中的导出管理组件"""
import csv
import os
from datetime import datetime


class ExportManager:
    """导出管理器"""
    
    def __init__(self, transaction_manager, category_manager):
        """
        初始化导出管理器
        
        Args:
            transaction_manager: 交易管理器实例
            category_manager: 分类管理器实例
        """
        self.transaction_manager = transaction_manager
        self.category_manager = category_manager
    
    def export_to_csv(self, filename, transactions=None):
        """
        导出为CSV格式
        
        Args:
            filename: 文件名
            transactions: 交易记录列表（可选，默认导出全部）
        
        Returns:
            是否成功
        """
        if transactions is None:
            transactions = self.transaction_manager.get_transactions()
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8-sig') as csvfile:
                fieldnames = ['日期', '类型', '分类', '金额', '备注']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for trans in transactions:
                    cat = self.category_manager.get_category_by_id(trans.category_id)
                    cat_name = cat.name if cat else '未分类'
                    
                    writer.writerow({
                        '日期': trans.date.strftime('%Y-%m-%d %H:%M:%S'),
                        '类型': trans.type.value,
                        '分类': cat_name,
                        '金额': trans.amount,
                        '备注': trans.note
                    })
                
            return True
        except Exception as e:
            print(f"导出失败: {str(e)}")
            return False
    
    def backup_data(self, backup_folder):
        """
        备份数据
        
        Args:
            backup_folder: 备份文件夹路径
        
        Returns:
            备份文件路径
        """
        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(backup_folder, f'backup_{timestamp}.csv')
        
        if self.export_to_csv(filename):
            return filename
        return None