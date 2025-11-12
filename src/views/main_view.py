"""主界面 - 增强版"""
import tkinter as tk
from tkinter import messagebox
from datetime import datetime


class MainView:
    """主界面类"""
    
    def __init__(self, trans_mgr, cat_mgr, stats_mgr, trans_view, 
                 query_view_class, stats_view_class):
        """初始化主界面"""
        self.trans_mgr = trans_mgr
        self.cat_mgr = cat_mgr
        self.stats_mgr = stats_mgr
        self.trans_view = trans_view
        self.query_view_class = query_view_class
        self.stats_view_class = stats_view_class
        
        self.root = tk.Tk()
        self.root.title("记账本系统 - by 陈姝含")
        self.root.geometry("850x650")
        
        self.setup_ui()
        self.display_balance()
        self.display_transactions()
    
    def setup_ui(self):
        """设置界面"""
        # 标题栏
        title_frame = tk.Frame(self.root, bg="#5B9BD5", height=50)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        tk.Label(
            title_frame, 
            text="💰 记账本系统", 
            font=("Arial", 18, "bold"),
            bg="#5B9BD5",
            fg="white"
        ).pack(side=tk.LEFT, padx=20)
        
        tk.Label(
            title_frame,
            text=f"当前: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            font=("Arial", 9),
            bg="#5B9BD5",
            fg="white"
        ).pack(side=tk.RIGHT, padx=20)
        
        # 余额卡片
        balance_frame = tk.Frame(self.root, bg="#7BB3E0", height=90)
        balance_frame.pack(fill=tk.X, padx=15, pady=12)
        balance_frame.pack_propagate(False)
        
        tk.Label(
            balance_frame, 
            text="总余额", 
            font=("Arial", 11),
            bg="#7BB3E0",
            fg="white"
        ).pack(pady=(8, 0))
        
        self.balance_label = tk.Label(
            balance_frame, 
            text="¥ 0.00", 
            font=("Arial", 24, "bold"),
            bg="#7BB3E0",
            fg="white"
        )
        self.balance_label.pack()
        
        # 收支统计
        stats_frame = tk.Frame(self.root)
        stats_frame.pack(fill=tk.X, padx=15, pady=8)
        
        income_frame = tk.Frame(
            stats_frame, 
            bg="white", 
            relief=tk.RAISED, 
            bd=1,
            highlightbackground="#70AD47",
            highlightthickness=2
        )
        income_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        tk.Label(
            income_frame, 
            text="📈 本月收入", 
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(pady=(8, 3))
        
        self.income_label = tk.Label(
            income_frame, 
            text="¥ 0.00", 
            font=("Arial", 14, "bold"),
            fg="#70AD47",
            bg="white"
        )
        self.income_label.pack(pady=(0, 8))
        
        expense_frame = tk.Frame(
            stats_frame, 
            bg="white", 
            relief=tk.RAISED, 
            bd=1,
            highlightbackground="#ED7D31",
            highlightthickness=2
        )
        expense_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        tk.Label(
            expense_frame, 
            text="📉 本月支出", 
            font=("Arial", 10, "bold"),
            bg="white"
        ).pack(pady=(8, 3))
        
        self.expense_label = tk.Label(
            expense_frame, 
            text="¥ 0.00", 
            font=("Arial", 14, "bold"),
            fg="#ED7D31",
            bg="white"
        )
        self.expense_label.pack(pady=(0, 8))
        
        # 最近交易标题
        header_frame = tk.Frame(self.root)
        header_frame.pack(fill=tk.X, padx=15, pady=(8, 3))
        
        tk.Label(
            header_frame, 
            text="📋 最近交易", 
            font=("Arial", 11, "bold")
        ).pack(side=tk.LEFT)
        
        tk.Button(
            header_frame,
            text="🗑️ 删除选中",
            font=("Arial", 9),
            command=self.delete_selected,
            fg="red",
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.RIGHT)
        
        tk.Button(
            header_frame,
            text="🔄 刷新",
            font=("Arial", 9),
            command=self.refresh_all,
            relief=tk.FLAT,
            cursor="hand2"
        ).pack(side=tk.RIGHT, padx=5)
        
        # 交易列表
        list_frame = tk.Frame(self.root)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.trans_listbox = tk.Listbox(
            list_frame,
            font=("Courier", 9),
            yscrollcommand=scrollbar.set,
            selectmode=tk.SINGLE
        )
        self.trans_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.trans_listbox.yview)
        
        # 按钮区
        button_frame = tk.Frame(self.root, bg="#f0f0f0", height=70)
        button_frame.pack(fill=tk.X, padx=15, pady=(8, 15))
        button_frame.pack_propagate(False)
        
        buttons = [
            ("➕ 添加", "#5B9BD5", self.show_add_dialog),
            ("📊 统计", "#70AD47", self.show_statistics_window),
            ("🔍 查询", "#FFA500", self.show_query_window),
        ]
        
        for text, color, command in buttons:
            btn = tk.Button(
                button_frame,
                text=text,
                font=("Arial", 10, "bold"),
                bg=color,
                fg="white",
                command=command,
                padx=12,
                pady=10,
                relief=tk.RAISED,
                cursor="hand2"
            )
            btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=3, pady=8)
    
    def display_balance(self):
        """显示余额"""
        now = datetime.now()
        stats = self.stats_mgr.calculate_monthly(now.year, now.month)
        
        self.balance_label.config(text=f"¥ {stats.get_balance():.2f}")
        self.income_label.config(text=f"¥ {stats.total_income:.2f}")
        self.expense_label.config(text=f"¥ {stats.total_expense:.2f}")
    
    def display_transactions(self):
        """显示交易记录"""
        self.trans_listbox.delete(0, tk.END)
        
        transactions = self.trans_mgr.get_latest_transactions(15)
        
        for trans in transactions:
            cat = self.cat_mgr.get_category_by_id(trans.category_id)
            cat_name = f"{cat.icon} {cat.name}" if cat else '未分类'
            sign = '+' if trans.type.value == '收入' else '-'
            
            line = f"[{trans.id:3d}] {trans.date.strftime('%m-%d %H:%M')} {cat_name:12s} {sign}¥{trans.amount:7.2f} {trans.note[:20]}"
            self.trans_listbox.insert(tk.END, line)
    
    def show_add_dialog(self):
        """显示添加对话框"""
        self.trans_view.show_add_dialog(self.root, self.on_transaction_added)
    
    def on_transaction_added(self, transaction):
        """交易添加后的回调"""
        self.trans_mgr.add_transaction(transaction)
        self.refresh_all()
        messagebox.showinfo("成功", "交易记录已添加！")
    
    def show_statistics_window(self):
        """显示统计窗口"""
        self.stats_view_class(
            self.root, 
            self.trans_mgr, 
            self.cat_mgr, 
            self.stats_mgr
        )
    
    def show_query_window(self):
        """显示查询窗口"""
        from managers.export_manager import ExportManager
        export_mgr = ExportManager(self.trans_mgr, self.cat_mgr)
        self.query_view_class(
            self.root, 
            self.trans_mgr, 
            self.cat_mgr,
            export_mgr
        )
    
    def delete_selected(self):
        """删除选中的交易"""
        selection = self.trans_listbox.curselection()
        if not selection:
            messagebox.showwarning("提示", "请先选择要删除的记录")
            return
        
        # 从列表项中提取ID
        line = self.trans_listbox.get(selection[0])
        try:
            trans_id = int(line.split(']')[0].strip('['))
            
            if messagebox.askyesno("确认", "确定要删除这条记录吗？"):
                self.trans_mgr.delete_transaction(trans_id)
                self.refresh_all()
                messagebox.showinfo("成功", "记录已删除")
        except:
            messagebox.showerror("错误", "无法删除该记录")
    
    def refresh_all(self):
        """刷新所有显示"""
        self.display_balance()
        self.display_transactions()
    
    def run(self):
        """运行主循环"""
        self.root.mainloop()