import csv
import random

import time
import math
import os
import matplotlib
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from scipy import stats

import artist
import market
import trader
from  trader import RandomTrader, CareerTrader, TrendTrader, GenreTrader, MeanRevTrader, LoyaltyTrader, ValueTrader, MomentumTrader
import main


def agents():
    return [
        RandomTrader("random"),
        CareerTrader("career"),
        TrendTrader("trend"),
        GenreTrader("genre"),
        MeanRevTrader("mean_rev"),
        LoyaltyTrader("loyalty"),
        ValueTrader("value"),
        MomentumTrader("momentum")
    ]
    


def experiment_strategy(trials=30, output_dir="results"):
    table = []
    for trial in range(trials):
        all_agents = agents()
        results = main.run_simulation(all_agents, num_artists=100, num_steps=500, seed=trial*100)
        for agent in all_agents:
            snapshot = results["snapshot"]
            wealth = agent.wealth(snapshot)
            table.append({
                "trial": trial,
                "agent": agent.trader_id,
                "wealth": wealth,
                "precentage_change": (wealth - 100000)/ 100 
            })
    df = pd.DataFrame(table)
    df.to_csv(f"{output_dir}/experiment_strategy.csv", index=False)
    return df

def experiment_volatility(trials=30, output_dir="results"):
    table = []
    voltatilities = [0.2, 0.5, 0.7, 1.5, 2.5]
    
    for v in voltatilities:
        for trial in range(trials):
            all_agents = agents()
            results = main.run_simulation(all_agents, num_artists=100, num_steps=500, config={"volatility": v},
                                          seed=trial * 100 + int(v * 1000))
            
            for agent in all_agents:
                snapshot = results["snapshot"]
                wealth = agent.wealth(snapshot)
                table.append({
                "trial": trial,
                "volatility": v,
                "agent": agent.trader_id,
                "wealth": wealth,
                "precentage_change": (wealth - 100000)/ 100 
                })
    df = pd.DataFrame(table)
    df.to_csv(f"{output_dir}/experiment_volatility.csv", index=False)
    return df

def experiment_population(trials=30, output_dir="results"):
    table = []
    
    compositions = {
        "balanced": [
            "random", "momentum", "mean_rev", "value", "genre", "career", "loyalty", "trend"
        ],
        "financial_focused": ["random", "momentum", "momentum", "mean_rev", "mean_rev", "value", "value", "value", "career"
        ],
        "music_focused": ["genre", "genre", "career", "career", "loyalty", "loyalty", "trend", "momentum"
        ]
    }
    
    for comps, comp_list in compositions.items():
        for trial in range(trials):
            all_agents = agents()
            
            for id, name in enumerate(comp_list):
                agent_list = {
                    "random": RandomTrader, "momentum": MomentumTrader, "mean_rev": MeanRevTrader,
                    "value": ValueTrader, "genre": GenreTrader, "career": CareerTrader,
                    "loyalty": LoyaltyTrader, "trend": TrendTrader
                }
                
                all_agents.append(agent_list[name](f"{name}_{id}"))
            
            results = main.run_simulation(all_agents, num_artists=100, num_steps=500,
                                          seed=trial * 100 + len(comps))
            
            for agent in all_agents:
                snapshot = results["snapshot"]
                wealth = agent.wealth(snapshot)
                table.append({
                "trial": trial,
                "composition": comps,
                "agent": agent.trader_id,
                "wealth": wealth,
                "precentage_change": (wealth - 100000)/ 100 
                })
    df = pd.DataFrame(table)
    df.to_csv(f"{output_dir}/experiment_population.csv", index=False)
    return df
            


if __name__ == "__main__":
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)
    
    start = time.time()
    
    experiment_strategy(trials=30, output_dir=output_dir)
    experiment_volatility(trials=30, output_dir=output_dir)
    experiment_population(trials=30, output_dir=output_dir)
    
    total = time.time() - start
    print(f"Completed running in {total:.0f}s, saved in {output_dir}/")    
    
    