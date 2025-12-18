"""查询窗口 - 对应UML组件图中的查询界面"""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from models.transaction import TransactionType


class QueryView:
    """查询界面类"""
    
    def __init__(self, parent, trans_mgr, cat_mgr, export_mgr):
        """
        初始化查询窗口
        
        Args:
            parent: 父窗口
            trans_mgr: 交易管理器
            cat_mgr: 分类管理器
            export_mgr: 导出管理器
        """
        self.trans_mgr = trans_mgr
        self.cat_mgr = cat_mgr
        self.export_mgr = export_mgr
        
        self.window = tk.Toplevel(parent)
        self.window.title("高级查询")
        self.window.geometry("750x600")
        self.window.transient(parent)
        
        self.query_results = []
        self.setup_ui()
    
    def setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self.window,
            text="🔍 高级查询",
            font=("Arial", 16, "bold"),
            bg="#FFA500",
            fg="white",
            pady=12
        )
        title.pack(fill=tk.X)
        
        # 查询条件区
        condition_frame = tk.LabelFrame(
            self.window,
            text="查询条件",
            font=("Arial", 10, "bold"),
            padx=15,
            pady=10
        )
        condition_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # 时间范围
        row = 0
        tk.Label(condition_frame, text="开始日期:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.start_date_entry = tk.Entry(condition_frame, width=12)
        self.start_date_entry.grid(row=row, column=1, padx=5, pady=5)
        self.start_date_entry.insert(0, "2024-01-01")
        
        tk.Label(condition_frame, text="结束日期:").grid(
            row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5
        )
        self.end_date_entry = tk.Entry(condition_frame, width=12)
        self.end_date_entry.grid(row=row, column=3, padx=5, pady=5)
        self.end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        
        # 金额范围
        row += 1
        tk.Label(condition_frame, text="最小金额:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.min_amount_entry = tk.Entry(condition_frame, width=12)
        self.min_amount_entry.grid(row=row, column=1, padx=5, pady=5)
        
        tk.Label(condition_frame, text="最大金额:").grid(
            row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5
        )
        self.max_amount_entry = tk.Entry(condition_frame, width=12)
        self.max_amount_entry.grid(row=row, column=3, padx=5, pady=5)
        
        # 交易类型
        row += 1
        tk.Label(condition_frame, text="交易类型:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.type_var = tk.StringVar(value="全部")
        type_combo = ttk.Combobox(
            condition_frame,
            textvariable=self.type_var,
            values=["全部", "收入", "支出"],
            state="readonly",
            width=10
        )
        type_combo.grid(row=row, column=1, padx=5, pady=5)
        
        # 分类
        tk.Label(condition_frame, text="分类:").grid(
            row=row, column=2, sticky=tk.W, padx=(10, 0), pady=5
        )
        categories = ["全部"] + [c.name for c in self.cat_mgr.get_categories()]
        self.category_var = tk.StringVar(value="全部")
        category_combo = ttk.Combobox(
            condition_frame,
            textvariable=self.category_var,
            values=categories,
            state="readonly",
            width=10
        )
        category_combo.grid(row=row, column=3, padx=5, pady=5)
        
        # 关键词
        row += 1
        tk.Label(condition_frame, text="关键词:").grid(
            row=row, column=0, sticky=tk.W, pady=5
        )
        self.keyword_entry = tk.Entry(condition_frame, width=30)
        self.keyword_entry.grid(row=row, column=1, columnspan=3, 
                               sticky=tk.EW, padx=5, pady=5)
        
        # 查询按钮
        row += 1
        button_frame = tk.Frame(condition_frame)
        button_frame.grid(row=row, column=0, columnspan=4, pady=10)
        
        tk.Button(
            button_frame,
            text="🔍 查询",
            command=self.do_query,
            bg="#5B9BD5",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="🔄 重置",
            command=self.reset_conditions,
            font=("Arial", 10),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="💾 导出结果",
            command=self.export_results,
            bg="#70AD47",
            fg="white",
            font=("Arial", 10, "bold"),
            padx=20,
            pady=5
        ).pack(side=tk.LEFT, padx=5)
        
        # 结果统计
        self.stats_label = tk.Label(
            self.window,
            text="查询结果: 0条记录",
            font=("Arial", 10),
            fg="gray"
        )
        self.stats_label.pack(anchor=tk.W, padx=15, pady=(5, 0))
        
        # 结果列表
        result_frame = tk.LabelFrame(
            self.window,
            text="查询结果",
            font=("Arial", 10, "bold"),
            padx=10,
            pady=10
        )
        result_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        scrollbar = tk.Scrollbar(result_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.result_listbox = tk.Listbox(
            result_frame,
            font=("Courier", 9),
            yscrollcommand=scrollbar.set
        )
        self.result_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.result_listbox.yview)
    
    def do_query(self):
        """执行查询"""
        self.result_listbox.delete(0, tk.END)
        
        try:
            # 解析条件
            start_date = None
            if self.start_date_entry.get():
                start_date = datetime.strptime(
                    self.start_date_entry.get(), '%Y-%m-%d'
                )
            
            end_date = None
            if self.end_date_entry.get():
                end_date = datetime.strptime(
                    self.end_date_entry.get(), '%Y-%m-%d'
                )
                end_date = end_date.replace(hour=23, minute=59, second=59)
            
            min_amount = None
            if self.min_amount_entry.get():
                min_amount = eval(self.min_amount_entry.get())
            
            max_amount = None
            if self.max_amount_entry.get():
                max_amount = float(self.max_amount_entry.get())
            
            keyword = self.keyword_entry.get()
            
            # 交易类型
            trans_type = None
            if self.type_var.get() == "收入":
                trans_type = TransactionType.INCOME
            elif self.type_var.get() == "支出":
                trans_type = TransactionType.EXPENSE
            
            # 分类
            category_id = None
            if self.category_var.get() != "全部":
                for cat in self.cat_mgr.get_categories():
                    if cat.name == self.category_var.get():
                        category_id = cat.id
                        break
            
            # 执行查询
            self.query_results = self.trans_mgr.query(
                start_date=start_date,
                end_date=end_date,
                category_id=category_id,
                min_amount=min_amount,
                max_amount=max_amount,
                keyword=keyword,
                trans_type=trans_type
            )
            
            # 显示结果
            if self.query_results:
                total_income = sum(
                    t.amount for t in self.query_results 
                    if t.type == TransactionType.INCOME
                )
                total_expense = sum(
                    t.amount for t in self.query_results 
                    if t.type == TransactionType.EXPENSE
                )
                
                self.stats_label.config(
                    text=f"查询结果: {len(self.query_results)}条记录  "
                         f"收入: ¥{total_income:.2f}  "
                         f"支出: ¥{total_expense:.2f}"
                )
                
                for trans in self.query_results:
                    cat = self.cat_mgr.get_category_by_id(trans.category_id)
                    cat_name = cat.name if cat else '未分类'
                    sign = '+' if trans.type == TransactionType.INCOME else '-'
                    
                    line = (f"{trans.date.strftime('%Y-%m-%d')}  "
                           f"{cat_name:8s}  {sign}¥{trans.amount:8.2f}  "
                           f"{trans.note}")
                    self.result_listbox.insert(tk.END, line)
            else:
                self.stats_label.config(text="查询结果: 0条记录")
                self.result_listbox.insert(tk.END, "未找到符合条件的记录")
        
        except Exception as e:
            messagebox.showerror("错误", f"查询失败: {str(e)}")
    
    def reset_conditions(self):
        """重置查询条件"""
        self.start_date_entry.delete(0, tk.END)
        self.start_date_entry.insert(0, "2024-01-01")
        self.end_date_entry.delete(0, tk.END)
        self.end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))
        self.min_amount_entry.delete(0, tk.END)
        self.max_amount_entry.delete(0, tk.END)
        self.keyword_entry.delete(0, tk.END)
        self.type_var.set("全部")
        self.category_var.set("全部")
        self.result_listbox.delete(0, tk.END)
        self.stats_label.config(text="查询结果: 0条记录")
    
    def export_results(self):
        """导出查询结果"""
        if not self.query_results:
            messagebox.showwarning("提示", "没有可导出的数据")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV文件", "*.csv"), ("所有文件", "*.*")]
        )
        
        if filename:
            if self.export_mgr.export_to_csv(filename, self.query_results):
                messagebox.showinfo("成功", f"已导出 {len(self.query_results)} 条记录")
            else:
                messagebox.showerror("错误", "导出失败")