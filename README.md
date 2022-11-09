# technical_analysis
A simple script that calculates some common technical indicators for norwegian stocks

## Data
The sript peforms simple technical analysis on all stocks where there is available price data on Yahoo Finance. The section focuses on momentum (rate of change) on different horizons, the rank of one month reversial (the worst performing stocks the last month) and the volatility for the last 80 and 30 days. I subesquently create two dataframes:

- Stocks where short term RoC (10 days) is higher than 21 day RoC and where the stocks are within the top 50 lowest volatility  
- Stocks where short term RoC (21 days) is higher than 50 day RoC and where the stocks are within the top 50 lowest volatility The result is the intersection of the two lists.  
