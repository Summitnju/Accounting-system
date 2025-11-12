"""分类管理器 - 对应UML类图中的CategoryManager类"""
from models.category import Category
from models.transaction import TransactionType

class CategoryManager:
    """分类管理器 - 对应UML组件图中的分类管理组件"""
    
    def __init__(self, database):
        """初始化管理器"""
        self.database = database
        self.categories = []
        self.load_categories()
    
    def load_categories(self):
        """从数据库加载分类"""
        data = self.database.load('categories')
        self.categories = []
        for item in data:
            trans_type = (TransactionType.INCOME if item['type'] == '收入' 
                         else TransactionType.EXPENSE)
            cat = Category(
                category_id=item['id'],
                name=item['name'],
                icon=item.get('icon', ''),
                trans_type=trans_type,
                is_predefined=bool(item.get('is_predefined', 0))
            )
            self.categories.append(cat)
    
    def add_category(self, category):
        """
        添加分类 - 对应UML中的addCategory()方法
        
        Args:
            category: Category对象
        """
        cat_data = {
            'name': category.name,
            'icon': category.icon,
            'type': category.type.value if category.type else None,
            'is_predefined': category.is_predefined
        }
        cat_id = self.database.save('categories', cat_data)
        category.id = cat_id
        self.categories.append(category)
    
    def get_categories(self, trans_type=None):
        """
        获取分类 - 对应UML中的getCategories()方法
        
        Args:
            trans_type: 交易类型（可选）
        
        Returns:
            分类列表
        """
        if trans_type:
            return [c for c in self.categories if c.type == trans_type]
        return self.categories
    
    def get_category_by_id(self, cat_id):
        """根据ID获取分类"""
        for cat in self.categories:
            if cat.id == cat_id:
                return cat
        return None