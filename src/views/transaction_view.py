"""交易界面 - 对应UML类图中的TransactionView类"""
import tkinter as tk
from tkinter import ttk, messagebox
from models.transaction import Transaction, TransactionType

class TransactionView:
    """交易界面类"""
    
    def __init__(self, cat_mgr):
        """初始化"""
        self.cat_mgr = cat_mgr
    
    def show_add_dialog(self, parent, callback):
        """
        显示添加对话框 - 对应UML中的showAddDialog()方法
        
        Args:
            parent: 父窗口
            callback: 添加成功后的回调函数
        """
        dialog = tk.Toplevel(parent)
        dialog.title("添加交易记录")
        dialog.geometry("400x300")
        dialog.transient(parent)
        dialog.grab_set()
        
        # 类型
        tk.Label(dialog, text="类型:", font=("Arial", 10)).grid(
            row=0, column=0, sticky=tk.W, padx=20, pady=10
        )
        
        type_var = tk.StringVar(value="支出")
        type_frame = tk.Frame(dialog)
        type_frame.grid(row=0, column=1, sticky=tk.W, pady=10)
        
        def update_categories():
            trans_type = (TransactionType.INCOME if type_var.get() == "收入" 
                         else TransactionType.EXPENSE)
            categories = self.cat_mgr.get_categories(trans_type)
            category_combo['values'] = [f"{c.icon} {c.name}" for c in categories]
            if categories:
                category_combo.current(0)
        
        tk.Radiobutton(
            type_frame, text="支出", variable=type_var, value="支出",
            command=update_categories
        ).pack(side=tk.LEFT)
        tk.Radiobutton(
            type_frame, text="收入", variable=type_var, value="收入",
            command=update_categories
        ).pack(side=tk.LEFT)
        
        # 金额
        tk.Label(dialog, text="金额:", font=("Arial", 10)).grid(
            row=1, column=0, sticky=tk.W, padx=20, pady=10
        )
        amount_entry = tk.Entry(dialog, font=("Arial", 10))
        amount_entry.grid(row=1, column=1, sticky=tk.EW, padx=20, pady=10)
        
        # 分类
        tk.Label(dialog, text="分类:", font=("Arial", 10)).grid(
            row=2, column=0, sticky=tk.W, padx=20, pady=10
        )
        category_combo = ttk.Combobox(dialog, font=("Arial", 10), state="readonly")
        category_combo.grid(row=2, column=1, sticky=tk.EW, padx=20, pady=10)
        
        # 备注
        tk.Label(dialog, text="备注:", font=("Arial", 10)).grid(
            row=3, column=0, sticky=tk.W, padx=20, pady=10
        )
        note_entry = tk.Entry(dialog, font=("Arial", 10))
        note_entry.grid(row=3, column=1, sticky=tk.EW, padx=20, pady=10)
        
        # 保存函数
        def save():
            try:
                amount = float(amount_entry.get())
                if amount <= 0:
                    raise ValueError("金额必须大于0")
            except ValueError as e:
                messagebox.showerror("错误", str(e))
                return
            
            trans_type = (TransactionType.INCOME if type_var.get() == "收入" 
                         else TransactionType.EXPENSE)
            
            cat_index = category_combo.current()
            categories = self.cat_mgr.get_categories(trans_type)
            category_id = categories[cat_index].id if cat_index >= 0 else None
            
            note = note_entry.get()
            
            transaction = Transaction(
                amount=amount,
                trans_type=trans_type,
                category_id=category_id,
                note=note
            )
            
            callback(transaction)
            dialog.destroy()
        
        # 按钮
        button_frame = tk.Frame(dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=15)
        
        tk.Button(
            button_frame, text="取消", command=dialog.destroy,
            padx=20, pady=5
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Button(
            button_frame, text="确定", command=save,
            bg="#5B9BD5", fg="white", padx=20, pady=5
        ).pack(side=tk.LEFT, padx=10)
        
        # 初始化分类
        update_categories()
    
    def refresh_list(self):
        """刷新列表 - 对应UML中的refreshList()方法"""
        pass