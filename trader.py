import random
from artist import Artist, GENRES, STAGES
from market import Market


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
        stores the genre popularity 
        looks at the history to see if it is getting more popular or less
        if trend is above .05 then buy else if it is less than -.05 then sell
        """
        for genre, popularity in genre_popularity.items():
            if genre not in self.popularity_history:
                self.popularity_history[genre] = []
            self.popularity_history[genre].append(popularity)
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
            if trend > 0.025 and self.can_buy(info["price"]):
                orders.append((aid, "buy"))
            elif trend < -0.025 and self.holds(aid) > 0:
                orders.append((aid, "sell"))
        return orders


class LoyaltyTrader(Trader):
    """
    Buys artists with a more loyal fanbase. Safer investment.
    """
    
    def pick(self, snapshot, timestep, genre_popularity):
        """
        buys stocks which have high loyalty, not declining, and not already owned
        if loyalty is low (0.4<) sell
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
    """
    Buys artist that have high virality and sells artist that are in a scandal
    """
    
    def pick(self, snapshot, timestep, genre_popularity):
        """
        if virality is above .15 buys
        else if virality is less than .05 then sell
        if scandal > .2 sell
        """
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
    """
    Buys artist that are emerging talent
    sells artist when they have reached peak  
    """
    
    def pick(self, snapshot, timestep, genre_popularity):
        """
        if artist is emerging and talent > 0.5 then buy
        else if artist is rising and talent > 0.6 and not already bought then buy
        once reached peak [peak, established, declining] sell
        """
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
    def __init__(self, trader_id, initial_fund=10000):
        super().__init__(trader_id, initial_fund)
        self.momentum_score = 0
        self.meanrev_score = 0
        self.using_momentum = True
        self.prev_wealth = initial_fund
    
    def pick(self, snapshot, timestep, genre_popularity):
        """
        Every 50 steps it checks which option performs better
        if the current wealth is better than previous then if its on momentum its score increases else the other score increase
        if its worse the scores are decreased for the model
        selects the agent and carries out the logic
        """
        
        if timestep > 0 and timestep % 50 == 0:
            current_wealth = self.wealth(snapshot)
            if current_wealth > self.prev_wealth:
                if self.using_momentum:
                    self.momentum_score += 1
                else:
                    self.meanrev_score += 1
            else:
                if self.using_momentum:
                    self.meanrev_score += 1
                    
                else:
                    self.momentum_score += 1
            if self.momentum_score >= self.meanrev_score:
                self.using_momentum = True
            else:
                self.using_momentum = False
            self.prev_wealth = current_wealth
        orders = []
        for aid, info in snapshot.items():
            history = info["history"]
            if len(history) < 20:
                continue
            price = info["price"]
            
            if self.using_momentum:
                if len(history) >= 10:
                    old = history[-10]
                    change = (price - old) / old if old > 0 else 0
                    if change > 0.05 and self.can_buy(price):
                        orders.append((aid, "buy"))
                    elif change < -0.05 and self.holds(aid) > 0:
                        orders.append((aid, "sell"))
            else:
                avg = sum(history[-20:]) / 20
                dev = (price - avg) / avg if avg > 0 else 0
                if dev < -0.1 and self.can_buy(price):
                    orders.append((aid, "buy"))
                elif dev > 0.1 and self.holds(aid) > 0:
                    orders.append((aid, "sell"))
        return orders
                
class HybridTrader(Trader):
    """
    Applies both finance and music knowledge
    buys when price momentum is up and genre is increasing in popularity
    sells when either option is not true
    """
    def __init__(self, trader_id, initial_fund=10000):
        super().__init__(trader_id, initial_fund)
        self.popularity_history = {}
        
        
    def pick(self, snapshot, timestep, genre_popularity):
        """
        if price rise and genre rise is true then buy if it is less than an amount then sell 
        """
        
        for genre, popularity in genre_popularity.items():
            if genre not in self.popularity_history:
                self.popularity_history[genre] = []
            self.popularity_history[genre].append(popularity)
            
        orders = []
        for aid, info in snapshot.items():
            history = info["history"]
            genre = info["genre"]
            price = info["price"]
            
            if len(history) < 10:
                continue
            if genre not in self.popularity_history or len(self.popularity_history[genre]) < 5:
                continue
            
            prev_price = history[-10]
            
            if prev_price:
                price_outcome = (price - prev_price) /  prev_price
            if prev_price > 0 and (price_outcome) > 0.03:
                price_rise = True
            else:
                price_rise = False
                
            genre_trend = self.popularity_history[genre][-1] - self.popularity_history[genre][-5]
            if genre_trend > 0.03:
                genre_rise = True
            else:
                genre_rise = False
                
            if price_rise and genre_rise and self.can_buy(price):
                orders.append((aid, "buy"))
                
            if price_outcome < -0.03 and not genre_rise and self.holds(aid) > 0:
                orders.append((aid, "sell"))
        return orders
            
class QLearningTrader(Trader):
    """
    Qlearning learns which actions works best in different cases
    current has 4 states , 500 steps to learn
    
    
    starts exploring randomly and starts learning
    
    """
    
    def __init__(self, trader_id, initial_fund=10000):
        super().__init__(trader_id, initial_fund)
        self.q_table = {}
        self.temporal_difference = 0
        self.learning_rate = 0.1
        self.explore_rate = 0.3
        self.discount = 0.9
        self.prev_wealth = initial_fund
        self.prev_actions = {}
        
    
    def get_state(self, info):
        """
        Turns the trading mechnics into a simple state: (price_up, growing)
        
        """
        
        history = info["history"]
        
        if len(history) >= 10 and history[-10] > 0:
            change = (info["price"] - history[-10]) / history[-10]
            if change > 0.02:
                price_up = True
            else:
                price_up = False
        else:
            price_up = False
        if info["stage"] in ["emerging", "rising"]:
            growing = True
        else:
            growing = False
        return (price_up, growing)
            
        
    def get_q(self, state):
        """
        Gets q value for the state
        if not in q table makes one 
        """
        
        if state not in self.q_table:
            self.q_table[state] = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        return self.q_table[state]    
        
    def pick(self, snapshot, timestep, genre_popularity):
        """
        reward is calculated from wealth change since prev weaalth
        and learns from prev steps actions
        
        """
        
        current_wealth = self.wealth(snapshot)
        reward = current_wealth - self.prev_wealth
        self.prev_wealth = current_wealth
        
        for aid, (prev_state, prev_action) in self.prev_actions.items():
            if aid in snapshot:
                new_state = self.get_state(snapshot[aid])
                prev_q = self.get_q(prev_state)
                new_q = self.get_q(new_state)
                best_option = max(new_q.values())
                
                # Q learning formula
                prev_q[prev_action] += self.learning_rate * (reward + self.discount * best_option - prev_q[prev_action])
        orders = []
        self.prev_actions = {}
        
        for aid, info in snapshot.items():
            state = self.get_state(info)
            q = self.get_q(state)
            # either explores new step or pick best known action
            if random.random() < self.explore_rate:
                action = random.choice(["buy", "sell", "hold"])
            else:
                action = max(q, key=q.get)
            
            if action == "buy" and self.can_buy(info["price"]):
                orders.append((aid, "buy"))
            elif action == "sell" and self.holds(aid) > 0:
                orders.append((aid, "sell"))
            else:
                action = "hold"
            self.prev_actions[aid] = (state, action)
        return orders
    
    
            
class QLearningBaseTrader(Trader):
    """
    The base trader is the same as the QLearningTrader, designed specifcally for the qlearning_experiment
    current has 4 states
    
    
    starts exploring randomly and starts learning
    
    """
    
    def __init__(self, trader_id, initial_fund=10000):
        super().__init__(trader_id, initial_fund)
        self.q_table = {}
        self.temporal_difference = 0
        self.learning_rate = 0.1
        self.explore_rate = 0.3
        self.discount = 0.9
        self.prev_wealth = initial_fund
        self.prev_actions = {}
        
    
    def get_state(self, info):
        """
        Turns the trading mechnics into a simple state: (price_up, growing)
        
        """
        
        history = info["history"]
        
        if len(history) >= 10 and history[-10] > 0:
            change = (info["price"] - history[-10]) / history[-10]
            if change > 0.02:
                price_up = True
            else:
                price_up = False
        else:
            price_up = False
        if info["stage"] in ["emerging", "rising"]:
            growing = True
        else:
            growing = False
        return (price_up, growing)
            
        
    def get_q(self, state):
        """
        Gets q value for the state
        if not in q table makes one 
        """
        
        if state not in self.q_table:
            self.q_table[state] = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        return self.q_table[state]    
        
    def pick(self, snapshot, timestep, genre_popularity):
        """
        reward is calculated from wealth change since prev weaalth
        and learns from prev steps actions
        
        """
        
        current_wealth = self.wealth(snapshot)
        reward = current_wealth - self.prev_wealth
        self.prev_wealth = current_wealth
        
        for aid, (prev_state, prev_action) in self.prev_actions.items():
            if aid in snapshot:
                new_state = self.get_state(snapshot[aid])
                prev_q = self.get_q(prev_state)
                new_q = self.get_q(new_state)
                best_option = max(new_q.values())
                
                # Q learning formula
                prev_q[prev_action] += self.learning_rate * (reward + self.discount * best_option - prev_q[prev_action])
        orders = []
        self.prev_actions = {}
        
        for aid, info in snapshot.items():
            state = self.get_state(info)
            q = self.get_q(state)
            # either explores new step or pick best known action
            if random.random() < self.explore_rate:
                action = random.choice(["buy", "sell", "hold"])
            else:
                action = max(q, key=q.get)
            
            if action == "buy" and self.can_buy(info["price"]):
                orders.append((aid, "buy"))
            elif action == "sell" and self.holds(aid) > 0:
                orders.append((aid, "sell"))
            else:
                action = "hold"
            self.prev_actions[aid] = (state, action)
        return orders
    
    
                
class QLearningHighTrader(Trader):
    """
    Qlearning high trader is a more sophisticated version of the base trader
    
    Has 18 states
    
    
    starts exploring randomly and starts learning
    
    """
    
    def __init__(self, trader_id, initial_fund=10000):
        super().__init__(trader_id, initial_fund)
        self.q_table = {}
        self.temporal_difference = 0
        self.learning_rate = 0.1
        self.explore_rate = 0.3
        self.discount = 0.9
        self.min_explore_rate = 0.07
        self.prev_wealth = initial_fund
        self.prev_actions = {}
        
    
    def get_state(self, info):
        """
        Turns the trading mechnics into a simple state: (price_up, growing)
        added 3 options
        {price, career, virality} 
        """
        
        history = info["history"]
        
        if len(history) >= 10 and history[-10] > 0:
            change = (info["price"] - history[-10]) / history[-10]
            if change > 0.02:
                price = "rise"
            elif change < -0.02:
                price = "decrease"
            else:
                price = "flat"
        else:
            price = "flat"
        if info["stage"] in ["emerging", "rising"]:
            career = "rising"
        elif info["stage"] == "peak":
            career = "peak"
        else:
            career = "falling"
            
        if info["viral"] > 0.1:
            viral = True
        else:
            viral = False
        return (price, career, viral)
            
        
    def get_q(self, state):
        """
        Gets q value for the state
        if not in q table makes one 
        """
        
        if state not in self.q_table:
            self.q_table[state] = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        return self.q_table[state]    
        
    def pick(self, snapshot, timestep, genre_popularity):
        """
        reward is calculated from wealth change since prev weaalth
        and learns from prev steps actions
        
        """
        
        current_wealth = self.wealth(snapshot)
        reward = current_wealth - self.prev_wealth
        self.prev_wealth = current_wealth
        
        for aid, (prev_state, prev_action) in self.prev_actions.items():
            if aid in snapshot:
                new_state = self.get_state(snapshot[aid])
                prev_q = self.get_q(prev_state)
                new_q = self.get_q(new_state)
                best_option = max(new_q.values())
                
                # Q learning formula
                prev_q[prev_action] += self.learning_rate * (reward + self.discount * best_option - prev_q[prev_action])
        self.explore_rate = max(self.min_explore_rate, self.explore_rate * 0.995)
        orders = []
        self.prev_actions = {}
        
        for aid, info in snapshot.items():
            state = self.get_state(info)
            q = self.get_q(state)
            # either explores new step or pick best known action
            if random.random() < self.explore_rate:
                action = random.choice(["buy", "sell", "hold"])
            else:
                action = max(q, key=q.get)
            
            if action == "buy" and self.can_buy(info["price"]):
                orders.append((aid, "buy"))
            elif action == "sell" and self.holds(aid) > 0:
                orders.append((aid, "sell"))
            else:
                action = "hold"
            self.prev_actions[aid] = (state, action)
        return orders
                
              
        
    
                
class QLearningPreHighTrader(Trader):
    """
    Qlearning high trader is a more sophisticated version of the base trader
    
    Has 18 states
    
    
    starts exploring randomly and starts learning
    
    """
    
    def __init__(self, trader_id, initial_fund=10000, pretrain_steps=500):
        super().__init__(trader_id, initial_fund)
        self.q_table = {}
        self.temporal_difference = 0
        self.learning_rate = 0.1
        self.explore_rate = 0.3
        self.discount = 0.9
        self.min_explore_rate = 0.07
        self.prev_wealth = initial_fund
        self.pretrain_steps = pretrain_steps
        self.prev_actions = {}
        
    
    def get_state(self, info):
        """
        Turns the trading mechnics into a simple state: (price_up, growing)
        added 3 options
        {price, career, virality} 
        """
        
        history = info["history"]
        
        if len(history) >= 10 and history[-10] > 0:
            change = (info["price"] - history[-10]) / history[-10]
            if change > 0.02:
                price = "rise"
            elif change < -0.02:
                price = "decrease"
            else:
                price = "flat"
        else:
            price = "flat"
        if info["stage"] in ["emerging", "rising"]:
            career = "rising"
        elif info["stage"] == "peak":
            career = "peak"
        else:
            career = "falling"
            
        if info["viral"] > 0.1:
            viral = True
        else:
            viral = False
        return (price, career, viral)
            
        
    def get_q(self, state):
        """
        Gets q value for the state
        if not in q table makes one 
        """
        
        if state not in self.q_table:
            self.q_table[state] = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        return self.q_table[state]    
        
    def pretrain(self, times=3):
        for run in range(times):
            random.seed(run * 999)
            mock_artists = []
            for i in range(100):
                genre = random.choice(GENRES)
                talent = max(0.05, min(0.95, random.gauss(0.5, 0.15)))
                loyalty = max(0.05, min(0.95, random.gauss(0.5, 0.15)))
                stage = random.choices(STAGES, weights=[0.3, 0.25, 0.15, 0.2, 0.1])[0]
                mock_artists.append(Artist(f"a{i:03d}", genre, talent, loyalty, stage))

            mock_market = Market(mock_artists)
            for a in mock_artists:
                a.value = a.calculate_value(mock_market.genre_popularity(a.genre, 0))
                a.price = a.value

            for t in range(self.pretrain_steps):
                mock_market.random_events(t)
                popularity = {g: mock_market.genre_popularity(g, t) for g in GENRES}
                for a in mock_artists:
                    a.steps(popularity[a.genre])

                snapshot = mock_market.get_snapshot()
                current_wealth = self.wealth(snapshot)
                reward = current_wealth - self.prev_wealth
                self.prev_wealth = current_wealth

                for aid, (prev_state, prev_action) in self.prev_actions.items():
                    if aid in snapshot:
                        new_state = self.get_state(snapshot[aid])
                        prev_q = self.get_q(prev_state)
                        new_q = self.get_q(new_state)
                        best_option = max(new_q.values())
                        prev_q[prev_action] += self.learning_rate * (reward + self.discount * best_option - prev_q[prev_action])

                buys = {}
                sells = {}
                self.prev_actions = {}

                for aid, info in snapshot.items():
                    state = self.get_state(info)
                    q = self.get_q(state)
                    if random.random() < self.explore_rate:
                        action = random.choice(["buy", "sell", "hold"])
                    else:
                        action = max(q, key=q.get)

                    artist = mock_market.artists[aid]
                    if action == "buy" and self.cash >= artist.price * 1.01:
                        self.cash -= artist.price * 1.01
                        self.portfolio[aid] = self.portfolio.get(aid, 0) + 1
                        buys[aid] = buys.get(aid, 0) + 1
                    elif action == "sell" and self.portfolio.get(aid, 0) > 0:
                        self.cash += artist.price * 0.99
                        self.portfolio[aid] -= 1
                        if self.portfolio[aid] == 0:
                            del self.portfolio[aid]
                        sells[aid] = sells.get(aid, 0) + 1
                    else:
                        action = "hold"
                    self.prev_actions[aid] = (state, action)

                mock_market.update_prices(buys, sells)

            self.cash = self.initial_fund
            self.portfolio = {}
            self.prev_wealth = self.initial_fund
            self.prev_actions = {}

        self.explore_rate = 0.1
        
        
    def pick(self, snapshot, timestep, genre_popularity):
        """
        reward is calculated from wealth change since prev weaalth
        and learns from prev steps actions
        
        """
        
        current_wealth = self.wealth(snapshot)
        reward = current_wealth - self.prev_wealth
        self.prev_wealth = current_wealth
        
        for aid, (prev_state, prev_action) in self.prev_actions.items():
            if aid in snapshot:
                new_state = self.get_state(snapshot[aid])
                prev_q = self.get_q(prev_state)
                new_q = self.get_q(new_state)
                best_option = max(new_q.values())
                
                # Q learning formula
                prev_q[prev_action] += self.learning_rate * (reward + self.discount * best_option - prev_q[prev_action])
        self.explore_rate = max(self.min_explore_rate, self.explore_rate * 0.995)
        orders = []
        self.prev_actions = {}
        
        for aid, info in snapshot.items():
            state = self.get_state(info)
            q = self.get_q(state)
            # either explores new step or pick best known action
            if random.random() < self.explore_rate:
                action = random.choice(["buy", "sell", "hold"])
            else:
                action = max(q, key=q.get)
            
            if action == "buy" and self.can_buy(info["price"]):
                orders.append((aid, "buy"))
            elif action == "sell" and self.holds(aid) > 0:
                orders.append((aid, "sell"))
            else:
                action = "hold"
            self.prev_actions[aid] = (state, action)
        return orders


class QLearningPreBaseTrader(Trader):
    """
    Pretrained QLearning
    Runs pretrain() on mock markets before the real simulation so the
    Q-table starts with prior experience instead of all zeros.
    """

    def __init__(self, trader_id, initial_fund=10000, pretrain_steps=500):
        super().__init__(trader_id, initial_fund)
        self.q_table = {}
        self.learning_rate = 0.1
        self.explore_rate = 0.3
        self.discount = 0.9
        self.prev_wealth = initial_fund
        self.pretrain_steps = pretrain_steps
        self.prev_actions = {}

    def get_state(self, info):
        history = info["history"]
        if len(history) >= 10 and history[-10] > 0:
            change = (info["price"] - history[-10]) / history[-10]
            price_up = change > 0.02
        else:
            price_up = False
        growing = info["stage"] in ["emerging", "rising"]
        return (price_up, growing)

    def get_q(self, state):
        if state not in self.q_table:
            self.q_table[state] = {"buy": 0.0, "sell": 0.0, "hold": 0.0}
        return self.q_table[state]

    def pretrain(self, times=3):
        for run in range(times):
            random.seed(run * 999)
            mock_artists = []
            for i in range(100):
                genre = random.choice(GENRES)
                talent = max(0.05, min(0.95, random.gauss(0.5, 0.15)))
                loyalty = max(0.05, min(0.95, random.gauss(0.5, 0.15)))
                stage = random.choices(STAGES, weights=[0.3, 0.25, 0.15, 0.2, 0.1])[0]
                mock_artists.append(Artist(f"a{i:03d}", genre, talent, loyalty, stage))

            mock_market = Market(mock_artists)
            for a in mock_artists:
                a.value = a.calculate_value(mock_market.genre_popularity(a.genre, 0))
                a.price = a.value

            for t in range(self.pretrain_steps):
                mock_market.random_events(t)
                popularity = {g: mock_market.genre_popularity(g, t) for g in GENRES}
                for a in mock_artists:
                    a.steps(popularity[a.genre])

                snapshot = mock_market.get_snapshot()
                current_wealth = self.wealth(snapshot)
                reward = current_wealth - self.prev_wealth
                self.prev_wealth = current_wealth

                for aid, (prev_state, prev_action) in self.prev_actions.items():
                    if aid in snapshot:
                        new_state = self.get_state(snapshot[aid])
                        prev_q = self.get_q(prev_state)
                        new_q = self.get_q(new_state)
                        best_option = max(new_q.values())
                        prev_q[prev_action] += self.learning_rate * (reward + self.discount * best_option - prev_q[prev_action])

                buys = {}
                sells = {}
                self.prev_actions = {}

                for aid, info in snapshot.items():
                    state = self.get_state(info)
                    q = self.get_q(state)
                    if random.random() < self.explore_rate:
                        action = random.choice(["buy", "sell", "hold"])
                    else:
                        action = max(q, key=q.get)

                    artist = mock_market.artists[aid]
                    if action == "buy" and self.cash >= artist.price * 1.01:
                        self.cash -= artist.price * 1.01
                        self.portfolio[aid] = self.portfolio.get(aid, 0) + 1
                        buys[aid] = buys.get(aid, 0) + 1
                    elif action == "sell" and self.portfolio.get(aid, 0) > 0:
                        self.cash += artist.price * 0.99
                        self.portfolio[aid] -= 1
                        if self.portfolio[aid] == 0:
                            del self.portfolio[aid]
                        sells[aid] = sells.get(aid, 0) + 1
                    else:
                        action = "hold"
                    self.prev_actions[aid] = (state, action)

                mock_market.update_prices(buys, sells)

            self.cash = self.initial_fund
            self.portfolio = {}
            self.prev_wealth = self.initial_fund
            self.prev_actions = {}

        self.explore_rate = 0.1

    def pick(self, snapshot, timestep, genre_popularity):
        current_wealth = self.wealth(snapshot)
        reward = current_wealth - self.prev_wealth
        self.prev_wealth = current_wealth

        for aid, (prev_state, prev_action) in self.prev_actions.items():
            if aid in snapshot:
                new_state = self.get_state(snapshot[aid])
                prev_q = self.get_q(prev_state)
                new_q = self.get_q(new_state)
                best_option = max(new_q.values())
                prev_q[prev_action] += self.learning_rate * (reward + self.discount * best_option - prev_q[prev_action])
        orders = []
        self.prev_actions = {}

        for aid, info in snapshot.items():
            state = self.get_state(info)
            q = self.get_q(state)
            if random.random() < self.explore_rate:
                action = random.choice(["buy", "sell", "hold"])
            else:
                action = max(q, key=q.get)

            if action == "buy" and self.can_buy(info["price"]):
                orders.append((aid, "buy"))
            elif action == "sell" and self.holds(aid) > 0:
                orders.append((aid, "sell"))
            else:
                action = "hold"
            self.prev_actions[aid] = (state, action)
        return orders

                    
