import math
import random


class Market:
    def __init__(self, artists, config=None):
        config = config or {}
        # list of artist in a dictionary stored with an unique id
        self.artists = {a.id: a for a in artists}
        # volatility multiplier increases the market change and random events involved 
        self.volatility = config.get("volatility", 1.0)
        # log of everything that happened
        self.events = []

    def genre_popularity(self, genre, timestamp):
        """
        The genre popularity using a sine wave to simulate the nature of trends
        genre's are assigned a number
        """
        
        genre_period = {"pop": 0, "rock": 1, "hip-hop": 2,
                        "electronic": 3, "jazz": 4, "r&b": 5}
        period = genre_period[genre]
        # the period are multiplied by 33 and then added by the timestamp - offsetting the waves
        # The changes the trends of all teh genres peak so they are not the same 
        cycle = math.sin((timestamp + period * 33) / 200 * 2 * math.pi)
        return cycle * 0.3

    def random_events(self, timestep):
        """
        The random_events run every timestep and randomly picks if anything happens to the artist
        """
        
        for artist in self.artists.values():
            # .5% chance for virality 
            if random.random() < 0.005 * self.volatility:
                artist.viral += random.uniform(0.2, 1.0)
                self.events.append(("viral", timestep, artist.id))
            # .3% chance for a scandal to occur
            if random.random() < 0.003 * self.volatility:
                # randomly selects the multiplier of the scandal
                artist.scandal += random.uniform(0.1, 0.8)
                # lose fans based on scandal and artist loyalty
                artist.fans *= (1 - artist.scandal * 0.1 * (1 - artist.loyalty))
                self.events.append(("scandal", timestep, artist.id))
            # 1% chance of dropping an album
            if random.random() < 0.01:
                artist.albums += 1
                self.events.append(("album", timestep, artist.id))

            # if the artist is declining there is 0.8% chance for nostalgia 
            if artist.stage == "declining" and random.random() < 0.008:
                # increases artist virality 
                artist.viral += random.uniform(0.1, 0.4)
                self.events.append(("nostalgia", timestep, artist.id))

    def update_prices(self, buys, sells):
        """
        Updates the price of artist based on how many buys and solds 
        takes the net from buy and sold. if more buys, price goes up. if more sells, price goes down
        
        """
        
        for artist in self.artists.values():
            buy_count = buys.get(artist.id, 0)
            sell_count = sells.get(artist.id, 0)

            if buy_count + sell_count > 0:
                net = buy_count - sell_count
                # stops the market from breaking when there is a big buy/sell
                artist.price *= (1 + net * 0.02 / (abs(net) + 10))
            # slows the pull back of the price closer to the true price
            artist.price += (artist.value - artist.price) * 0.05
            # random gauss is used to apply a small amount of fluctuation to the price
            artist.price *= (1 + random.gauss(0, 0.005))
            # prevents negative numbers
            artist.price = max(1.0, artist.price)

    def get_snapshot(self):
        """
        Stores all the current data of market into a dictionary
        """
        
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
