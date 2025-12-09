#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import time
import pandas as pd
import numpy as np
import sys
import random

# 尝试导入 tqdm 用于进度条，如果没有则使用简单打印
try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

# ANSI 颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def colorize(text, color):
        return f"{color}{text}{Colors.ENDC}"

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_banner():
    print(Colors.colorize("="*60, Colors.BLUE))
    print(Colors.colorize("   OnlineLp 实时竞价模拟器 (Real-time Bidding Simulator)", Colors.BOLD + Colors.CYAN))
    print(Colors.colorize("="*60, Colors.BLUE))

class OnlineLpSimulator:
    def __init__(self, data_path, model_path, advertiser_number=None, delay=0.5):
        self.data_path = data_path
        self.model_path = model_path
        self.delay = delay
        self.advertiser_number = advertiser_number
        
        # 加载模型
        print(f"正在加载模型: {model_path} ...")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件未找到: {model_path}\n请先运行 main/main_onlineLp.py 进行训练。")
        self.model = pd.read_csv(model_path)
        
        # 加载数据
        print(f"正在加载数据: {data_path} ...")
        if not os.path.exists(data_path):
             # 尝试查找转换后的数据
            rl_data_path = data_path.replace(".csv", "-rlData.csv").replace("traffic/", "traffic/training_data_rlData_folder/")
            if os.path.exists(rl_data_path):
                 print(f"未找到原始数据，尝试使用转换后的数据: {rl_data_path}")
                 self.data_path = rl_data_path
            else:
                 raise FileNotFoundError(f"数据文件未找到: {data_path}")
        
        # 读取数据（只读取一部分以加快速度，或者读取特定广告主）
        # 这里我们读取整个文件，然后筛选
        self.raw_data = pd.read_csv(self.data_path)
        
        # 如果未指定广告主，随机选择一个有足够数据的广告主
        if self.advertiser_number is None:
            valid_advertisers = self.raw_data['advertiserNumber'].unique()
            # 简单筛选一下数据量较多的广告主
            self.advertiser_number = valid_advertisers[0] # 默认第一个，或者随机
            print(f"自动选择广告主: {self.advertiser_number}")

        # 筛选特定广告主的数据
        self.data = self.raw_data[self.raw_data['advertiserNumber'] == self.advertiser_number].copy()
        
        if self.data.empty:
            raise ValueError(f"广告主 {self.advertiser_number} 没有数据！")
            
        # 获取基本信息
        self.category = self.data['advertiserCategoryIndex'].iloc[0]
        self.budget = self.data['budget'].iloc[0]
        self.cpa_constraint = self.data['CPAConstraint'].iloc[0]
        self.remaining_budget = self.budget
        self.total_steps = 48
        
        print(f"模拟配置: 广告主={self.advertiser_number}, 行业={self.category}, 预算={self.budget}, CPA约束={self.cpa_constraint}")
        time.sleep(1)

    def get_alpha(self, time_step, remaining_budget):
        """根据 OnlineLp 策略获取 alpha (CPA阈值)"""
        # 筛选当前时间步和类别的模型数据
        tem = self.model[
            (self.model["timeStepIndex"] == time_step) & 
            (self.model["advertiserCategoryIndex"] == self.category)
        ]
        
        alpha = self.cpa_constraint
        
        if len(tem) > 0:
            # 查找累积成本大于剩余预算的第一行
            filtered_df = tem[tem['cum_cost'] > remaining_budget]
            if not filtered_df.empty:
                alpha = filtered_df.iloc[0]['realCPA']
        
        # 限制 alpha 不超过 CPA 约束的 1.5 倍
        alpha = min(self.cpa_constraint * 1.5, alpha)
        return alpha

    def simulate(self):
        clear_screen()
        print_banner()
        
        total_cost = 0
        total_conversion = 0
        total_wins = 0
        total_impression = 0
        
        history = []
        
        # 按时间步遍历
        for time_step in range(self.total_steps):
            # 获取当前时间步的数据
            step_data = self.data[self.data['timeStepIndex'] == time_step]
            
            if step_data.empty:
                continue
                
            # 1. 策略计算：获取 CPA 阈值 (alpha)
            alpha = self.get_alpha(time_step, self.remaining_budget)
            
            # 2. 计算出价
            # bids = alpha * pValue
            p_values = step_data['pValue'].values
            bids = alpha * p_values
            
            # 3. 模拟竞价结果
            # 真实数据中有 leastWinningCost (最低获胜成本)
            least_winning_costs = step_data['leastWinningCost'].values
            
            # 判断是否获胜: 出价 >= 最低获胜成本
            is_win = bids >= least_winning_costs
            
            # 计算成本: 如果是广义第二价格拍卖(GSP)，成本通常是 leastWinningCost
            # 但为了简化，这里假设支付 leastWinningCost
            costs = least_winning_costs * is_win
            
            # 模拟转化 (使用真实数据中的概率进行伯努利采样，或者直接用真实数据的转化如果存在)
            # 这里我们基于 pValue 模拟转化，因为真实转化是基于真实历史出价的
            # 为了更接近真实评估，我们使用 pValue 模拟
            conversions = np.zeros_like(costs)
            # 只有获胜且曝光的才可能转化。这里简化假设获胜即曝光
            # 生成随机数模拟转化
            random_vals = np.random.rand(len(p_values))
            conversions = (random_vals < p_values) & is_win
            
            # 统计本时间步结果
            step_cost = np.sum(costs)
            step_conversion = np.sum(conversions)
            step_wins = np.sum(is_win)
            step_traffic = len(step_data)
            
            # 处理预算超支
            if step_cost > self.remaining_budget:
                ratio = self.remaining_budget / step_cost
                step_cost = self.remaining_budget # 只能花这么多
                step_wins = int(step_wins * ratio)
                step_conversion = int(step_conversion * ratio)
                # 实际逻辑可能更复杂，这里简化处理
            
            # 更新状态
            self.remaining_budget -= step_cost
            if self.remaining_budget < 0: self.remaining_budget = 0
            
            total_cost += step_cost
            total_conversion += step_conversion
            total_wins += step_wins
            total_impression += step_wins # 简化假设
            
            # 计算实时指标
            current_cpa = total_cost / (total_conversion + 1e-10)
            budget_percent = (self.budget - self.remaining_budget) / self.budget * 100
            
            # --- 动态展示 ---
            clear_screen()
            print_banner()
            
            print(f"时间步: {Colors.colorize(f'{time_step+1}/{self.total_steps}', Colors.BOLD)}")
            print("-" * 60)
            
            # 关键指标面板
            print(f"预算消耗: [{self.progress_bar(budget_percent)}] {budget_percent:.1f}%")
            print(f"剩余预算: {Colors.colorize(f'{self.remaining_budget:.2f}', Colors.GREEN)} / {self.budget:.2f}")
            print(f"当前 Alpha (CPA阈值): {Colors.colorize(f'{alpha:.4f}', Colors.WARNING)}")
            print("-" * 60)
            
            print(f"{'指标':<15} | {'本步数据':<15} | {'累计数据':<15}")
            print("-" * 60)
            print(f"{'流量数':<15} | {step_traffic:<15} | {np.sum([h['traffic'] for h in history]) + step_traffic:<15}")
            print(f"{'出价数':<15} | {step_traffic:<15} | -")
            print(f"{'获胜数':<15} | {Colors.colorize(step_wins, Colors.GREEN):<24} | {total_wins:<15}")
            print(f"{'消耗':<15} | {step_cost:<15.2f} | {total_cost:<15.2f}")
            print(f"{'转化':<15} | {Colors.colorize(step_conversion, Colors.BOLD):<24} | {total_conversion:<15}")
            print(f"{'实际 CPA':<15} | {(step_cost/(step_conversion+1e-10)):<15.2f} | {Colors.colorize(f'{current_cpa:.2f}', Colors.CYAN):<24}")
            print("-" * 60)
            
            # 记录历史
            history.append({
                'time_step': time_step,
                'alpha': alpha,
                'cost': step_cost,
                'conversion': step_conversion,
                'wins': step_wins,
                'traffic': step_traffic
            })
            
            # 延时以便观察
            time.sleep(self.delay)
            
        # 最终结果
        self.show_summary(total_cost, total_conversion, total_wins, history)

    def progress_bar(self, percent, length=30):
        filled_length = int(length * percent // 100)
        bar = '█' * filled_length + '-' * (length - filled_length)
        return bar

    def show_summary(self, total_cost, total_conversion, total_wins, history):
        clear_screen()
        print_banner()
        print(Colors.colorize("\n🏆 模拟结束！最终结果报告", Colors.BOLD + Colors.GREEN))
        print("=" * 60)
        
        real_cpa = total_cost / (total_conversion + 1e-10)
        score = self.calculate_score(total_conversion, real_cpa, self.cpa_constraint)
        
        print(f"总消耗预算: {total_cost:.2f} / {self.budget:.2f} ({(total_cost/self.budget*100):.1f}%)")
        print(f"总获得转化: {int(total_conversion)}")
        print(f"总获胜次数: {int(total_wins)}")
        print(f"最终 CPA  : {Colors.colorize(f'{real_cpa:.2f}', Colors.CYAN)} (约束: {self.cpa_constraint})")
        print(f"综合得分  : {Colors.colorize(f'{score:.2f}', Colors.BOLD + Colors.WARNING)}")
        print("=" * 60)
        print("\n(按任意键退出)")
        # input()

    def calculate_score(self, reward, cpa, cpa_constraint):
        """计算 NeurIPS 比赛得分"""
        beta = 2
        penalty = 1
        if cpa > cpa_constraint:
            coef = cpa_constraint / (cpa + 1e-10)
            penalty = pow(coef, beta)
        return penalty * reward

def main():
    # 默认路径配置
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATA_PATH = os.path.join(BASE_DIR, "data/traffic/period-7.csv")
    MODEL_PATH = os.path.join(BASE_DIR, "saved_model/onlineLpTest/period.csv")
    
    # 检查路径
    if not os.path.exists(DATA_PATH):
        # 尝试查找 data 目录下的其他 csv
        traffic_dir = os.path.join(BASE_DIR, "data/traffic")
        if os.path.exists(traffic_dir):
            files = [f for f in os.listdir(traffic_dir) if f.endswith(".csv")]
            if files:
                DATA_PATH = os.path.join(traffic_dir, files[0])
    
    try:
        simulator = OnlineLpSimulator(DATA_PATH, MODEL_PATH, delay=0.2) # delay=0.2秒，速度适中
        simulator.simulate()
    except Exception as e:
        print(Colors.colorize(f"\n❌ 错误: {e}", Colors.FAIL))
        sys.exit(1)

if __name__ == "__main__":
    main()
