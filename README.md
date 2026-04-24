<h1 align="center">music-stock-exchange</h1>

## Project Description
 Music Stock Exchange is a culature stock exchange where music artist are traded as stocks. Trading agents compete to see how a financial agent performs compared to a music-domain agent in maximising profit.

The project is inspired by the Bristol Stock Exchange (Cliff, 2018).

## Agents

### Financial 
- **RandomTrader** - Baseline
- **MomentumTrader** - Buys when prices rises, sells when prices fall
- **MeanRevTrader**  - Buys when prices fall, sells when prices rise
- **ValueTrader** - Compares short term to long term to find the average 

### Music-Domain
- **GenreTrader** - Buys artist in genres that are popular
- **CareerTrader** - Buys artist that are emerging, sells at their peak
- **LoyaltyTrader** - Buys artist with loyal fans
- **TrendTrader** - Buys artist based on virality, sells when scandals occurr

### Adaptive
- **AdaptiveTrader** - Switches between momentum and MeanRev based on which is performing better



## Screenshot

## Project Structure
```
├── main.py             # Main simulation (artists, market, agents)
├── experiments.py      # Runs experiments and creates charts
├── results/            # Output CSVs and charts (generated)
└── README.md
```


## How to Setup
To build from source code:

1. Clone the repository: `git clone https://github.com/1102Aryan/music-stock-exchange`
2. Install the required libraries: `pip install -r requirements.txt`
3. Run the application: `python main.py`
4. Run all experiments: `python experiments.py`
5. Results and charts can be viewed in `results/` folder


<div align="center">
  
  [Report Bug](https://github.com/1102Aryan/music-stock-exchange/issues) • [Request Feature](https://github.com/1102Aryan/music-stock-exchange/issues)
</div>
