Create a program, trading bot
each time you create a method create test for it
the tests should have gherkin docstring for readability
each time you come up with an approach think about another 2 possible approaches then decide which is the best and apply it 

below are going to be the requirements at high level

# Master Prompt - Part 1 of 7

## **Title**: End-to-End Trading Bot Requirements & Instructions

## **Section A: Purpose & Overview**
1. **Purpose**:  
   - We want a **Paper Trading Bot** on **Binance Testnet**.
   - The bot should implement **a popular TradingView strategy** by converting Pine Script logic into Python signals.
   - Key functionalities include **Stop-Loss & Take-Profit** risk management, **logging**, and **data storage** for future backtesting.

2. **Key Objectives**:  
   - **No Real Funds**: Completely simulate trading with zero risk to actual capital.
   - **Data Logging**: Store trade actions in a structured format for analysis (CSV or a database).
   - **Strategy Execution**: Precisely replicate the logic of a well-known TradingView script.
   - **Risk Controls**: Basic SL/TP to exit trades automatically.

3. **Scope & Limitations**:
   - **In-Scope**:
     1. Fetching OHLCV data from Binance Testnet.
     2. Converting Pine Script → Python logic for signals.
     3. Logging each trade (timestamp, price, volume, PnL).
   - **Out-of-Scope**:
     1. Real-money trading.
     2. Advanced order types (limit, trailing stop).
     3. Complex AI/ML modules.

4. **Business Rationale**:
   - **Risk-Free Validation**: Evaluate strategies before live deployment.
   - **Scalable Architecture**: Code design that allows adding new markets, advanced risk controls, or real trading in the future.
   - **Data-Driven Insights**: Thorough logs for QA, strategy tuning, or investor presentations.

---

## **Section B: High-Level System Flow**

Below is a **Markdown diagram** illustrating the **flow of operations** from fetching data to logging trades:

```mermaid
flowchart LR
    A[Start Bot] --> B[Fetch OHLCV from Binance Testnet]
    B --> C[Apply TradingView Strategy Logic]
    C --> D{Signal?}
    D -- Buy --> E[Execute Market Buy (Paper)]
    D -- Sell --> F[Execute Market Sell (Paper)]
    D -- Hold --> G[No Action]
    E --> H[Check Stop-Loss & Take-Profit]
    F --> H[Check Stop-Loss & Take-Profit]
    G --> H[Check Stop-Loss & Take-Profit]
    H --> I[Log Trade/Position Info]
    I --> B[Wait for Next Cycle]
```
# Master Prompt - Part 2 of 7

## **Section D: In-Depth Functional Requirements**

1. **Market Data Retrieval**  
   - **Binance Testnet**: Use `ccxt` to connect to the Testnet endpoint, ensuring no real capital is involved.  
   - **OHLCV**: Must retrieve Open, High, Low, Close, Volume data.  
   - **Timeframes**: Typically 1-minute or 5-minute intervals; store the default in a config (e.g., `1m`).  
   - **Data Integrity**:  
     - Log or store each new candle in `data/historical_data.csv`.  
     - Check for duplicates or overlapping timestamps to prevent data corruption.

2. **Conversion of a Popular TradingView Strategy**  
   - **Strategy Identification**: Choose one of the highest-starred, widely used scripts on TradingView (e.g., **SMA Crossover**, **RSI Divergence**, or **MACD**).  
   - **Pine Script → Python**:  
     - Translate all indicator logic (moving averages, RSI, MACD lines, etc.).  
     - Ensure **signal conditions** are mirrored exactly: if the Pine Script says `buy` at X crossing Y, the Python script must reflect the same condition.  
   - **Parameter Customization**:  
     - Use a dictionary in `config/settings.py` for user-adjustable values.  
     - Example:
       ```python
       STRATEGY_PARAMS = {
         "SMA_SHORT": 10,
         "SMA_LONG": 50,
         "RSI_PERIOD": 14,
         "RSI_OVERBOUGHT": 70,
         "RSI_OVERSOLD": 30
       }
       ```
   - **Signal Output**:  
     - `1` → BUY  
     - `-1` → SELL  
     - `0` → HOLD  

3. **Paper Trade Execution**  
   - **Market Orders**:  
     - Use `ccxt` to call something like `exchange.create_market_order("BTC/USDT", "buy", 0.001)` for a buy.  
     - Must store or log the `orderId` and result.  
   - **Position Management**:  
     - MVP can allow only **one open position** at a time for simplicity. If a position is already open, a new buy signal is ignored unless closed.  
   - **Trade Logging**:  
     - Each successful order must be appended to a CSV (`data/historical_trades.csv`) with fields:  
       - `timestamp`  
       - `side` (`BUY` or `SELL`)  
       - `entry_price`  
       - `exit_price` (if closed)  
       - `quantity`  
       - `PnL` (if closed)  
       - `stop_loss_triggered` (boolean)  
       - `take_profit_triggered` (boolean)

4. **Stop-Loss & Take-Profit Mechanics**  
   - **Stop-Loss**:  
     - Default: 2% below entry price.  
     - Triggered if `current_price <= entry_price * (1 - STOP_LOSS_PERCENT)`.  
   - **Take-Profit**:  
     - Default: 4% above entry price.  
     - Triggered if `current_price >= entry_price * (1 + TAKE_PROFIT_PERCENT)`.  
   - **Execution**:  
     - On each cycle, if an open position is active, check the last price.  
     - If SL or TP is triggered, place a **market sell** (if we’re in a long position).  
     - Log the event: mark `stop_loss_triggered = True` or `take_profit_triggered = True` as needed.

5. **Data & Logging Structure**  
   - **historical_data.csv**:  
     - `[timestamp, open, high, low, close, volume]` per candle.  
     - Possibly a `strategy_signal` column if you want to store the last known signal for each candle.  
   - **historical_trades.csv**:  
     - `[timestamp, order_id, side, entry_price, exit_price, quantity, PnL, stop_loss_triggered, take_profit_triggered]`.  
   - **trading.log** & **errors.log**:  
     - **trading.log**: Human-readable events (e.g., `2025-02-28 12:00:00 - BUY order placed at 23000 USDT`).  
     - **errors.log**: Detailed stack traces or error messages if the bot encounters exceptions.

6. **Error Handling & Resilience**  
   - **API Failures**:  
     - Implement a retry mechanism (3 attempts, exponential backoff).  
     - If all fail, log the error, skip the current cycle, and proceed on the next iteration.  
   - **Invalid Data**:  
     - If OHLCV is `None` or missing fields, log a warning, skip strategy logic for that cycle.  
   - **Position Conflicts**:  
     - If the code detects a position state mismatch (e.g., an open position in code but exchange says none), log an error. The bot might forcibly sync state by reading open orders from testnet.

7. **Priority & MVP Constraints**  
   - This is an **MVP** to validate the concept. Keep it **simple**: one pair, one strategy, one position at a time.  
   - **Future** expansions might handle multiple pairs, partial closes, advanced trailing stops, etc.

---

## **Prompt Usage:**

- Combine **Part 2** with the other parts (1, 3–7) into a single, multi-section specification.  
- Make sure to keep the **markdown format** intact for easy reading.  

**End of Part 2**  

*(Continue to **Part 3** in the next message...)*

# Master Prompt - Part 3 of 7

## **Section E: Detailed Architecture & File Structure**

Below is a recommended **folder layout** for clarity and scalability:

```plaintext
Trading_Bot/
├── main.py                     # Entry point for running the bot
├── config/
│   └── settings.py             # Configuration (API keys, intervals, strategy params)
├── strategies/
│   └── tv_strategy.py          # Conversion of popular TradingView strategy to Python
├── data/
│   ├── historical_data.csv     # Stored OHLCV data
│   └── historical_trades.csv   # Stored trade history
├── logs/
│   ├── trading.log             # Main trade activity log
│   └── errors.log              # Critical errors & exceptions
├── .env                        # Sensitive info (API keys), excluded from Git
├── .gitignore                  # Ignore .env, logs, data CSVs, etc.
└── README.md                   # Basic documentation for quick start
```
# Master Prompt - Part 4 of 7

## **Section F: Risk Management & Additional Requirements**

1. **Stop-Loss (SL)**
   - **Default**: 2% below entry (`settings.py` → `STOP_LOSS_PERCENT = 0.02`).
   - **Trigger Logic**:
     - If `last_price <= entry_price * (1 - STOP_LOSS_PERCENT)`, the bot should immediately place a **market sell** to exit.
   - **Logging**:
     - Mark `stop_loss_triggered` as `True` in `historical_trades.csv` upon closure.

2. **Take-Profit (TP)**
   - **Default**: 4% above entry (`settings.py` → `TAKE_PROFIT_PERCENT = 0.04`).
   - **Trigger Logic**:
     - If `last_price >= entry_price * (1 + TAKE_PROFIT_PERCENT)`, place a **market sell**.
   - **Logging**:
     - Mark `take_profit_triggered` as `True` in `historical_trades.csv`.

3. **Position Management**
   - MVP approach: **One open position** at a time.
   - If a buy signal occurs while a position is open, ignore it unless you decide to scale in. For MVP, keep it simple—no scaling in or out.
   - If a sell signal occurs while no position is open, do nothing.

4. **Trade Size / Amount**
   - **Fixed trade size** (e.g., 0.001 BTC). 
   - Future enhancements: dynamic sizing based on risk or capital.

5. **Error Handling**
   - On exceptions (API errors, invalid data), write to `errors.log` with a timestamp and stack trace.
   - Retry API calls up to 3 times if it’s a recoverable error (e.g., network timeout).

6. **Data Validation**
   - If fetched OHLCV data contains unexpected or None values, skip strategy logic for that cycle to avoid erroneous signals.
   - Check for overlapping timestamps in `historical_data.csv` to prevent duplicates.

7. **Security**
   - Keep `.env` out of Git. 
   - For extra safety, consider partial encryption of `.env` in shared environments, though not mandatory for local development.

8. **Roadmap for Future Risk Management**
   - Trailing stop-loss, partial closes, or advanced risk-based sizing can be added once the basic system is stable.
   - For multi-position logic, a dedicated portfolio manager component might be introduced later.

---

**End of Part 4**  

# Master Prompt - Part 5 of 7

## **Section G: Testing & Validation**

1. **Unit Tests**
   - **Data Fetch**: Mock ccxt calls to ensure the bot correctly parses OHLCV data.  
   - **Strategy Logic**: Provide synthetic data (e.g., a simple uptrend) to confirm if the strategy triggers expected buy signals.  
   - **Risk Triggers**: Test that a fake price below the stop-loss threshold immediately closes the position.  

2. **Integration Tests**
   - **End-to-End**: Let the bot run for a short period (e.g., 30 minutes) on the testnet and confirm:  
     1. **OHLCV** is being saved to `historical_data.csv` without duplication.  
     2. **Trades** appear in `historical_trades.csv` when signals occur.  
     3. **Stop-Loss/Take-Profit** logic is enforced.  
   - **Error Handling**: Force an API error (e.g., by cutting internet) to see if the bot logs an error and recovers.

3. **Performance Testing**
   - **Long-Run**: Let the bot operate continuously for 24–72 hours.  
   - **Monitoring**: Check memory usage, CPU load, and file sizes (logs, CSV) to ensure stability.

4. **User Acceptance Testing (UAT)**
   - **Paper Trading Evaluation**:  
     - Observe the trades for at least 1 day.  
     - Confirm that logs match expected signals (buy on cross, sell on cross, etc.).  
   - **Review**: Stakeholders verify that the strategy is performing logically, no catastrophic errors occur.

5. **Backtesting Considerations** (Future)
   - Once sufficient data is collected (in `historical_data.csv`), the team might implement a **backtesting module**.  
   - This module would replay historical data, feeding it into the strategy logic to compute hypothetical PnL.

6. **Documentation of Test Results**
   - A simple **test report** or table summarizing each scenario (e.g., “Stop-Loss triggered as expected”) is recommended.  
   - Keep logs and CSVs for reference and debugging.

---

**End of Part 5**  

# Master Prompt - Part 6 of 7

## **Section H: Deployment & Scalability**

1. **Local Deployment**
   - **Python**: 3.9+ recommended.
   - **Install Dependencies**:
     ```bash
     pip install ccxt pandas numpy requests python-dotenv matplotlib
     ```
   - **Run**:
     ```bash
     python main.py
     ```
   - **Logs & CSV**: Found in `logs/` and `data/`.

2. **VPS / Cloud Deployment**
   - After local tests, move to a **VPS** (e.g., DigitalOcean, Linode, AWS EC2) for continuous 24/7 operation.
   - Use **screen** or **tmux** to keep the bot running:
     ```bash
     screen -S trading_bot
     python main.py
     ```
   - Or consider **systemd** or a Docker container for auto-restarts.

3. **Horizontal Scaling** (Future)
   - If monitoring multiple pairs or multiple strategies, replicate or run separate instances for each configuration.
   - A dedicated **scheduler** or message queue (e.g., RabbitMQ) might help distribute tasks.

4. **Logging & Monitoring**
   - In production-like environments, consider a log aggregation solution (e.g., ELK stack, Grafana).
   - **Error Alerts**: Send critical errors to Slack, Discord, or email once stable.

5. **Security**
   - **API Keys**: Keep them in `.env`. For team usage, consider a secrets manager like Vault or AWS Secrets Manager.
   - **SSH Access** to VPS should be limited; use secure keys.

6. **Extensibility**
   - **Strategy**: Additional scripts can be placed in `strategies/`.
   - **Indicators**: If you want more advanced indicators, integrate something like `ta-lib`.
   - **Live Trading**: Swap out the testnet endpoint for the main Binance endpoint only after thorough testing and acceptance.

---

**End of Part 6**  

# Master Prompt - Part 7 of 7

## **Section I: Final Roadmap & Conclusion**

1. **Comprehensive Roadmap**

   | Phase | Task                                          | Description                                                                                         |
   |-------|-----------------------------------------------|-----------------------------------------------------------------------------------------------------|
   | 1     | **Project Setup**                            | Create `Trading_Bot/`, initialize Git, set up `.env` and `requirements.txt`.                         |
   | 2     | **Fetch Data & Store**                       | Implement `exchange.fetch_ohlcv` calls, append results to `historical_data.csv`.                     |
   | 3     | **Convert TradingView Strategy**             | Translate Pine Script logic to Python in `tv_strategy.py`.                                          |
   | 4     | **Implement Paper Trading Logic**            | Place market orders on Binance Testnet, log trades in `historical_trades.csv`.                       |
   | 5     | **Risk Management**                          | Add stop-loss and take-profit triggers.                                                             |
   | 6     | **Logging & Error Handling**                 | Write events to `trading.log`, errors to `errors.log`, handle API failures.                         |
   | 7     | **Testing & Validation**                     | Unit tests, integration tests, UAT.                                                                 |
   | 8     | **Refine & Deploy**                          | Optionally deploy to a VPS for continuous operation.                                                |
   | 9     | **Future Upgrades**                          | Backtesting engine, advanced risk strategies, multi-exchange, real-money trading, notifications.     |

2. **Recommended Best Practices**
   - **Coding Style**: Follow Python’s PEP 8.  
   - **Clean Architecture**: Keep separate modules for data, strategy, and execution.  
   - **Continuous Integration**: If possible, set up a pipeline to run tests on push.

3. **Conclusion & Next Steps**
   - This completes the **MVP** specification for a Binance Testnet paper trading bot:
     1. Secure environment (.env).  
     2. Reliable data flow (OHLCV from Testnet).  
     3. Strategy conversion (Pine → Python).  
     4. Basic risk management (SL/TP).  
     5. Logging & CSV storage for future backtesting.  
   - **Key Next Step**: Implement each phase in code, test thoroughly in paper mode, then decide on expansions (like real trading).

4. **Maintenance & Feedback Loop**
   - Keep logs for at least a few weeks to analyze strategy performance.  
   - Regularly tune strategy parameters in `settings.py` based on logged PnL and observed performance.  
   - Gather stakeholder feedback after each stable release.

---

## **Final Instructions for the Complete Prompt**
Combine **all 7 parts** (Parts 1 through 7) into one large **master prompt**.  
- Retain **Markdown** formatting.  
- Ensure **mermaid diagrams**, tables, and bullet lists remain intact.  
- Copy-paste each part in order (1 → 7).  

This final prompt outlines everything needed to build, test, and deploy a **Paper Trading Bot** on **Binance Testnet** using a **popular TradingView strategy** with **Stop-Loss & Take-Profit** risk management, **logging**, and a path toward future enhancements.

**End of Part 7**  

