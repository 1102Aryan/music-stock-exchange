import math
import random

GENRES = ["pop", "rock", "hip-hop", "electronic", "jazz", "r&b"]
STAGES = ["emerging", "rising", "peak", "established", "declining"]


class Artist:
    def __init__(self, id, genre, talent, loyalty, stage="rising"):
        self.id = id
        self.genre = genre
        self.talent = talent
        self.loyalty = loyalty
        self.stage = stage
        fans_by_stage = {"emerging": 200, "rising": 800, "peak": 5000, "established": 3000, "declining": 700}
        self.fans = float(fans_by_stage.get(stage, 200))
        self.albums = 0
        self.viral = 0.0
        self.scandal = 0.0
        self.price = 0.0
        self.value = 0.0
        self.price_history = []

    def calculate_value(self, genre_popularity):
        """
        Determines the value of the artist 
        """
        base = self.talent * 100
        genre_times = 1.0 + genre_popularity * 0.5
        fan_times = 1.0 + self.loyalty * math.log1p(self.fans) / 10
        temp = 1.0 + self.viral - self.scandal
        return max(1.0, base * genre_times * fan_times * temp)

    def steps(self, genre_popularity):
        """
        represents the natural progression of the artist
        """
        
        idx = STAGES.index(self.stage)
        # chance artist might progress to next stage
        probs = {"emerging": 0.02, "rising": 0.03, "peak": 0.02, "established": 0.01, "declining": 0}
        if idx < 4 and random.random() < probs[self.stage]:
            self.stage = STAGES[idx + 1]
        # fans increase if they are in one of these stages
        if self.stage in ["emerging", "rising", "peak"]:
            self.fans *= 1.01
        # fans decrease if they are in declining
        elif self.stage == "declining":
            self.fans *= (1 - 0.1 * (1 - self.loyalty))

        # decreases the multiplied by 10%
        self.viral *= 0.9
        self.scandal *= 0.9

        # calculates the true value
        self.value = self.calculate_value(genre_popularity)
        self.price_history.append(self.price)
