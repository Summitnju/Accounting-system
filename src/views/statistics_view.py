"""统计窗口 - 对应UML组件图中的统计界面"""
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from models.transaction import TransactionType


class StatisticsView:
    """统计界面类"""
    
    def __init__(self, parent, trans_mgr, cat_mgr, stats_mgr):
        """
        初始化统计窗口
        
        Args:
            parent: 父窗口
            trans_mgr: 交易管理器
            cat_mgr: 分类管理器
            stats_mgr: 统计管理器
        """
        self.trans_mgr = trans_mgr
        self.cat_mgr = cat_mgr
        self.stats_mgr = stats_mgr
        
        self.window = tk.Toplevel(parent)
        self.window.title("统计分析")
        self.window.geometry("700x550")
        self.window.transient(parent)
        
        self.setup_ui()
        self.show_monthly_stats()
    
    def setup_ui(self):
        """设置界面"""
        # 标题
        title = tk.Label(
            self.window,
            text="📊 统计分析",
            font=("Arial", 16, "bold"),
            bg="#70AD47",
            fg="white",
            pady=12
        )
        title.pack(fill=tk.X)
        
        # 时间选择
        time_frame = tk.Frame(self.window, pady=10)
        time_frame.pack(fill=tk.X, padx=15)
        
        tk.Label(time_frame, text="统计周期:", font=("Arial", 10)).pack(side=tk.LEFT)
        
        self.period_var = tk.StringVar(value="本月")
        for period in ["本月", "本年", "全部"]:
            tk.Radiobutton(
                time_frame,
                text=period,
                variable=self.period_var,
                value=period,
                command=self.update_stats
            ).pack(side=tk.LEFT, padx=10)
        
        # 统计摘要
        summary_frame = tk.Frame(
            self.window,
            bg="#E8F5E9",
            relief=tk.RAISED,
            bd=2
        )
        summary_frame.pack(fill=tk.X, padx=15, pady=10)
        
        self.summary_label = tk.Label(
            summary_frame,
            text="",
            font=("Arial", 11),
            bg="#E8F5E9",
            justify=tk.LEFT,
            pady=15,
            padx=20
        )
        self.summary_label.pack()
        
        # 分类统计
        tk.Label(
            self.window,
            text="📋 分类明细",
            font=("Arial", 11, "bold")
        ).pack(anchor=tk.W, padx=15, pady=(5, 3))
        
        # 创建文本框显示分类统计
        text_frame = tk.Frame(self.window)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.stats_text = tk.Text(
            text_frame,
            font=("Courier", 10),
            yscrollcommand=scrollbar.set,
            wrap=tk.WORD,
            height=15
        )
        self.stats_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.stats_text.yview)
        
        # 关闭按钮
        tk.Button(
            self.window,
            text="关闭",
            command=self.window.destroy,
            font=("Arial", 10),
            padx=30,
            pady=8
        ).pack(pady=10)
    
    def update_stats(self):
        """更新统计"""
        period = self.period_var.get()
        
        if period == "本月":
            self.show_monthly_stats()
        elif period == "本年":
            self.show_yearly_stats()
        else:
            self.show_all_stats()
    
    def show_monthly_stats(self):
        """显示月度统计"""
        now = datetime.now()
        stats = self.stats_mgr.calculate_monthly(now.year, now.month)
        
        title = f"📅 {now.year}年{now.month}月统计"
        self.display_stats(stats, title)
    
    def show_yearly_stats(self):
        """显示年度统计"""
        now = datetime.now()
        
        # 计算年度统计
        start_date = datetime(now.year, 1, 1)
        end_date = datetime(now.year, 12, 31, 23, 59, 59)
        transactions = self.trans_mgr.query(
            start_date=start_date,
            end_date=end_date
        )
        
        from models.statistics import Statistics
        stats = Statistics()
        stats.calculate(transactions)
        
        title = f"📅 {now.year}年统计"
        self.display_stats(stats, title)
    
    def show_all_stats(self):
        """显示全部统计"""
        transactions = self.trans_mgr.get_transactions()
        
        from models.statistics import Statistics
        stats = Statistics()
        stats.calculate(transactions)
        
        title = "📅 全部数据统计"
        self.display_stats(stats, title)
    
    def display_stats(self, stats, title):
        """
        显示统计数据
        
        Args:
            stats: Statistics对象
            title: 标题
        """
        # 更新摘要
        summary = f"{title}\n\n"
        summary += f"💰 总收入: ¥{stats.total_income:.2f}\n"
        summary += f"💸 总支出: ¥{stats.total_expense:.2f}\n"
        summary += f"💵 净余额: ¥{stats.get_balance():.2f}\n"
        summary += f"📊 交易笔数: {self.trans_mgr.get_transaction_count()}笔"
        
        self.summary_label.config(text=summary)
        
        # 更新分类统计
        self.stats_text.config(state=tk.NORMAL)
        self.stats_text.delete('1.0', tk.END)
        
        if stats.category_data:
            # 表头
            header = f"{'分类':10s}  {'金额':>12s}  {'占比':>8s}  {'笔数':>6s}\n"
            self.stats_text.insert(tk.END, header)
            self.stats_text.insert(tk.END, "-" * 50 + "\n")
            
            # 分类数据（按金额降序）
            sorted_cats = sorted(
                stats.category_data.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            for cat_id, amount in sorted_cats:
                cat = self.cat_mgr.get_category_by_id(cat_id)
                if cat:
                    # 计算占比
                    percentage = (amount / stats.total_expense * 100 
                                if stats.total_expense > 0 else 0)
                    
                    # 计算笔数
                    count = sum(1 for t in self.trans_mgr.get_transactions()
                              if t.category_id == cat_id)
                    
                    line = f"{cat.icon} {cat.name:8s}  ¥{amount:10.2f}  {percentage:6.1f}%  {count:4d}笔\n"
                    self.stats_text.insert(tk.END, line)
        else:
            self.stats_text.insert(tk.END, "暂无数据")
        
        self.stats_text.config(state=tk.DISABLED)