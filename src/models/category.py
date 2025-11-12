"""分类模型"""


class Category:
    """分类类 - 对应UML类图中的Category类"""
    
    def __init__(self, category_id=None, name="", icon="", 
                 trans_type=None, is_predefined=False):
        """
        初始化分类
        
        Args:
            category_id: 分类ID
            name: 分类名称
            icon: 图标
            trans_type: 所属交易类型
            is_predefined: 是否预定义
        """
        self.id = category_id
        self.name = name
        self.icon = icon
        self.type = trans_type
        self.is_predefined = is_predefined
    
    def get_name(self):
        """获取名称 - 对应UML中的getName()方法"""
        return self.name
    
    def get_icon(self):
        """获取图标 - 对应UML中的getIcon()方法"""
        return self.icon