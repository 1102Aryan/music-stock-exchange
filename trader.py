import random


class Trader:
    """
    Trader starts with a initial fund amount, initialised with an id
    """

    def __init__(self, trader_id, initial_fund=10000.0):
        self.trader_id = trader_id
        self.initial_fund = initial_fund
        self.cash = initial_fund
        self.portfolio = {}

    def wealth(self, snapshot):
        """
        total calculated from shares value + cash in liquid
        """
        total = self.cash
        for artist_id, quantity in self.portfolio.items():
            if artist_id in snapshot:
                total += quantity * snapshot[artist_id]["price"]
        return total

    def can_buy(self, price):
        """
        Checks if trader can buy the stock with 2% extra as safety
        """
        return self.cash >= price * 1.02

    def holds(self, artist_id):
        """
        Checks how many shares of the stock trader owns
        """
        return self.portfolio.get(artist_id, 0)

    def pick(self, snapshot, timestep, genre_popularity):
        return []


class RandomTrader(Trader):
    """Baseline model"""

    def pick(self, snapshot, timestep, genre_popularity):
        """
        if random number is less than 0.05 buys
        else if random number is less than 0.1 sells the stock if present
        """
        orders = []
        for aid, info in snapshot.items():
            r = random.random()
            if r < 0.05 and self.can_buy(info["price"]):
                orders.append((aid, "buy"))
            elif r < 0.10 and self.holds(aid) > 0:
                orders.append((aid, "sell"))
        return orders


class MomentumTrader(Trader):
    """
    Buys stock when they are rising and sells stock when they are declining
    """

    def pick(self, snapshot, timestep, genre_popularity):
        """
        Uses history and looks at the previous 10 prices to see if a stock is rising or declining
        if it rises more than 5% then buys
        else if it declines more than 5% it sells the stock
        """
        orders = []
        for aid, info in snapshot.items():
            history = info["history"]
            if len(history) < 10:
                continue
            old_price = history[-10]
            new_price = info["price"]
            if old_price <= 0:
                continue
            change = (new_price - old_price) / old_price
            if change > 0.05 and self.can_buy(info["price"]):
                orders.append((aid, "buy"))
            elif change < -0.05 and self.holds(aid) > 0:
                orders.append((aid, "sell"))
        return orders


class MeanRevTrader(Trader):
    """
    If the price is below the average then buy
    if the price is above the average then sell
    - Idea that the price will always come back to the average
    """

    def pick(self, snapshot, timestep, genre_popularity):
        """
        Looks into 20 of the history array and takes the average price
        if the current price is less than 10% of the average then buy
        else if the current price is over than 10% of the average then sell
        """
        orders = []
        for aid, info in snapshot.items():
            history = info["history"]
            if len(history) < 20:
                continue
            mean = sum(history) / len(history)
            price = info["price"]
            if price < mean * 0.9 and self.can_buy(price):
                orders.append((aid, "buy"))
            elif price > mean * 1.1 and self.holds(aid) > 0:
                orders.append((aid, "sell"))
        return orders


class ValueTrader(Trader):
    """
    Looks at the trend of the stock 
    if stock is performing better than the logn term average then it is overvalued and sell
    if stock is performing worse than the long term average then it is undervalued and buy
    """
    
    def pick(self, snapshot, timestep, genre_popularity):
        """
        Looks at the previous 50 price range 
        and takes the average of the last 50 and last 10
        checks to see if the short term is less than long term by 5% then buy
        else if short term is greater than the long term by 5% then sell
        """
        orders = []
        for aid, info in snapshot.items():
            history = info["history"]
            if len(history) < 50:
                continue
            long_avg = sum(history[-50:]) / 50
            short_avg = sum(history[-10:]) / 10
            if short_avg < long_avg * 0.95 and self.can_buy(info["price"]):
                orders.append((aid, "buy"))
            elif short_avg > long_avg * 1.05 and self.holds(aid) > 0:
                orders.append((aid, "sell"))
        return orders


class GenreTrader(Trader):
    """
    Trades based on the popularity of the genre
    if the genre popularity is increasing then buy
    if the genre popularity is decreasing then sell
    """
    def __init__(self, trader_id, initial_fund=10000):
        super().__init__(trader_id, initial_fund)
        self.popularity_history = {}

    def pick(self, snapshot, timestep, genre_popularity):
        """
        
        """
        for genre, heat in genre_popularity.items():
            if genre not in self.popularity_history:
                self.popularity_history[genre] = []
            self.popularity_history[genre].append(heat)
        orders = []
        for aid, info in snapshot.items():
            genre = info["genre"]
            if (
                genre not in self.popularity_history
                or len(self.popularity_history[genre]) < 5
            ):
                continue
            popularity_now = self.popularity_history[genre][-1]
            popularity_before = self.popularity_history[genre][-5]
            trend = popularity_now - popularity_before
            if trend > 0.05 and self.can_buy(info["price"]):
                orders.append((aid, "buy"))
            elif trend < -0.05 and self.holds(aid) > 0:
                orders.append((aid, "sell"))
        return orders


class LoyaltyTrader(Trader):
    def pick(self, snapshot, timestep, genre_popularity):
        """
        
        """
        orders = []
        for aid, info in snapshot.items():
            loyalty = info["loyalty"]
            stage = info["stage"]
            price = info["price"]
            if (
                loyalty > 0.6
                and stage != "declining"
                and self.holds(aid) == 0
                and self.can_buy(price)
            ):
                orders.append((aid, "buy"))
            elif loyalty < 0.4 and self.holds(aid) > 0:
                orders.append((aid, "sell"))
        return orders


class TrendTrader(Trader):
    def pick(self, snapshot, timestep, genre_popularity):
        """ """
        orders = []
        for aid, info in snapshot.items():
            price = info["price"]
            if info["viral"] > 0.15 and self.can_buy(price):
                orders.append((aid, "buy"))
            elif info["viral"] < 0.05 and self.holds(aid) > 0:
                orders.append((aid, "sell"))
            if info["scandal"] > 0.2 and self.holds(aid) > 0:
                orders.append((aid, "sell"))
        return orders


class CareerTrader(Trader):
    def pick(self, snapshot, timestep, genre_popularity):
        """ """
        orders = []
        for aid, info in snapshot.items():
            stage = info["stage"]
            talent = info["talent"]
            price = info["price"]
            if stage == "emerging" and talent > 0.5 and self.can_buy(price):
                orders.append((aid, "buy"))
            elif (
                stage == "rising"
                and talent > 0.6
                and self.holds(aid) == 0
                and self.can_buy(price)
            ):
                orders.append((aid, "buy"))
            elif stage in ["peak", "established", "declining"] and self.holds(aid) > 0:
                orders.append((aid, "sell"))
        return orders
    
class AdaptiveTrader(Trader):
    """
    Switches between financial and music-domain trading to maximise profit
    """
    
    def pick(self, snapshot, timestep, genre_popularity):
        pass
