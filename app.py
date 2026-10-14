import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Nassau Candy - Shipping Route Efficiency", layout="wide")

# ----------------------------------------------------------------------
# Load data (produced in Step 6)
# ----------------------------------------------------------------------
@st.cache_data
def load_data():
    d = pd.read_csv("clean_shipments.csv", parse_dates=["Order Date", "Ship Date"])
    return d

df = load_data()

US_CODES = {
    'Alabama': 'AL', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA', 'Colorado': 'CO',
    'Connecticut': 'CT', 'Delaware': 'DE', 'District Of Columbia': 'DC', 'District of Columbia': 'DC',
    'Florida': 'FL', 'Georgia': 'GA', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS', 'Missouri': 'MO',
    'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH', 'New Jersey': 'NJ',
    'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH',
    'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI',
    'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY',
}

# ----------------------------------------------------------------------
# Sidebar filters
# ----------------------------------------------------------------------
st.sidebar.title("Filters")

min_d, max_d = df["Order Date"].min().date(), df["Order Date"].max().date()
date_range = st.sidebar.date_input("Order date range", value=(min_d, max_d),
                                   min_value=min_d, max_value=max_d)

regions = sorted(df["Region"].unique())
sel_regions = st.sidebar.multiselect("Region", regions, default=regions)

states_avail = sorted(df[df["Region"].isin(sel_regions)]["State/Province"].unique())
sel_states = st.sidebar.multiselect("State / Province (leave empty = all)", states_avail)

modes = sorted(df["Ship Mode"].unique())
sel_modes = st.sidebar.multiselect("Ship mode", modes, default=modes)

lt_min, lt_max = int(df["Lead Time"].min()), int(df["Lead Time"].max())
default_thr = int(df["Lead Time"].quantile(0.75))
threshold = st.sidebar.slider("Delay threshold (days)", lt_min, lt_max, default_thr)

min_orders = st.sidebar.number_input("Min orders for a reliable route", 1, 100, 10)

# ----------------------------------------------------------------------
# Apply filters
# ----------------------------------------------------------------------
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
else:
    start, end = pd.to_datetime(min_d), pd.to_datetime(max_d)

f = df[(df["Order Date"] >= start) & (df["Order Date"] <= end)
       & (df["Region"].isin(sel_regions)) & (df["Ship Mode"].isin(sel_modes))].copy()
if sel_states:
    f = f[f["State/Province"].isin(sel_states)]

if f.empty:
    st.warning("No shipments match the selected filters.")
    st.stop()

f["Delayed"] = f["Lead Time"] > threshold

# Year-adjusted lead time: each order's lead time minus the average for its own order year.
# This removes the order-year effect found in the data (2024 orders average ~1,094 days, 2025 ~1,479).
f["Order Year"] = f["Order Date"].dt.year
f["Adj Lead"] = f["Lead Time"] - f.groupby("Order Year")["Lead Time"].transform("mean")


def aggregate(data, col):
    r = data.groupby(col).agg(
        Shipments=("Row ID", "count"),
        Avg_Lead=("Lead Time", "mean"),
        Std_Lead=("Lead Time", "std"),
        Delay_Pct=("Delayed", "mean"),
        Total_Sales=("Sales", "sum"),
    ).reset_index()
    r["Delay_Pct"] *= 100
    r["Std_Lead"] = r["Std_Lead"].fillna(0)
    return r


def add_score(r):
    if len(r) > 1 and r["Avg_Lead"].max() > r["Avg_Lead"].min():
        r["Efficiency_Score"] = (1 - (r["Avg_Lead"] - r["Avg_Lead"].min()) /
                                 (r["Avg_Lead"].max() - r["Avg_Lead"].min())) * 100
    else:
        r["Efficiency_Score"] = 100.0
    return r


# ----------------------------------------------------------------------
# Header + KPIs
# ----------------------------------------------------------------------
st.title("Nassau Candy Distributor - Shipping Route Efficiency")
st.caption("Factory-to-customer route analytics. Lead time = Ship Date - Order Date.")

st.warning(
    "**Data limitation:** Lead times in this dataset are not realistic. Order dates fall in "
    "2024-2025 but ship dates fall in 2026-2030, giving lead times of roughly 900 to 1,640 days. "
    "The ship dates appear to be synthetic or shifted. Treat all results as **relative "
    "comparisons between routes**, not as real-world delivery times."
)
with st.expander("About the data and method"):
    st.markdown(
        "- **Lead time** = Ship Date - Order Date (days).\n"
        "- **Factory** is not in the raw data; it is mapped from Product Name using the project's "
        "product-factory table.\n"
        "- **Route** = Factory -> customer Region or State.\n"
        "- **Delay frequency** = share of shipments with lead time above the threshold slider "
        "(default = 75th percentile).\n"
        "- **Route Efficiency Score** = min-max normalized average lead time (100 = fastest route "
        "in the current selection, 0 = slowest). Routes with fewer than the minimum order count "
        "are excluded from rankings.\n"
        "- **Year-adjusted lead time** = an order's lead time minus the average for orders placed in the same "
        "year. It removes an order-year effect in the data (2025 orders are about 385 days slower than 2024 "
        "orders), so states are not penalised for simply having more 2025 orders.\n"
        "- Because of the unrealistic dates, ship mode results can look counter-intuitive "
        "(for example, Same Day is not faster than Standard Class)."
    )

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Shipments", f"{len(f):,}")
k2.metric("Avg lead time (days)", f"{f['Lead Time'].mean():,.1f}")
k3.metric("Lead time std dev", f"{f['Lead Time'].std():,.1f}")
k4.metric("Delay frequency", f"{f['Delayed'].mean() * 100:.1f}%")
k5.metric("Total sales", f"${f['Sales'].sum():,.0f}")

tab1, tab2, tab3, tab4 = st.tabs(["Route Efficiency Overview", "Geographic Shipping Map",
                                  "Ship Mode Comparison", "Route Drill-Down"])

# ----------------------------------------------------------------------
# Tab 1: Route Efficiency Overview
# ----------------------------------------------------------------------
with tab1:
    level = st.radio("Route level", ["Factory -> Region", "Factory -> State"], horizontal=True)
    col = "Route (Region)" if level == "Factory -> Region" else "Route (State)"
    routes = aggregate(f, col)
    routes = routes[routes["Shipments"] >= min_orders].copy()

    if routes.empty:
        st.info("No routes meet the minimum order count. Lower it in the sidebar.")
    else:
        routes = add_score(routes).sort_values("Efficiency_Score", ascending=False).reset_index(drop=True)
        routes.index = routes.index + 1

        n = min(10, len(routes))
        c1, c2 = st.columns(2)
        with c1:
            st.subheader(f"Top {n} most efficient routes")
            top = routes.head(n)
            fig = px.bar(top.iloc[::-1], x="Avg_Lead", y=col, orientation="h",
                         color_discrete_sequence=["seagreen"], hover_data=["Shipments", "Delay_Pct"])
            fig.update_xaxes(range=[routes["Avg_Lead"].min() * 0.95, routes["Avg_Lead"].max() * 1.02])
            st.plotly_chart(fig, use_container_width=True)
        with c2:
            st.subheader(f"Bottom {n} least efficient routes")
            bot = routes.tail(n)
            fig = px.bar(bot, x="Avg_Lead", y=col, orientation="h",
                         color_discrete_sequence=["firebrick"], hover_data=["Shipments", "Delay_Pct"])
            fig.update_xaxes(range=[routes["Avg_Lead"].min() * 0.95, routes["Avg_Lead"].max() * 1.02])
            st.plotly_chart(fig, use_container_width=True)

        st.subheader("Route performance leaderboard")
        st.dataframe(routes[[col, "Shipments", "Avg_Lead", "Std_Lead", "Delay_Pct", "Efficiency_Score"]]
                     .round(1), use_container_width=True)
        st.download_button("Download leaderboard (CSV)", routes.to_csv().encode("utf-8"),
                           "route_leaderboard.csv", "text/csv")

# ----------------------------------------------------------------------
# Tab 2: Geographic Shipping Map
# ----------------------------------------------------------------------
with tab2:
    sp = aggregate(f, "State/Province")
    sp = sp.merge(f.groupby("State/Province")["Adj Lead"].mean().rename("Year_Adj_Lead").reset_index(),
                  on="State/Province")
    sp["Code"] = sp["State/Province"].map(US_CODES)
    us_sp = sp.dropna(subset=["Code"])

    metric_choice = st.selectbox("Map metric", ["Avg_Lead", "Delay_Pct", "Shipments"])
    fig = px.choropleth(us_sp, locations="Code", locationmode="USA-states", scope="usa",
                        color=metric_choice, color_continuous_scale="RdYlGn_r",
                        hover_name="State/Province",
                        hover_data={"Shipments": True, "Avg_Lead": ":.1f", "Delay_Pct": ":.1f", "Code": False},
                        title=f"{metric_choice} by state (red = worse)")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Regional bottleneck view")
    rg = aggregate(f, "Region")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(rg.sort_values("Avg_Lead"), x="Region", y="Avg_Lead", color="Delay_Pct",
                     color_continuous_scale="RdYlGn_r", title="Avg lead time by region")
        fig.update_yaxes(range=[rg["Avg_Lead"].min() * 0.97, rg["Avg_Lead"].max() * 1.01])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        reliable = sp[sp["Shipments"] >= max(min_orders, 30)]
        if reliable.empty:
            st.info("Not enough volume per state for the bubble chart.")
        else:
            fig = px.scatter(reliable, x="Shipments", y="Avg_Lead", size="Shipments", color="Delay_Pct",
                             color_continuous_scale="RdYlGn_r", hover_name="State/Province",
                             title="Volume vs lead time (top-right = bottleneck)")
            fig.add_hline(y=f["Lead Time"].mean(), line_dash="dash")
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Congestion-prone states (high volume + slower + more delays)")
    st.caption("A state is flagged when its volume is at or above the median, its average lead time is above "
               "the overall average and its delay frequency is above the overall rate. "
               "**Year_Adj_Lead** is the state's lead time versus the same-year average (positive = slower). "
               "A flagged state is only a confirmed bottleneck if Year_Adj_Lead is clearly positive; "
               "otherwise its raw slowness is mostly explained by having more 2025 orders.")
    reliable = sp[sp["Shipments"] >= 30]
    if not reliable.empty:
        cong = reliable[(reliable["Shipments"] >= reliable["Shipments"].median())
                        & (reliable["Avg_Lead"] > f["Lead Time"].mean())
                        & (reliable["Delay_Pct"] > f["Delayed"].mean() * 100)].copy()
        cong["Confirmed after year adjustment"] = np.where(cong["Year_Adj_Lead"] > 20, "Yes", "No / weak")
        st.dataframe(cong.sort_values("Shipments", ascending=False)
                     [["State/Province", "Shipments", "Avg_Lead", "Delay_Pct", "Year_Adj_Lead",
                       "Confirmed after year adjustment"]].round(1),
                     use_container_width=True)

# ----------------------------------------------------------------------
# Tab 3: Ship Mode Comparison
# ----------------------------------------------------------------------
with tab3:
    mode = aggregate(f, "Ship Mode")
    extra = f.groupby("Ship Mode").agg(Avg_Cost=("Cost", "mean"),
                                       Profit=("Gross Profit", "sum"),
                                       Sales=("Sales", "sum"),
                                       Units=("Units", "sum"),
                                       Cost_Sum=("Cost", "sum")).reset_index()
    extra["Profit_Margin_%"] = extra["Profit"] / extra["Sales"] * 100
    extra["Cost_per_Unit"] = extra["Cost_Sum"] / extra["Units"]
    mode = mode.merge(extra[["Ship Mode", "Avg_Cost", "Profit_Margin_%", "Cost_per_Unit"]], on="Ship Mode")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.bar(mode, x="Ship Mode", y="Avg_Lead", color="Ship Mode", title="Avg lead time by ship mode")
        fig.update_yaxes(range=[mode["Avg_Lead"].min() * 0.97, mode["Avg_Lead"].max() * 1.01])
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        fig = px.box(f, x="Ship Mode", y="Lead Time", color="Ship Mode", title="Lead time spread")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(mode, x="Ship Mode", y="Delay_Pct", color="Ship Mode",
                     title=f"Delay frequency (> {threshold} days)")
        st.plotly_chart(fig, use_container_width=True)
    with c4:
        fig = px.scatter(mode, x="Avg_Lead", y="Cost_per_Unit", size="Shipments", color="Ship Mode",
                         title="Cost-time tradeoff (cost per unit vs lead time)")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Cost-time summary (descriptive)")
    st.dataframe(mode.round(2), use_container_width=True)

    f["Ship Category"] = np.where(f["Ship Mode"] == "Standard Class", "Standard", "Expedited")
    cat = f.groupby("Ship Category").agg(Shipments=("Row ID", "count"),
                                         Avg_Lead=("Lead Time", "mean"),
                                         Delay_Pct=("Delayed", "mean")).reset_index()
    cat["Delay_Pct"] *= 100
    st.subheader("Standard vs Expedited")
    st.dataframe(cat.round(2), use_container_width=True)

# ----------------------------------------------------------------------
# Tab 4: Route Drill-Down
# ----------------------------------------------------------------------
with tab4:
    state_options = sorted(f["State/Province"].unique())
    chosen = st.selectbox("Select a state / province", state_options)
    s = f[f["State/Province"] == chosen]

    d1, d2, d3, d4, d5 = st.columns(5)
    d1.metric("Shipments", f"{len(s):,}")
    d2.metric("Avg lead time", f"{s['Lead Time'].mean():,.1f}")
    d3.metric("Std dev", f"{s['Lead Time'].std():,.1f}" if len(s) > 1 else "n/a")
    d4.metric("Delay frequency", f"{s['Delayed'].mean() * 100:.1f}%")
    d5.metric("Year-adjusted lead (days)", f"{s['Adj Lead'].mean():+,.1f}")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Routes into this state")
        sr = aggregate(s, "Factory")
        st.dataframe(sr.round(1), use_container_width=True)
    with c2:
        st.subheader("Avg lead time by ship mode")
        sm = aggregate(s, "Ship Mode")
        fig = px.bar(sm, x="Ship Mode", y="Avg_Lead", color="Ship Mode")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Lead time distribution")
    fig = px.histogram(s, x="Lead Time", nbins=30, color="Factory")
    fig.add_vline(x=threshold, line_dash="dash", annotation_text="threshold")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Order-level shipment timelines")
    n_show = st.slider("Number of orders to show", 5, 50, 20)
    order_view = s.sort_values("Lead Time", ascending=False).head(n_show).copy()
    order_view["Label"] = order_view["Order ID"].astype(str) + " | " + order_view["Factory"]
    fig = px.timeline(order_view, x_start="Order Date", x_end="Ship Date", y="Label",
                      color="Ship Mode", hover_data=["Lead Time", "Product Name"])
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Showing the slowest orders first. Each bar runs from order date to ship date.")

    st.dataframe(s[["Order ID", "Order Date", "Ship Date", "Lead Time", "Ship Mode", "Factory",
                    "Product Name", "City", "Sales", "Units"]].sort_values("Lead Time", ascending=False),
                 use_container_width=True)
