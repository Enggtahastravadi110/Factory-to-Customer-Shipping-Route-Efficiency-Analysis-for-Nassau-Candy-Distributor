# Factory-to-Customer Shipping Route Efficiency Analysis
### Nassau Candy Distributor | Unified Mentor Internship Project
###A data analysis project and interactive Streamlit dashboard that measures how efficiently Nassau Candy Distributor ships products from its factories to customers across the US, at route, region, state and ship-mode level.

###Live dashboard: https://factorytocustomershippingrouteefficiency.streamlit.app/

A data analysis project and interactive Streamlit dashboard that measures how efficiently Nassau Candy Distributor ships products from its factories to customers across the US, at route, region, state and ship-mode level.

**Live dashboard:** _add your Streamlit link here_

---

## Important: Data Limitation

> **The shipping lead times in this dataset are not realistic.**
>
> Order dates run from **January 2024 to December 2025**, but ship dates run from **June 2026 to June 2030**. This produces lead times of roughly **904 to 1,642 days** (mean about 1,320 days). No lead time is negative, and there are no missing dates, but the ship dates appear to be synthetic or shifted.
>
> A visible symptom: **Same Day shipping (average 1,333 days) is not faster than Standard Class (average 1,314 days)**, which would not happen with real delivery data.
>
> **How this project handles it:** raw values are kept, and all conclusions are framed as **relative comparisons between routes** (which routes, states and modes perform better or worse than others), not as real-world delivery times. The delay threshold is set as a percentile (75th percentile = 1,638 days) instead of a fixed number of days. Findings about absolute delivery speed should not be drawn from this dataset.

---

## Business Problem

Nassau Candy ships from several factories to customers nationwide, but logistics decisions are made without route-level efficiency intelligence. The company lacks clarity on:

- Which factory-to-customer routes are consistently efficient
- Which routes experience frequent delays
- How performance varies by region, state and ship mode
- Where geographic bottlenecks exist

## Dataset

`Nassau_Candy_Distributor.csv` has 10,194 order lines and 18 columns, including Order Date, Ship Date, Ship Mode, Region, State/Province, Product Name, Sales, Units, Gross Profit and Cost.

- No missing values and no duplicate rows
- 4 ship modes, 4 regions, 15 products, 59 states and provinces (includes Canadian provinces)
- **Factory is not in the raw data.** It was derived by mapping each product to its factory using the product-factory table in the project brief, and factory coordinates come from the same brief.

| Factory | Orders |
|---|---|
| Lot's O' Nuts | 5,692 |
| Wicked Choccy's | 4,152 |
| Secret Factory | 217 |
| The Other Factory | 100 |
| Sugar Shack | 33 |

## Methodology

1. **Data cleaning and validation:** parse `DD-MM-YYYY` dates, drop invalid or negative lead times, standardize text and geographic fields, remove duplicates.
2. **Feature engineering:** lead time (Ship Date − Order Date), product-to-factory mapping, factory coordinates, route labels (Factory → Region and Factory → State), Standard vs Expedited grouping, profit margin and cost per unit.
3. **Route aggregation:** shipments, average, median and standard deviation of lead time, and delay frequency for each route.
4. **Efficiency benchmarking:** Route Efficiency Score (0 to 100, min-max normalized average lead time), Top 10 and Bottom 10 routes. Routes with fewer than **10 orders** are excluded from rankings because their averages are unreliable.
5. **Geographic bottleneck analysis:** regional and state comparison, congestion-prone states (high volume, slower than average, more delays than average), US heatmap.
6. **Ship mode analysis:** lead time, spread, delay frequency and descriptive cost-time tradeoff by mode.

## KPIs

| KPI | Definition |
|---|---|
| Shipping Lead Time | Ship Date − Order Date |
| Average Lead Time | Mean lead time per route |
| Route Volume | Number of orders per route |
| Delay Frequency | % of shipments above the lead-time threshold |
| Route Efficiency Score | Normalized lead-time performance (100 = fastest, 0 = slowest) |

## Key Findings

_All findings are relative, because of the data limitation above._

- **Overall:** 10,194 shipments, average lead time 1,320.8 days, delay frequency 21.1%, profit margin 65.9%.
- **Region is not the main driver.** The four regions differ by only about 12 days (Gulf 1,311 to Interior 1,323). **State-level differences are much larger** (about 220 days between fastest and slowest states with at least 30 orders).
- **Route extremes (at least 10 orders):** fastest state route is Wicked Choccy's → Nevada (about 1,182 days); slowest is Wicked Choccy's → New Mexico (about 1,489 days).
- **Congestion-prone states** (high volume and slower with more delays than average): Washington, Tennessee and Indiana are the clearest cases, with New Jersey and Georgia also qualifying.
- **Ship mode:** expedited modes were not faster than Standard Class in this data (see the data limitation). Cost per unit (about 1.23 to 1.26) and profit margin (about 65.7% to 66.1%) are almost identical across modes.
- **Volume is very uneven across factories,** so small routes need a minimum-order filter before ranking.

## Dashboard

The Streamlit app has four modules:

| Module | Contents |
|---|---|
| Route Efficiency Overview | Top/Bottom 10 routes, route leaderboard, CSV download |
| Geographic Shipping Map | US heatmap, regional bottleneck view, congestion-prone states |
| Ship Mode Comparison | Lead time, spread, delay %, cost-time tradeoff, Standard vs Expedited |
| Route Drill-Down | State-level KPIs, factory routes, distribution, order-level shipment timelines |

**Filters:** order date range, region, state/province, ship mode, delay-threshold slider and minimum orders per route.

The dashboard shows the data limitation as a warning banner at the top of every page.

## Project Structure

```
nassau-candy-dashboard/
├── app.py                  # Streamlit dashboard
├── requirements.txt        # Python dependencies
├── README.md
├── clean_shipments.csv     # Cleaned data with engineered features
├── factory_kpis.csv    
├── region_routes.csv   
├── overall_kpis.csv
├── state_routes.csv
├── state_performance.csv   
└── Analysis.ipynb          # Notebook with the full analysis (optional)
```

## Run Locally

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Then open `http://localhost:8501`.

## Tech Stack

Python, pandas, NumPy, Plotly, Streamlit, Jupyter.

## Limitations

- Unrealistic lead times (see the data limitation above); absolute delivery performance cannot be assessed.
- The delay threshold is a percentile, so some share of shipments is flagged by construction, and the 75th-percentile cutoff mainly flags Standard and Second Class orders.
- Factory assignment depends on the product-factory table in the project brief; actual fulfilment locations are not in the data.
- Many state-level routes have few orders, so rankings use a minimum of 10 orders and statistical confidence is limited for small routes.
- The data includes Canadian provinces, which appear in tables but not on the US map.
- Cost-time analysis is descriptive only; it does not show causation.

## Author

Taha S. Travadi | Unified Mentor Internship | 
