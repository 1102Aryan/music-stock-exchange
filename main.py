import random

from artist import Artist, GENRES, STAGES
from market import Market
from trader import (
    RandomTrader, MomentumTrader, MeanRevTrader, ValueTrader,
    GenreTrader, CareerTrader, LoyaltyTrader, TrendTrader, AdaptiveTrader
)


def create_artists(num=100, seed=42):
    random.seed(seed)
    artists = []
    for i in range(num):
        genre = random.choice(GENRES)
        talent = max(0.05, min(0.95, random.gauss(0.5, 0.15)))
        loyalty = max(0.05, min(0.95, random.gauss(0.5, 0.15)))
        stage = random.choices(STAGES, weights=[0.3, 0.25, 0.15, 0.2, 0.1])[0]
        artists.append(Artist(f"a{i:03d}", genre, talent, loyalty, stage))
    return artists


def run_simulation(agents, num_artists=100, num_steps=500, config=None, seed=42):
    random.seed(seed)
    artists = create_artists(num_artists, seed)
    market = Market(artists, config)

    for a in artists:
        a.value = a.calculate_value(market.genre_popularity(a.genre, 0))
        a.price = a.value

    for t in range(num_steps):
        market.random_events(t)

        popularity = {g: market.genre_popularity(g, t) for g in GENRES}
        for a in artists:
            a.steps(popularity[a.genre])

        snapshot = market.get_snapshot()
        buys = {}
        sells = {}

        for agent in agents:
            orders = agent.pick(snapshot, t, popularity)

            for artist_id, action in orders:
                artist = market.artists[artist_id]
                if action == "buy" and agent.cash >= artist.price * 1.01:
                    agent.cash -= artist.price * 1.01
                    agent.portfolio[artist_id] = agent.portfolio.get(artist_id, 0) + 1
                    buys[artist_id] = buys.get(artist_id, 0) + 1
                elif action == "sell" and agent.portfolio.get(artist_id, 0) > 0:
                    agent.cash += artist.price * 0.99
                    agent.portfolio[artist_id] -= 1
                    if agent.portfolio[artist_id] == 0:
                        del agent.portfolio[artist_id]
                    sells[artist_id] = sells.get(artist_id, 0) + 1

        market.update_prices(buys, sells)

    snapshot = market.get_snapshot()
    print(f"\n{'Trader':<15} {'Final Wealth':>14} {'Profit':>10}")
    print("-" * 42)
    for agent in agents:
        final_wealth = agent.wealth(snapshot)
        profit = final_wealth - agent.initial_fund
        sign = "+" if profit >= 0 else ""
        print(f"{agent.trader_id:<15} ${final_wealth:>13,.2f} {sign}{profit:>+9,.2f}")


def main():
    agents = [
        RandomTrader("random"),
        MomentumTrader("momentum"),
        MeanRevTrader("mean_rev"),
        ValueTrader("value"),
        GenreTrader("genre"),
        CareerTrader("career"),
        LoyaltyTrader("loyalty"),
        TrendTrader("trend"),
        AdaptiveTrader("adaptive")
    ]

    run_simulation(agents)


if __name__ == "__main__":
    main()
