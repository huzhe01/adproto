import os
import sys
import pandas as pd
import numpy as np
import json

# 配置路径
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
STRATEGY_ENV_DIR = os.path.join(PROJECT_ROOT, "strategy_train_env")

# 默认数据路径
DEFAULT_DATA_PATH = os.path.join(STRATEGY_ENV_DIR, "data/traffic/period-7.csv")
DEFAULT_MODEL_PATH = os.path.join(STRATEGY_ENV_DIR, "saved_model/onlineLpTest/period.csv")

class OnlineLpSimulatorGenerator:
    def __init__(self, data_path, model_path, advertiser_number=None):
        self.data_path = data_path
        self.model_path = model_path
        self.advertiser_number = advertiser_number
        
        print(f"Loading Model: {model_path}")
        if not os.path.exists(model_path):
             raise FileNotFoundError(f"Model not found: {model_path}")
        self.model = pd.read_csv(model_path)
        
        print(f"Loading Data: {data_path}")
        if not os.path.exists(data_path):
             # Try fallback
             rl_data_path = data_path.replace(".csv", "-rlData.csv").replace("traffic/", "traffic/training_data_rlData_folder/")
             if os.path.exists(rl_data_path):
                 print(f"Using alternate data: {rl_data_path}")
                 self.data_path = rl_data_path
             else:
                 raise FileNotFoundError(f"Data not found: {data_path}")
        
        self.raw_data = pd.read_csv(self.data_path)
        
        if self.advertiser_number is None:
            valid_advertisers = self.raw_data['advertiserNumber'].unique()
            self.advertiser_number = valid_advertisers[0]
            print(f"Auto-selected Advertiser: {self.advertiser_number}")

        self.data = self.raw_data[self.raw_data['advertiserNumber'] == self.advertiser_number].copy()
        
        if self.data.empty:
            raise ValueError(f"No data for advertiser {self.advertiser_number}")
            
        self.category = self.data['advertiserCategoryIndex'].iloc[0]
        self.budget = float(self.data['budget'].iloc[0])
        self.cpa_constraint = float(self.data['CPAConstraint'].iloc[0])
        self.remaining_budget = self.budget
        self.total_steps = 48

    def get_alpha(self, time_step, remaining_budget):
        tem = self.model[
            (self.model["timeStepIndex"] == time_step) & 
            (self.model["advertiserCategoryIndex"] == self.category)
        ]
        
        alpha = self.cpa_constraint
        
        if len(tem) > 0:
            filtered_df = tem[tem['cum_cost'] > remaining_budget]
            if not filtered_df.empty:
                alpha = filtered_df.iloc[0]['realCPA']
        
        alpha = min(self.cpa_constraint * 1.5, alpha)
        return float(alpha)

    def generate(self):
        total_cost = 0
        total_conversion = 0
        total_wins = 0
        
        # This list will hold the snapshot of every step for the frontend
        simulation_steps = []
        
        # Initial state (Step 0 / Time 0)
        simulation_steps.append({
            "step": 0,
            "alpha": 0, # No alpha before start
            "step_cost": 0,
            "step_conversion": 0,
            "step_wins": 0,
            "step_traffic": 0,
            "total_cost": 0,
            "total_conversion": 0,
            "total_wins": 0,
            "remaining_budget": self.budget,
            "budget_percentage": 0,
            "real_cpa": 0
        })

        for time_step in range(self.total_steps):
            step_data = self.data[self.data['timeStepIndex'] == time_step]
            
            if step_data.empty:
                # Still record empty steps to maintain time continuity
                last_step = simulation_steps[-1]
                simulation_steps.append({
                    "step": time_step + 1,
                    "alpha": last_step["alpha"],
                    "step_cost": 0,
                    "step_conversion": 0,
                    "step_wins": 0,
                    "step_traffic": 0,
                    "total_cost": total_cost,
                    "total_conversion": total_conversion,
                    "total_wins": total_wins,
                    "remaining_budget": self.remaining_budget,
                    "budget_percentage": (self.budget - self.remaining_budget) / self.budget * 100,
                    "real_cpa": total_cost / (total_conversion + 1e-10)
                })
                continue
                
            alpha = self.get_alpha(time_step, self.remaining_budget)
            
            p_values = step_data['pValue'].values
            bids = alpha * p_values
            
            least_winning_costs = step_data['leastWinningCost'].values
            is_win = bids >= least_winning_costs
            costs = least_winning_costs * is_win
            
            # Simulation conversions
            random_vals = np.random.rand(len(p_values))
            conversions = (random_vals < p_values) & is_win
            
            step_cost = np.sum(costs)
            step_conversion = np.sum(conversions)
            step_wins = np.sum(is_win)
            step_traffic = len(step_data)
            
            if step_cost > self.remaining_budget:
                ratio = self.remaining_budget / step_cost if step_cost > 0 else 0
                step_cost = self.remaining_budget
                step_wins = int(step_wins * ratio)
                step_conversion = int(step_conversion * ratio)
            
            self.remaining_budget -= step_cost
            if self.remaining_budget < 0: self.remaining_budget = 0
            
            total_cost += step_cost
            total_conversion += step_conversion
            total_wins += step_wins
            
            real_cpa = total_cost / (total_conversion + 1e-10)
            budget_percent = (self.budget - self.remaining_budget) / self.budget * 100
            
            simulation_steps.append({
                "step": time_step + 1,
                "alpha": round(alpha, 4),
                "step_cost": round(float(step_cost), 2),
                "step_conversion": int(step_conversion),
                "step_wins": int(step_wins),
                "step_traffic": int(step_traffic),
                "total_cost": round(float(total_cost), 2),
                "total_conversion": int(total_conversion),
                "total_wins": int(total_wins),
                "remaining_budget": round(float(self.remaining_budget), 2),
                "budget_percentage": round(float(budget_percent), 2),
                "real_cpa": round(float(real_cpa), 2)
            })

        # Final config metadata
        metadata = {
            "advertiser_number": int(self.advertiser_number),
            "category": int(self.category),
            "initial_budget": float(self.budget),
            "cpa_constraint": float(self.cpa_constraint)
        }
        
        return metadata, simulation_steps

def main():
    try:
        generator = OnlineLpSimulatorGenerator(DEFAULT_DATA_PATH, DEFAULT_MODEL_PATH)
        metadata, steps = generator.generate()
        
        output_data = {
            "meta": metadata,
            "history": steps
        }
        
        # Save as JS file to avoid CORS issues
        output_file = os.path.join(CURRENT_DIR, "data/simulation_data.js")
        json_str = json.dumps(output_data, indent=2)
        
        with open(output_file, "w", encoding='utf-8') as f:
            f.write(f"window.SIMULATION_DATA = {json_str};")
            
        print(f"Successfully generated data to: {output_file}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
