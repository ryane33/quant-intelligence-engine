# Quant Intelligence Engine

> A research-grade quantitative intelligence platform for systematic market research, probabilistic forecasting, machine learning, AI-assisted information extraction, strategy construction, portfolio optimization, risk management, and paper execution.

## Overview

Quant Intelligence Engine (QIE) is an open-source quantitative finance research project designed to explore how structured market data, statistical methods, machine learning, alternative data, and AI-assisted research can be combined into a rigorous systematic investment workflow.

The project is intentionally designed as more than an AI stock picker or trading bot.

QIE separates:

- data collection
- feature engineering
- statistical research
- machine learning
- unstructured-information processing
- opportunity detection
- strategy construction
- portfolio optimization
- risk management
- execution
- model evaluation

The long-term objective is to create a reproducible quantitative research environment capable of generating hypotheses, testing them against historical data, producing calibrated probabilistic forecasts, constructing candidate trades, managing portfolio risk, and evaluating decisions through backtesting and paper trading.

> **Current status:** Early development. Core project infrastructure and research architecture are being built first. No live-money trading is currently supported or intended during the initial research phases.

---

## Core Philosophy

QIE is built around several principles.

### Research before trading

Every strategy should begin as a hypothesis.

```text
Hypothesis
    ↓
Data
    ↓
Feature Engineering
    ↓
Statistical Testing
    ↓
Modeling
    ↓
Out-of-Sample Validation
    ↓
Backtesting
    ↓
Forward / Shadow Testing
    ↓
Paper Trading


————


A strategy is not considered useful simply because it performs well in one historical test.

⸻

AI is a research layer, not the trading system

Large language models are intended primarily for processing information that traditional numerical models cannot easily interpret.

Examples include:

* SEC filings
* earnings transcripts
* corporate disclosures
* news
* government policy
* congressional financial disclosures
* executive/public-figure statements
* qualitative investment research

AI-generated information is converted into structured features that can be evaluated alongside traditional quantitative data.

Numerical calculations, statistics, portfolio optimization, risk limits, and execution controls remain deterministic wherever possible.

⸻

Predictions should express uncertainty

QIE aims to produce probabilistic forecasts rather than deterministic price predictions.

Example:

P(positive 20-day return)      0.68
P(return > 5%)                 0.41
P(drawdown > 5%)               0.17

Expected excess return         +3.2%
Expected volatility             7.8%

Forecast quality can then be evaluated using tools such as:

* calibration curves
* Brier score
* log loss
* prediction intervals
* out-of-sample error
* realized versus predicted return distributions

⸻

No-trade is a valid strategy

An attractive company, event, or statistical signal does not necessarily imply an attractive trade.

QIE separates: 

Opportunity Detection
        ↓
Strategy Construction
        ↓
Portfolio / Risk Evaluation
        ↓
Execution Decision

Possible strategy outcomes may eventually include:

* long equity
* short equity
* long call
* long put
* defined-risk option spreads
* covered strategies
* cash-secured strategies
* no trade

The system should be capable of rejecting an opportunity when liquidity, volatility, valuation, portfolio exposure, or risk/reward is unfavorable.

Architecture

                       QUANT INTELLIGENCE ENGINE

 STRUCTURED DATA                               UNSTRUCTURED DATA
 ───────────────                               ─────────────────
 Market prices                                 SEC filings
 Volume                                        Earnings transcripts
 Options                                       News
 Fundamentals                                  Government releases
 Macro data                                    Congressional disclosures
                                                Public-figure events
        │                                               │
        └───────────────────┬───────────────────────────┘
                            ↓
                     DATA INGESTION
                            ↓
                  POINT-IN-TIME STORAGE
                            ↓
                   FEATURE ENGINEERING
                            ↓
              ┌─────────────┴─────────────┐
              ↓                           ↓
     STATISTICAL RESEARCH          AI RESEARCH LAYER
     Event studies                 Filing analysis
     Regression                    Event classification
     Time series                   Policy analysis
     Hypothesis testing            Research synthesis
     Bayesian methods              Bull / bear analysis
              │                           │
              └─────────────┬─────────────┘
                            ↓
                    MACHINE LEARNING
                            ↓
                       ALPHA MODEL
                            ↓
                   OPPORTUNITY SCORE
                            ↓
                    STRATEGY ENGINE
                            ↓
                     STRATEGY SCORE
                            ↓
                PORTFOLIO OPTIMIZATION
                            ↓
                       RISK ENGINE
                            ↓
                  EXECUTION / TIMING
                            ↓
                    PAPER BROKERAGE
                            ↓
                 POSITION MONITORING
                            ↓
                      EXIT ENGINE
                            ↓
                    OUTCOME MEMORY
                            ↓
                RESEARCH / RETRAINING

Planned Research Areas

QIE is intended to support several categories of quantitative research.

Market and factor research

Initial baseline signals may include:

* momentum
* valuation
* quality
* volatility
* liquidity
* earnings revisions
* market regime
* macroeconomic variables

These provide a benchmark against which more complex signals can be evaluated.

⸻

Event-driven research

Potential research questions include:

* Do major policy announcements create predictable second-order equity effects?
* Can event classification improve short-horizon return forecasts?
* Do public executive statements produce measurable delayed effects across suppliers, customers, or competitors?
* Does LLM-extracted information from earnings calls improve prediction beyond conventional financial factors?

⸻

Congressional disclosures

Public congressional financial disclosures may be studied as an alternative dataset.

A critical requirement is strict point-in-time handling:

A strategy may only use a transaction once that transaction was publicly disclosed.

Potential research areas include:

* abnormal returns after disclosure
* disclosure delay
* transaction size
* sector concentration
* committee relevance
* options versus equity transactions
* clustered activity across officials

The project does not assume these signals contain alpha. They must be tested empirically.

⸻

Market regime detection

Future research may explore regime classification using:

* volatility
* interest rates
* credit spreads
* market breadth
* correlations
* inflation
* liquidity
* momentum

Possible techniques include:

* clustering
* Gaussian mixture models
* hidden Markov models
* Bayesian regime models

⸻

Machine Learning

The project is designed to compare models empirically rather than assuming complexity produces better predictions.

Planned model families include:

Baselines

* linear regression
* logistic regression
* regularized regression

Tree models

* random forests
* XGBoost
* LightGBM
* CatBoost

Time-series models

* ARIMA
* GARCH
* regime models

Probabilistic models

* Bayesian inference
* calibrated classifiers
* predictive distributions

Neural methods

* PyTorch-based models
* financial NLP models
* sequence models

Reinforcement learning

Reinforcement learning may be explored later for sequential portfolio or execution problems, but only after simpler statistical and machine-learning baselines have been established.

⸻

Quantitative Research Standards

Backtests should account for:

* look-ahead bias
* survivorship bias
* point-in-time availability
* corporate actions
* transaction costs
* bid/ask spreads
* slippage
* liquidity constraints
* execution delays
* overlapping labels
* multiple hypothesis testing
* data snooping
* model overfitting

Validation methods may include:

* walk-forward validation
* rolling out-of-sample testing
* bootstrap analysis
* permutation testing
* factor-adjusted event studies
* probabilistic calibration

⸻

Research Memory

QIE is designed to preserve the complete history of a prediction.
Example:

Prediction ID
Timestamp
Ticker
Information cutoff
Feature vector
Model version
Forecast probabilities
Expected return
Opportunity score
Strategy recommendation
Strategy score
Risk decision
Entry decision
Execution result
Exit decision
Realized return
Forecast error

This creates an auditable research ledger that can later be used for:

* calibration
* retraining
* model comparison
* regime analysis
* strategy postmortems
* hypothesis generation

⸻

Strategy Engine

A dedicated strategy layer will eventually evaluate how an opportunity should be expressed.

Potential inputs:

* expected direction
* expected magnitude
* forecast horizon
* probability distribution
* volatility
* implied volatility
* liquidity
* options chain
* catalyst timing
* portfolio exposure

Candidate strategies may include:

* equity
* short equity
* calls
* puts
* defined-risk spreads
* no trade

Undefined-risk option strategies are not part of the initial design.

⸻

Risk Management

Risk controls are intended to remain deterministic.

Potential constraints include:

* maximum position size
* maximum sector exposure
* portfolio volatility limits
* leverage limits
* liquidity requirements
* maximum options exposure
* drawdown constraints
* correlation limits
* strategy whitelists

AI components should not be able to override hard risk controls.

⸻

Algorithms and Data Structures

QIE is also designed as a computer-science-intensive project.

Potential applications include:

Priority queues

Prioritize incoming events based on:

* materiality
* novelty
* time sensitivity
* confidence
* expected impact

Hash maps

Fast lookup for:

* ticker → company
* security ID → asset
* event ID → event
* model ID → model metadata

Graphs

Build economic relationship graphs connecting:

* companies
* sectors
* suppliers
* customers
* countries
* executives
* policies
* government agencies
* technologies

Graph traversal may help identify first-, second-, and third-order exposure to events.

Optimization

Portfolio construction may use constrained optimization for:

* expected return
* volatility
* factor exposure
* sector limits
* turnover
* liquidity
* CVaR

⸻

Technology Stack

Core

* Python 3.12
* Git
* GitHub
* uv
* VS Code

Data

* NumPy
* Pandas
* Polars
* PyArrow
* DuckDB
* Parquet

Statistics

* SciPy
* statsmodels
* ARCH
* Pingouin

Machine Learning

* scikit-learn
* XGBoost
* LightGBM
* CatBoost
* Optuna

Deep Learning / NLP

* PyTorch
* Hugging Face Transformers
* sentence-transformers
* spaCy

Quantitative Finance

* vectorbt
* QuantStats
* Empyrical Reloaded
* CVXPY
* QuantLib
* Alpaca
* FRED
* exchange calendars

AI / Research Agents

* Ollama
* Qwen
* LangGraph
* PydanticAI
* LiteLLM
* LlamaIndex

Research Infrastructure

* MLflow
* DVC
* NetworkX
* Prefect

Application Layer

* FastAPI
* Uvicorn
* Streamlit

Engineering Quality

* pytest
* Hypothesis
* Ruff
* mypy
* pyright
* pre-commit
* Bandit
* pip-audit

Project Structure

quant-intelligence-engine/
│
├── src/qie/
│   ├── data/
│   │   ├── ingestion/
│   │   ├── validation/
│   │   └── point_in_time/
│   │
│   ├── features/
│   │   ├── fundamentals/
│   │   ├── technical/
│   │   ├── macro/
│   │   ├── events/
│   │   └── alternative/
│   │
│   ├── statistics/
│   ├── models/
│   ├── agents/
│   ├── alpha/
│   ├── scoring/
│   ├── strategy/
│   ├── portfolio/
│   ├── execution/
│   ├── memory/
│   ├── backtesting/
│   └── utils/
│
├── research/
│   ├── hypotheses/
│   ├── experiments/
│   └── notebooks/
│
├── model_registry/
├── dashboard/
├── tests/
├── docs/
└── data/

Development Roadmap

Phase 1 — Quantitative Foundation

* market-data provider abstraction
* historical OHLCV ingestion
* validated schemas
* Parquet/DuckDB storage
* return calculations
* volatility
* baseline features
* performance analytics

Phase 2 — Baseline Alpha Models

* momentum
* quality
* valuation
* simple factor combinations
* statistical benchmarks

Phase 3 — Research Framework

* event studies
* hypothesis testing
* bootstrapping
* regression
* walk-forward validation
* probabilistic calibration

Phase 4 — Machine Learning

* return forecasting
* direction classification
* volatility forecasting
* model comparison
* hyperparameter optimization
* model registry

Phase 5 — AI Research Layer

* SEC filing extraction
* earnings transcript analysis
* event classification
* policy research
* bull/bear research
* structured feature extraction

Phase 6 — Alternative Data

* congressional disclosures
* policy events
* executive/public-figure events
* event knowledge graph
* second-order exposure analysis

Phase 7 — Strategy Construction

* equity strategy comparison
* options analysis
* Greeks
* expected payoff
* probability of profit
* strategy scoring

Phase 8 — Portfolio and Risk

* covariance models
* portfolio optimization
* concentration limits
* risk limits
* strategy allocation

Phase 9 — Paper Execution

* Alpaca integration
* shadow trading
* paper orders
* position monitoring
* exit engine

Phase 10 — Research Dashboard

* opportunity rankings
* forecasts
* model performance
* open positions
* experiment history
* calibration
* strategy results

⸻

Testing Progression

QIE will progress through four environments:

Historical Backtest
        ↓
Forward / Shadow Testing
        ↓
Paper Trading
        ↓
Live Trading

Live-money trading is not part of the initial development phase.

⸻

Open-Source Research References

QIE will study and learn from established open-source projects including:

* Microsoft Qlib
* RD-Agent
* FinRL
* FinRL-X
* FinGPT
* FinRobot
* LEAN
* NautilusTrader
* vectorbt
* OpenBB

These projects serve as architectural and research references.

QIE is not intended to simply reproduce any one of them.

⸻

Current Status

Version: Early development

Completed:

* project architecture
* dependency environment
* configuration framework
* testing framework
* linting / formatting
* pre-commit validation
* GitHub repository

Next milestone:

Build the market-data ingestion, validation, storage, and return-calculation foundation.

⸻

Disclaimer

This project is for research, educational, and software-development purposes.

Nothing in this repository constitutes investment advice, financial advice, or a recommendation to buy or sell any security.

Backtested, simulated, and paper-trading results do not represent actual trading performance and may differ materially from live-market results.

⸻

Author

Ryan Esajas

Quantitative finance, financial technology, machine learning, and systematic-investing research project.
