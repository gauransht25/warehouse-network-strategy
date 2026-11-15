# E-Commerce Warehouse Network Strategy Analysis

A reproducible scenario analysis of fulfillment coverage in 30 Indian cities using 10 assumed warehouse sites and a greedy 3-site expansion heuristic.

**Data integrity:** Demand volumes are synthetic; city coordinates approximate; existing warehouse sites illustrative, not verified Amazon/Flipkart facilities. Haversine distance is straight-line, not driving distance.

## Run
```bash
pip install -r requirements.txt
python analyze.py
```

## Method
1. Calculate nearest-site great-circle distance using Haversine (6371.0088 km Earth radius).
2. Add three distinct city sites greedily to minimize demand-weighted distance.
3. Report baseline versus proposed network coverage.

## Project deliverables
`analyze.py`, `data/`, `sql/`, `outputs/` (maps, coverage, metrics, SQLite).

## Limitations
This is not a live logistics system. No real order volume, capacity, population, traffic, cost or SLA data is used. Greedy selection is not a global optimality guarantee.
