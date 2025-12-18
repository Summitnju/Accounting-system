# simple_fuzz_test.py
"""
简易模糊测试脚本（不依赖外部库）
使用随机数据测试系统的异常处理能力
"""
import sys
import os
import random
import string
import time
from datetime import datetime

sys.path.insert(0, 'src')

from database.database import Database
from managers.transaction_manager import TransactionManager
from models.transaction import Transaction, TransactionType


class SimpleFuzzer:
    """简易模糊测试器"""
    
    def __init__(self):
        self.iterations = 0
        self.crashes = []
        self.start_time = time.time()
    
    def generate_random_string(self, max_length=200):
        """生成随机字符串"""
        length = random.randint(0, max_length)
        # 包含各种字符：字母、数字、特殊符号、中文
        chars = string.ascii_letters + string.digits + string.punctuation + "  \n\t中文测试"
        return ''.join(random.choice(chars) for _ in range(length))
    
    def generate_random_amount(self):
        """生成随机金额"""
        choices = [
            random.uniform(-10000, 10000),  # 正常范围
            0,  # 边界：零
            -1,  # 边界：负数
            float('inf'),  # 极值：无穷大
            float('-inf'),  # 极值：负无穷
            2000000,  # 触发植入缺陷
        ]
        return random.choice(choices)
    
    def fuzz_database_query(self, db):
        """模糊测试数据库查询"""
        try:
            condition = self.generate_random_string(100)
            db.load('transactions', condition=condition)
        except Exception as e:
            # ✅ 记录严重的崩溃类型
            error_type = type(e).__name__
            if error_type in ['AttributeError', 'ZeroDivisionError', 'TypeError', 'OverflowError', 'sqlite3.OperationalError']: 
                self.crashes.append({
                    'iteration': self.iterations,
                    'error': str(e),
                    'type': error_type,
                    'location': 'database_query'
                })
                print(f"\n❌ 发现崩溃 (第 {self.iterations} 次迭代): {error_type}")
                print(f"   位置: database_query")
                print(f"   错误: {str(e)[:100]}")
    
    def fuzz_transaction_add(self, manager):
        """模糊测试添加交易"""
        amount = self.generate_random_amount()
        try:
            trans = Transaction(
                amount=amount,
                trans_type=random.choice([TransactionType.INCOME, TransactionType.EXPENSE]),
                category_id=random.randint(-10, 100),
                date=datetime.now(),
                note=self.generate_random_string(500)
            )
            manager.add_transaction(trans)
        except Exception as e:
            # ✅ 记录所有严重崩溃
            error_type = type(e).__name__
            # 记录这些严重错误类型
            if error_type in ['AttributeError', 'ZeroDivisionError', 'TypeError', 'OverflowError', 'ValueError', 'sqlite3.IntegrityError']:
                self. crashes.append({
                    'iteration': self.iterations,
                    'error': str(e),
                    'type': error_type,
                    'location':  'transaction_add',
                    'test_case': f'amount={amount}'
                })
                print(f"\n❌ 发现崩溃 (第 {self.iterations} 次迭代): {error_type}")
                print(f"   位置: transaction_add")
                print(f"   触发条件: amount={amount}")
                print(f"   错误:  {str(e)[:100]}")
    
    def fuzz_transaction_query(self, manager):
        """模糊测试查询功能"""
        min_amt = self.generate_random_amount()
        max_amt = self.generate_random_amount()
        keyword = self.generate_random_string(50)
        try:
            manager.query(
                keyword=keyword,
                min_amount=min_amt,
                max_amount=max_amt
            )
        except Exception as e:
            # ✅ 记录异常
            error_type = type(e).__name__
            if error_type in ['AttributeError', 'ZeroDivisionError', 'TypeError', 'ValueError']:
                self.crashes.append({
                    'iteration': self.iterations,
                    'error': str(e),
                    'type': error_type,
                    'location': 'transaction_query',
                    'test_case':  f'min={min_amt}, max={max_amt}'
                })
                print(f"\n❌ 发现崩溃 (第 {self.iterations} 次迭代): {error_type}")
                print(f"   位置: transaction_query")
                print(f"   错误:  {str(e)[:100]}")
    
    def run(self, duration_hours=5):
        """运行模糊测试"""
        print("="*70)
        print(f"  简易模糊测试启动")
        print(f"  目标模块: database.py, transaction_manager.py")
        print(f"  测试方法: 随机输入生成（字符串、数值、边界值）")
        print(f"  预计运行时间: {duration_hours} 小时")
        print(f"  开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70)
        print()
        
        end_time = time.time() + duration_hours * 3600
        last_report = time.time()
        
        while time. time() < end_time:
            try:
                # 初始化测试环境
                db = Database(':memory:')
                manager = TransactionManager(db)
                
                # 执行各种模糊测试
                self.fuzz_database_query(db)
                self.fuzz_transaction_add(manager)
                self.fuzz_transaction_query(manager)
                
                db.close()
                self.iterations += 1
                
                # 每10秒报告一次进度
                if time.time() - last_report > 10:
                    self.print_status()
                    last_report = time.time()
                
            except KeyboardInterrupt: 
                print("\n\n⚠️  用户中断测试（Ctrl+C）")
                break
            except Exception as e:
                # 捕获最外层的严重崩溃（不应该到这里）
                self.crashes.append({
                    'iteration': self.iterations,
                    'error': str(e),
                    'type': type(e).__name__,
                    'location': 'main_loop'
                })
                print(f"\n💥 严重崩溃 (第 {self.iterations} 次迭代): {type(e).__name__} - {str(e)[:100]}")
        
        self.print_final_report()
    
    def print_status(self):
        """打印当前状态"""
        elapsed = time. time() - self.start_time
        rate = self.iterations / elapsed if elapsed > 0 else 0
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        print(f"\r⏱️  [{hours:02d}:{minutes:02d}] "
              f"迭代:  {self.iterations:,}  "
              f"速率: {rate:.0f} exec/s  "
              f"崩溃: {len(self.crashes)}", end='', flush=True)
    
    def print_final_report(self):
        """打印最终报告"""
        elapsed = time. time() - self.start_time
        hours = elapsed / 3600
        minutes = elapsed / 60
        
        print("\n")
        print("="*70)
        print("  📊 模糊测试完成 - 最终报告")
        print("="*70)
        print(f"⏱️  运行时长: {hours:.2f} 小时 ({minutes:.1f} 分钟)")
        print(f"🔢 总迭代次数: {self.iterations:,}")
        print(f"⚡ 平均速率: {self.iterations/elapsed:.0f} exec/s")
        print(f"💥 发现崩溃:  {len(self.crashes)}")
        
        if self.crashes:
            print("\n崩溃详情:")
            # 按类型分组统计
            crash_types = {}
            for crash in self.crashes:
                crash_type = crash['type']
                if crash_type not in crash_types:
                    crash_types[crash_type] = []
                crash_types[crash_type].append(crash)
            
            for crash_type, crashes in crash_types.items():
                print(f"\n  {crash_type}:  {len(crashes)} 次")
                # 显示前3个示例
                for i, crash in enumerate(crashes[:3], 1):
                    print(f"    {i}. 第 {crash['iteration']} 次迭代")
                    print(f"       位置: {crash['location']}")
                    if 'test_case' in crash: 
                        print(f"       条件: {crash['test_case']}")
                    print(f"       错误: {crash['error'][:80]}")
                if len(crashes) > 3:
                    print(f"    ... 还有 {len(crashes) - 3} 次相同类型的崩溃")
        else:
            print("\n✅ 未发现导致程序崩溃的输入")
            print("   系统对异常输入的处理较为健壮")
        
        print("="*70)


if __name__ == '__main__': 
    fuzzer = SimpleFuzzer()
    
    # 可以通过命令行参数指定运行时长
    # 例如：python simple_fuzz_test.py 2  # 运行2小时
    # 或者：python simple_fuzz_test.py 0.05  # 运行3分钟
    import sys
    if len(sys.argv) > 1:
        hours = float(sys.argv[1])
    else:
        hours = 5  # 默认5小时
    
    fuzzer.run(duration_hours=hours)