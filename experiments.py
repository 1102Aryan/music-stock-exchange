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
from trader import RandomTrader, CareerTrader, TrendTrader, GenreTrader, MeanRevTrader, LoyaltyTrader, ValueTrader, MomentumTrader, AdaptiveTrader, HybridTrader, QLearningTrader
import main

COLOURS = {
    "random": "#999999", "momentum": "#e74c3c", "mean_rev": "#e67e22",
    "value": "#f1c40f", "genre": "#2ecc71", "career": "#3498db",
    "loyalty": "#9b59b6", "trend": "#1abc9c", "adaptive": "#34495e",
    "hybrid": "#e91e63", "q_learning": "#00bcd4",
}

def agents():
    return [
        RandomTrader("random"),
        CareerTrader("career"),
        TrendTrader("trend"),
        GenreTrader("genre"),
        MeanRevTrader("mean_rev"),
        LoyaltyTrader("loyalty"),
        ValueTrader("value"),
        MomentumTrader("momentum"),
        AdaptiveTrader("adaptive"),
        HybridTrader("hybrid"),
        QLearningTrader("q_learning")
        
    ]

def experiment_strategy(trials=30, output_dir="results"):
    table = []
    for trial in range(trials):
        all_agents = agents()
        results = main.run_simulation(all_agents, num_artists=100, num_steps=500, seed=trial * 100)
        for agent in all_agents:
            snapshot = results["snapshot"]
            wealth = agent.wealth(snapshot)
            table.append({
                "trial": trial,
                "agent": agent.trader_id,
                "wealth": wealth,
                "return_pct": (wealth - 10000) / 100,
            })
    df = pd.DataFrame(table)
    df.to_csv(f"{output_dir}/experiment_strategy.csv", index=False)
    return df

def experiment_volatility(trials=30, output_dir="results"):
    table = []
    volatilities = [0.2, 0.5, 0.7, 1.5, 2.5]

    for v in volatilities:
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
                    "return_pct": (wealth - 10000) / 100,
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
        "financial_focused": [
            "random", "momentum", "momentum", "mean_rev", "mean_rev", "value", "value", "value", "career"
        ],
        "music_focused": [
            "genre", "genre", "career", "career", "loyalty", "loyalty", "trend", "momentum"
        ],
    }

    agent_list = {
        "random": RandomTrader, "momentum": MomentumTrader, "mean_rev": MeanRevTrader,
        "value": ValueTrader, "genre": GenreTrader, "career": CareerTrader,
        "loyalty": LoyaltyTrader, "trend": TrendTrader,
    }

    for comps, comp_list in compositions.items():
        for trial in range(trials):
            all_agents = []
            for id, name in enumerate(comp_list):
                all_agents.append(agent_list[name](f"{name}_{id}"))
            results = main.run_simulation(all_agents, num_artists=100, num_steps=500,
                                          seed=trial * 100 + len(comps))
            for agent in all_agents:
                snapshot = results["snapshot"]
                wealth = agent.wealth(snapshot)
                base_name = agent.trader_id.rsplit("_", 1)[0]
                table.append({
                    "trial": trial,
                    "composition": comps,
                    "agent": agent.trader_id,
                    "agent_type": base_name,
                    "wealth": wealth,
                    "return_pct": (wealth - 10000) / 100,
                })
    df = pd.DataFrame(table)
    df.to_csv(f"{output_dir}/experiment_population.csv", index=False)
    return df


def experiment_chart_strategy(output_dir="results"):
    df = pd.read_csv(f"{output_dir}/experiment_strategy.csv")
    fig, ax = plt.subplots(figsize=(12, 6))
    order = df.groupby("agent")["return_pct"].median().sort_values(ascending=False).index
    sns.boxplot(data=df, x="agent", y="return_pct", order=order, hue="agent", palette=COLOURS, legend=False, ax=ax)
    ax.set_xlabel("Agent")
    ax.set_ylabel("Return (%)")
    ax.set_title("Experiment 1: Strategy Tournament")
    ax.axhline(y=0, color="black", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{output_dir}/chart_strategy.png", dpi=150)
    plt.close()

    print("Experiment_Strategy_Results")
    print(f"{'Agent':<15} {'Mean':>10} {'Median':>10}")
    for agent in order:
        s = df[df["agent"] == agent]["return_pct"]
        print(f"{agent:<15} {s.mean():>+9.1f}% {s.median():>+9.1f}%")

    financial = df[df["agent"].isin(["random", "momentum", "mean_rev", "value"])]["return_pct"]
    domain = df[df["agent"].isin(["genre", "career", "loyalty", "trend"])]["return_pct"]
    u, p = stats.mannwhitneyu(financial, domain, alternative="two-sided")
    print(f"\nFinancial vs Domain: U={u:.0f}, p={p:.6f}")
    print(f"  {'Significant' if p < 0.05 else 'Not significant'} at p=0.05")


def experiment_chart_volatility(output_dir="results"):
    df = pd.read_csv(f"{output_dir}/experiment_volatility.csv")
    fig, ax = plt.subplots(figsize=(12, 6))
    for agent in df["agent"].unique():
        subset = df[df["agent"] == agent]
        means = subset.groupby("volatility")["return_pct"].mean()
        ax.plot(means.index, means.values, marker="o",
                label=agent, color=COLOURS.get(agent, "#ccc"), linewidth=2)

    ax.set_xlabel("Volatility")
    ax.set_ylabel("Mean Return (%)")
    ax.set_title("Experiment 2: Performance Across Volatility Levels")
    ax.legend(bbox_to_anchor=(1.02, 1), loc="upper left", fontsize=9)
    ax.axhline(y=0, color="black", linestyle="--", alpha=0.3)
    fig.tight_layout()
    fig.savefig(f"{output_dir}/chart_volatility.png", dpi=150)
    plt.close()

    print("Experiment_Volatility_Results")
    for v in sorted(df["volatility"].unique()):
        best = df[df["volatility"] == v].groupby("agent")["return_pct"].mean().idxmax()
        val = df[df["volatility"] == v].groupby("agent")["return_pct"].mean().max()
        print(f"  Volatility {v}: {best} ({val:+.1f}%)")


def experiment_chart_population(output_dir="results"):
    df = pd.read_csv(f"{output_dir}/experiment_population.csv")

    pivot = df.pivot_table(values="return_pct", index="agent_type",
                           columns="composition", aggfunc="mean")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(pivot, annot=True, fmt=".1f", cmap="RdYlGn", center=0,
                ax=ax, linewidths=0.5)
    ax.set_title("Experiment 3: Returns by Agent Type and Market Composition")
    fig.tight_layout()
    fig.savefig(f"{output_dir}/chart_population.png", dpi=150)
    plt.close()

    print("Experiment_Population_Result")
    for comp in sorted(df["composition"].unique()):
        best = df[df["composition"] == comp].groupby("agent_type")["return_pct"].mean().idxmax()
        val = df[df["composition"] == comp].groupby("agent_type")["return_pct"].mean().max()
        print(f"  {comp}: {best} ({val:+.1f}%)")


if __name__ == "__main__":
    output_dir = "results"
    os.makedirs(output_dir, exist_ok=True)

    start = time.time()

    experiment_strategy(trials=30, output_dir=output_dir)
    experiment_volatility(trials=30, output_dir=output_dir)
    experiment_population(trials=30, output_dir=output_dir)

    experiment_chart_strategy(output_dir)
    experiment_chart_volatility(output_dir)
    experiment_chart_population(output_dir)

    total = time.time() - start
    print(f"Completed running in {total:.0f}s, saved in {output_dir}/")
