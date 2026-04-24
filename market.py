import math
import random


class Market:
    def __init__(self, artists, config=None):
        config = config or {}
        self.artists = {a.id: a for a in artists}
        self.volatility = config.get("volatility", 1.0)
        self.events = []

    def genre_popularity(self, genre, timestamp):
        genre_period = {"pop": 0, "rock": 1, "hip-hop": 2,
                        "electronic": 3, "jazz": 4, "r&b": 5}
        period = genre_period[genre]
        cycle = math.sin((timestamp + period * 33) / 200 * 2 * math.pi)
        return cycle * 0.6

    def random_events(self, timestep):
        for artist in self.artists.values():
            if random.random() < 0.005 * self.volatility:
                artist.viral += random.uniform(0.2, 1.0)
                self.events.append(("viral", timestep, artist.id))

            if random.random() < 0.003 * self.volatility:
                artist.scandal += random.uniform(0.1, 0.8)
                artist.fans *= (1 - artist.scandal * 0.1 * (1 - artist.loyalty))
                self.events.append(("scandal", timestep, artist.id))

            if random.random() < 0.01:
                artist.albums += 1
                self.events.append(("album", timestep, artist.id))

            if artist.stage == "declining" and random.random() < 0.008:
                artist.viral += random.uniform(0.1, 0.4)
                self.events.append(("nostalgia", timestep, artist.id))

    def update_prices(self, buys, sells):
        for artist in self.artists.values():
            buy_count = buys.get(artist.id, 0)
            sell_count = sells.get(artist.id, 0)

            if buy_count + sell_count > 0:
                net = buy_count - sell_count
                artist.price *= (1 + net * 0.02 / (abs(net) + 10))

            artist.price += (artist.value - artist.price) * 0.05
            artist.price *= (1 + random.gauss(0, 0.005))
            artist.price = max(1.0, artist.price)

    def get_snapshot(self):
        snapshot = {}
        for artist in self.artists.values():
            snapshot[artist.id] = {
                "price": artist.price,
                "history": list(artist.price_history),
                "genre": artist.genre,
                "stage": artist.stage,
                "talent": artist.talent,
                "loyalty": artist.loyalty,
                "fans": artist.fans,
                "viral": artist.viral,
                "scandal": artist.scandal,
            }
        return snapshot
