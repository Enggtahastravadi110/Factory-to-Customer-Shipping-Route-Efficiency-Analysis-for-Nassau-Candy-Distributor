# Factory-to-Customer Shipping Route Efficiency Analysis
### Nassau Candy Distributor | Unified Mentor Internship, Project 2

**Author:** Taha S. Travadi
**Live dashboard:** [https://factorytocustomershippingrouteefficiency.streamlit.app/](https://factorytocustomershippingrouteefficiency.streamlit.app/)

A data analysis project and interactive Streamlit dashboard that measures how efficiently Nassau Candy Distributor ships products from its factories to customers across the US and Canada, at route, region, state and ship-mode level.

**Deliverables:** research paper, Streamlit dashboard, executive summary (all in this repository).

---

## Important: Data Limitation

> **The shipping lead times in this dataset are not realistic.**
>
> Order dates run from **January 2024 to December 2025**, but ship dates run from **June 2026 to June 2030**. This gives lead times of roughly **904 to 1,642 days** (mean about 1,320 days). No lead time is negative and no dates are missing, but the ship dates appear to be synthetic or shifted.
>
> Symptoms of this problem:
> - **Same Day shipping (average 1,333 days) is not faster than Standard Class (average 1,314 days).**
> - **Lead time depends on the year the order was placed.** Orders placed in 2024 average about 1,094 days and orders placed in 2025 average about 1,479 days (a gap of about 385 days). Lead times form three separate clusters instead of a smooth distribution. States with more 2025 orders therefore look slower for reasons unrelated to geography.
>
> **How the project handles it:** raw values are kept, the delay threshold is a percentile (75th percentile = 1,638 days), a **year-adjusted lead time** is used as a robustness check, and every conclusion is framed as a **relative comparison between routes**. Nothing in this project should be read as a real-world delivery time.

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Business Problem](#business-problem)
3. [Dataset](#dataset)
4. [Methodology](#methodology)
5. [KPIs](#kpis)
6. [Research Paper Summary](#research-paper-summary)
7. [Dashboard](#dashboard)
8. [Project Structure](#project-structure)
9. [Run Locally](#run-locally)
10. [Limitations](#limitations)
11. [Author](#author)

---

## Executive Summary

**Purpose.** Nassau Candy ships from five factories to customers in 59 states and provinces but has lacked a clear view of which delivery routes work well. This project analysed 10,194 order lines (orders from January 2024 to December 2025) to rank routes, find geographic problem areas and compare ship modes.

**Key findings** (all relative, see the data limitation above):

1. **Problems are local, not regional.** The four regions differ by only about 12 days, and the two main factories perform almost identically. States differ by about 217 days (fastest vs slowest, states with 30+ orders).
2. **Tennessee and Indiana are the clearest bottlenecks.** Both have high volume (183 and 149 orders), about 31% of shipments flagged as delayed, and lead times well above the same-year average (about +45 and +40 days). They are slow from both large factories.
3. **Virginia and Oregon are consistently strong** under every measure used, as are smaller states such as Mississippi, Oklahoma and Arkansas. Virginia is fast from both large factories.
4. **The largest markets are not the problem.** California (2,001 orders) and Texas (985 orders) perform close to average.
5. **Premium shipping showed no speed advantage.** Same Day averaged 1,333 days against 1,314 for Standard Class, with nearly identical cost per unit and margin across modes.
6. **Order timing distorts raw results.** After correcting for it, Washington, New Jersey and several other states that looked slow are not confirmed as problem areas.

**Performance snapshot**

| Measure | Value |
|---|---|
| Order lines analysed | 10,194 |
| Average lead time (relative measure, days) | 1,320.8 |
| Share of shipments flagged as delayed | 21.1% |
| Routes reliable enough to rank (state level) | 96 of 196 |
| Overall gross profit margin | 65.9% |
| Gap between best and worst region | about 12 days |
| Gap between best and worst state (30+ orders) | about 217 days (166 after year adjustment) |

**Recommended actions, in priority order**

1. **Fix the shipping date data.** Confirm how ship dates are recorded and capture actual ship and delivery dates. Re-check every decision against real dates.
2. **Review Tennessee and Indiana first.** Examine carrier handoffs and local delivery arrangements, since both main factories are slow into these states.
3. **Monitor a watch list monthly:** Maryland, Massachusetts, Kentucky and Minnesota (slow after correction); New Mexico and Iowa (slow but low volume).
4. **Copy what works.** Compare practices for Virginia and Oregon with the slow states.
5. **Re-examine premium shipping.** If real dates confirm faster modes are not faster, review what customers are promised and charged.
6. **Use the dashboard routinely** to monitor routes, states and ship modes.

The full one-to-two page version is in `reports/Nassau_Candy_Executive_Summary.docx`.

---

## Business Problem

Nassau Candy ships from several factories to customers nationwide, but logistics decisions are made without route-level efficiency intelligence. The company lacks clarity on:

- Which factory-to-customer routes are consistently efficient
- Which routes experience frequent delays
- How performance varies by region, state and ship mode
- Where geographic bottlenecks exist

## Dataset

`Nassau_Candy_Distributor.csv` has 10,194 order lines and 18 columns (order and ship dates, ship mode, customer geography, product, sales, units, gross profit, cost).

- No missing values and no duplicate rows
- 4 ship modes, 4 regions, 15 products, 59 states and provinces (9,994 US lines, 200 Canadian lines)
- Chocolate is 96.6% of order lines; total sales are $141,783.63
- **Factory is not in the raw data.** It was derived by mapping each product to its factory using the product-factory table in the project brief. Factory coordinates also come from the brief.

| Factory | Orders |
|---|---|
| Lot's O' Nuts | 5,692 |
| Wicked Choccy's | 4,152 |
| Secret Factory | 217 |
| The Other Factory | 100 |
| Sugar Shack | 33 |

## Methodology

1. **Data cleaning and validation:** parse `DD-MM-YYYY` dates, remove invalid or negative lead times (none found), standardize text and geographic fields, remove duplicates.
2. **Feature engineering:** lead time (Ship Date minus Order Date), product-to-factory mapping, factory coordinates, route labels (Factory to Region, Factory to State), Standard vs Expedited grouping, profit margin, cost per unit.
3. **Route aggregation:** shipments, average, median and standard deviation of lead time, and delay frequency per route (20 region routes, 196 state routes).
4. **Efficiency benchmarking:** Route Efficiency Score (0 to 100, min-max normalized average lead time), Top 10 and Bottom 10 routes. Routes with fewer than **10 orders** are excluded from rankings.
5. **Geographic bottleneck analysis:** region and state comparison (states with 30+ orders), congestion-prone states (high volume, slower than average, more delays than average), US heatmap.
6. **Ship mode analysis:** lead time, spread, delay frequency and descriptive cost-time tradeoff.
7. **Robustness check:** year-adjusted lead time (each order's lead time minus the average for its own order year) to remove the order-year effect.

## KPIs

| KPI | Definition |
|---|---|
| Shipping Lead Time | Ship Date minus Order Date |
| Average Lead Time | Mean lead time per route |
| Route Volume | Number of orders per route |
| Lead Time Variability | Standard deviation of lead time per route |
| Delay Frequency | % of shipments above the threshold (75th percentile, 1,638 days) |
| Route Efficiency Score | Normalized lead-time performance (100 = fastest, 0 = slowest) |

## Research Paper Summary

The full paper (`reports/Nassau_Candy_Research_Paper.docx`, about 15 pages with 8 tables and 7 charts) is organised as follows.

| Section | What it covers |
|---|---|
| Abstract and Introduction | Problem, objectives, data limitation note |
| Data and Methodology | Dataset, cleaning, feature engineering, route definition, KPIs |
| Data Quality and Limitations | Unrealistic lead times, three lead-time clusters, order-year effect |
| Exploratory Data Analysis | Order size, lead time percentiles, near-identical averages across broad groups |
| Route Efficiency Results | Region-level and state-level rankings, Top 10 and Bottom 10 tables |
| Geographic Bottleneck Analysis | Regions, states, congestion-prone states |
| Ship Mode Performance | Four modes and Standard vs Expedited, cost-time view |
| Robustness Check | Year-adjusted lead time and what changes |
| Recommendations | Seven prioritised actions |
| Limitations and Future Work | Data caveats, distance-based and carrier analysis as next steps |

**Main results**

- **Regions:** Gulf 1,311.4, Pacific 1,322.2, Atlantic 1,322.7, Interior 1,323.1 average days; delay frequency 20.5% to 21.5%.
- **Routes (10+ orders):** fastest state route is Wicked Choccy's to Nevada (about 1,182 days, 12 orders); slowest is Wicked Choccy's to New Mexico (about 1,489 days, 17 orders). Routes with solid volume that stand out: Virginia (fast), Tennessee and Indiana (slow).
- **Congestion-prone states:** eight states qualify on raw numbers (New York, Pennsylvania, Washington, Illinois, Georgia, Tennessee, Indiana, New Jersey). After year adjustment, only **Tennessee (+45.3 days)** and **Indiana (+39.7 days)** remain clearly slower. Washington (+10.5) and Pennsylvania (+10.7) are mildly slower, New York, Illinois and Georgia are near average, and New Jersey is faster (-27.8).
- **Slow after adjustment:** Maryland (+35.7), Minnesota (+42.7), Massachusetts (+34.8), Kentucky (+32.5); New Mexico (+77.6) and Iowa (+42.2) are slow but low volume.
- **Consistently fast:** Virginia (-43.4, 224 orders) and Oregon (-27.9, 124 orders) at meaningful volume; strongest adjusted advantages are in smaller states: Mississippi (-88.6, 53 orders), Oklahoma (-78.1, 66 orders), Arkansas (-58.2, 60 orders); also Nevada (-25.0, 39 orders).
- **Ship modes:** average lead time Standard Class 1,314.3, Second Class 1,323.8, Same Day 1,333.4, First Class 1,338.3 days. Cost per unit 1.23 to 1.26 and margin 65.7% to 66.1%. Delay percentages are largely a threshold artifact (only Standard and Second Class orders exceed 1,638 days).

## Dashboard

The Streamlit app (`app.py`) has four modules:

| Module | Contents |
|---|---|
| Route Efficiency Overview | Top/Bottom 10 routes, route leaderboard, CSV download |
| Geographic Shipping Map | US heatmap, regional bottleneck view, congestion-prone states with a year-adjusted check |
| Ship Mode Comparison | Lead time, spread, delay %, cost-time tradeoff, Standard vs Expedited |
| Route Drill-Down | State KPIs including year-adjusted lead time, factory routes, distribution, order-level shipment timelines |

**Filters:** order date range, region, state/province, ship mode, delay-threshold slider and minimum orders per route.

The dashboard shows the data limitation as a warning banner at the top, plus an "About the data and method" section that explains each measure.

## Project Structure

```
nassau-candy-dashboard/
├── app.py                                   # Streamlit dashboard
├── requirements.txt                         # Python dependencies
├── README.md
├── data/
│  ├── clean_shipments.csv                   # Cleaned data with engineered features
│  ├── state_routes.csv
│  ├── factory_kpis.csv                   
│  ├── region_routes.csv
│  ├── overall_kpis.csv
│  └── state_performance.csv                  
├── reports/
│   ├── Nassau_Candy_Research_Paper.pdf      # Full research paper
│   └── Nassau_Candy_Executive_Summary.pdf   # Executive summary
└── Analysis.ipynb                           # Notebook with the full analysis (optional)
```

## Run Locally

```bash
pip install -r requirements.txt
python -m streamlit run app.py
```

Then open `http://localhost:8501`.

## Limitations

- Unrealistic lead times that depend on order year; only relative conclusions are supported.
- The delay threshold is a percentile, so some share of shipments is flagged by construction, mostly 2025 orders and the slower modes.
- Factory assignment depends on the product-factory table in the project brief; actual fulfilment locations are not in the data.
- Many state-level routes have few orders, so rankings use a minimum of 10 orders (30 for state analysis) and carry uncertainty for small routes.
- Canadian provinces appear in tables but not on the US map.
- The cost-time analysis is descriptive only and does not show causation.
- Distance between factory and customer was not modelled; this is a natural next step along with a carrier dimension once real data is available.

## Tech Stack

Python, pandas, NumPy, Plotly, Streamlit, Jupyter, Matplotlib.

## Author

**Taha S. Travadi** | Unified Mentor Internship | Linkedin : https://www.linkedin.com/in/taha-travadi-cte-gecbvn-ce-b92977297 | Email : ttravadi540@gmail.com
