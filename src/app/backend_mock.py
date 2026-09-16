"""
backend_mock.py — Fuel & Convenience Retail Marketing Analytics
Hardcoded mock data for local development (USE_MOCK_BACKEND=true).
"""
import pandas as pd
import numpy as np
from datetime import date, timedelta

np.random.seed(42)

TODAY      = date.today()
N_DAYS     = 90
START_DATE = TODAY - timedelta(days=N_DAYS - 1)

# ── Sites ──────────────────────────────────────────────────────────────────
_SITES = [
    # Texas (16 sites)
    ("S001","QuickFuel Houston Galleria","South","TX","Houston","urban",29.74,-95.46),
    ("S002","QuickFuel Houston Heights","South","TX","Houston","urban",29.80,-95.40),
    ("S003","QuickFuel Dallas Uptown","South","TX","Dallas","urban",32.80,-96.80),
    ("S004","QuickFuel Dallas Plano","South","TX","Dallas","suburban",33.02,-96.70),
    ("S005","QuickFuel Austin Downtown","South","TX","Austin","urban",30.27,-97.74),
    ("S006","QuickFuel Austin Cedar Park","South","TX","Austin","suburban",30.55,-97.82),
    ("S007","QuickFuel San Antonio Alamo","South","TX","San Antonio","urban",29.42,-98.50),
    ("S008","QuickFuel San Antonio Loop","South","TX","San Antonio","suburban",29.47,-98.42),
    ("S009","QuickFuel Fort Worth","South","TX","Fort Worth","suburban",32.75,-97.33),
    ("S010","QuickFuel El Paso","South","TX","El Paso","urban",31.76,-106.49),
    ("S011","QuickFuel Lubbock","South","TX","Lubbock","rural",33.58,-101.86),
    ("S012","QuickFuel Amarillo","South","TX","Amarillo","rural",35.22,-101.83),
    ("S013","QuickFuel Waco","South","TX","Waco","rural",31.55,-97.15),
    ("S014","QuickFuel Corpus Christi","South","TX","Corpus Christi","urban",27.80,-97.40),
    ("S015","QuickFuel McAllen","South","TX","McAllen","urban",26.20,-98.23),
    ("S016","QuickFuel Midland","South","TX","Midland","urban",31.99,-102.08),
    # South non-TX (4 sites)
    ("S017","QuickFuel Oklahoma City","South","OK","Oklahoma City","urban",35.47,-97.52),
    ("S018","QuickFuel New Orleans","South","LA","New Orleans","urban",29.95,-90.07),
    ("S019","QuickFuel Tulsa","South","OK","Tulsa","suburban",36.13,-95.93),
    ("S020","QuickFuel Baton Rouge","South","LA","Baton Rouge","suburban",30.45,-91.19),
    # Southeast (5 sites)
    ("S021","QuickFuel Miami","Southeast","FL","Miami","urban",25.78,-80.21),
    ("S022","QuickFuel Tampa","Southeast","FL","Tampa","suburban",27.97,-82.47),
    ("S023","QuickFuel Orlando","Southeast","FL","Orlando","suburban",28.54,-81.38),
    ("S024","QuickFuel Atlanta","Southeast","GA","Atlanta","urban",33.74,-84.39),
    ("S025","QuickFuel Nashville","Southeast","TN","Nashville","urban",36.16,-86.78),
    # Midwest (5 sites)
    ("S026","QuickFuel Chicago","Midwest","IL","Chicago","urban",41.88,-87.63),
    ("S027","QuickFuel Columbus","Midwest","OH","Columbus","suburban",39.96,-82.99),
    ("S028","QuickFuel Indianapolis","Midwest","IN","Indianapolis","suburban",39.77,-86.16),
    ("S029","QuickFuel Detroit","Midwest","MI","Detroit","urban",42.33,-83.05),
    ("S030","QuickFuel Milwaukee","Midwest","WI","Milwaukee","urban",43.04,-87.91),
    # West (5 sites)
    ("S031","QuickFuel Los Angeles","West","CA","Los Angeles","urban",34.05,-118.24),
    ("S032","QuickFuel San Francisco","West","CA","San Francisco","urban",37.77,-122.42),
    ("S033","QuickFuel Phoenix","West","AZ","Phoenix","urban",33.45,-112.07),
    ("S034","QuickFuel Denver","West","CO","Denver","urban",39.74,-104.99),
    ("S035","QuickFuel Seattle","West","WA","Seattle","urban",47.61,-122.33),
    # Northeast (5 sites)
    ("S036","QuickFuel New York","Northeast","NY","New York","urban",40.71,-74.00),
    ("S037","QuickFuel Philadelphia","Northeast","PA","Philadelphia","urban",39.95,-75.16),
    ("S038","QuickFuel Boston","Northeast","MA","Boston","urban",42.36,-71.06),
    ("S039","QuickFuel Newark","Northeast","NJ","Newark","urban",40.73,-74.17),
    ("S040","QuickFuel Pittsburgh","Northeast","PA","Pittsburgh","urban",40.44,-80.00),
]

SITES_DF = pd.DataFrame(_SITES, columns=[
    "site_id","name","region","state","city","site_type","lat","lon"
])

# ── Campaigns ──────────────────────────────────────────────────────────────
_CAMP_START = {
    "C001": TODAY - timedelta(days=68),
    "C002": TODAY - timedelta(days=24),
    "C003": TODAY - timedelta(days=99),
    "C004": TODAY - timedelta(days=38),
    "C005": TODAY - timedelta(days=180),
    "C006": TODAY - timedelta(days=150),
    "C007": TODAY - timedelta(days=274),
    "C008": TODAY - timedelta(days=350),
}
_CAMP_END = {
    "C001": TODAY + timedelta(days=53),
    "C002": TODAY + timedelta(days=66),
    "C003": TODAY + timedelta(days=22),
    "C004": TODAY + timedelta(days=53),
    "C005": TODAY - timedelta(days=121),
    "C006": TODAY - timedelta(days=76),
    "C007": TODAY - timedelta(days=183),
    "C008": TODAY - timedelta(days=274),
}

_CAMPAIGNS = [
    #  id       name                      region       state   channels                              status     uplift  incr_rev  basket_inc  part_rate
    ("C001","Fill & Refuel",             "South",      "all",  "In-store discount, Fuel loyalty, SMS","Active",  12.4,   8.2,      0.94,       0.23),
    ("C002","Texas Summer Drive",        "South",      "TX",   "Digital, Email, POS",                 "Active",   8.7,   5.4,      0.71,       0.31),
    ("C003","Urban Fresh",               "all",        "urban","Social, In-store, Display",            "Active",   6.2,   3.9,      0.52,       0.19),
    ("C004","Midwest Value Pack",        "Midwest",    "all",  "Coupon, Email, POS",                  "Active",   4.8,   3.1,      0.41,       0.27),
    ("C005","Holiday Fuel Rewards",      "all",        "all",  "Email, App, SMS",                     "Historic", 15.3,  10.2,     1.24,       0.34),
    ("C006","Spring Snack Attack",       "Southeast",  "all",  "Social, POS, Coupon",                 "Historic",  9.1,   6.1,     0.72,       0.22),
    ("C007","Coffee Morning Rush",       "Northeast",  "urban","In-store, Digital, App",              "Historic",  7.4,   4.8,     0.58,       0.28),
    ("C008","Rural Road Trip",           "all",        "rural","Billboard, Radio, SMS",               "Historic",  5.2,   3.3,     0.38,       0.18),
]

CAMPAIGNS_DF = pd.DataFrame(_CAMPAIGNS, columns=[
    "campaign_id","name","target_region","target_state","channels","status",
    "campaign_uplift_pct","incremental_revenue_m","basket_size_increase","participation_rate",
])
CAMPAIGNS_DF["start_date"] = CAMPAIGNS_DF["campaign_id"].map(_CAMP_START)
CAMPAIGNS_DF["end_date"]   = CAMPAIGNS_DF["campaign_id"].map(_CAMP_END)

# ── Daily Sales Generation ──────────────────────────────────────────────────
def _gen_sales():
    rng = np.random.default_rng(42)
    base_rev_map = {"urban": 3200, "suburban": 2400, "rural": 1600}
    base_gal_map = {"urban": 1800, "suburban": 2400, "rural": 3200}
    records = []
    for _, site in SITES_DF.iterrows():
        base_r = base_rev_map.get(site.site_type, 2400)
        base_g = base_gal_map.get(site.site_type, 2000)
        for d in range(N_DAYS):
            dt = START_DATE + timedelta(days=d)
            wknd  = 1.25 if dt.weekday() >= 5 else 1.0
            trend = 1 + (d / N_DAYS) * 0.10 if site.state == "TX" else 1.0
            trend *= 0.97 if site.region == "Midwest" else 1.0
            rev = base_r * wknd * trend * (1 + rng.normal(0, 0.08))
            gal = base_g * wknd * (1 + rng.normal(0, 0.07))
            rev = max(rev, 100)
            gal = max(gal, 100)
            txns = max(int(rev / rng.uniform(7, 10)), 1)
            records.append({
                "site_id":          site.site_id,
                "date":             dt,
                "fuel_gallons":     round(gal),
                "instore_revenue":  round(rev, 2),
                "basket_size":      round(rev / txns, 2),
                "transaction_count":txns,
                "margin":           round(rev * rng.uniform(0.28, 0.36), 2),
            })
    return pd.DataFrame(records)

SALES_DF = _gen_sales()

# ── State lat/lon ──────────────────────────────────────────────────────────
STATE_COORDS = {
    "TX":(31.0,-99.0),"OK":(35.5,-96.9),"LA":(30.9,-91.8),
    "FL":(27.9,-81.7),"GA":(33.2,-83.5),"TN":(35.7,-86.3),
    "IL":(40.3,-89.0),"OH":(40.3,-82.8),"IN":(39.9,-86.3),
    "MI":(43.3,-84.5),"WI":(44.5,-89.6),
    "CA":(36.8,-119.4),"AZ":(33.7,-111.4),"CO":(38.9,-105.5),"WA":(47.5,-121.0),
    "NY":(42.9,-75.5),"PA":(41.2,-77.2),"MA":(42.1,-71.6),"NJ":(40.1,-74.5),
}

VS_PRIOR = {
    "TX": 12.1,"OK": 4.2,"LA": 3.7,
    "FL":  6.8,"GA": 5.4,"TN": 2.9,
    "IL": -1.3,"OH":-0.4,"IN": 1.2,"MI":-2.1,"WI": 0.8,
    "CA":  7.8,"AZ": 9.3,"CO": 6.1,"WA": 8.4,
    "NY":  3.3,"PA": 2.1,"MA": 4.7,"NJ": 1.8,
}

# ── Public functions ────────────────────────────────────────────────────────

def get_sites() -> pd.DataFrame:
    return SITES_DF.copy()


def get_data_catalog() -> pd.DataFrame:
    return pd.DataFrame([
        {"table_name": name, "table_type": "MANAGED", "comment": "Shell retail analytics source"}
        for name in sorted([
            "bundle_definition", "campaigns", "customer_preference", "customer_profile",
            "daily_sales", "loyalty_events_raw", "offers", "product_master", "sites", "store_master",
        ])
    ])


def get_data_freshness() -> pd.DataFrame:
    now = pd.Timestamp.now().floor("min")
    return pd.DataFrame([
        {"table_name": name, "last_altered": now - pd.Timedelta(minutes=index * 17)}
        for index, name in enumerate(["daily_sales", "customer_profile", "campaigns", "sites", "offers"])
    ])


def get_kpis() -> dict:
    total_rev = SALES_DF.instore_revenue.sum()
    total_gal = SALES_DF.fuel_gallons.sum()
    basket    = SALES_DF.basket_size.mean()
    return {
        "total_revenue_m":      round(total_rev / 1e6, 2),
        "basket_size":          round(basket, 2),
        "basket_vs_prior":      3.2,
        "repeat_visits":        67.3,
        "repeat_vs_prior":      2.4,
        "rev_vs_prior":         5.8,
        "campaign_uplift":      8.7,
        "fuel_gallons_m":       round(total_gal / 1e6, 1),
        "fuel_vs_prior":       -0.4,
        "active_campaigns":     4,
        "total_sites":          len(SITES_DF),
        # Loyalty CY YTM vs PY YTM (Jan–May 2026 vs Jan–May 2025)
        "loyalty_activations_k": 497,
        "loyalty_act_yoy":       57.6,
        "loyalty_reg_k":         774,
        "loyalty_reg_yoy":       64.5,
    }


def get_regional_summary() -> pd.DataFrame:
    merged = SALES_DF.merge(SITES_DF[["site_id","region","state"]], on="site_id")
    agg = merged.groupby(["region","state"]).agg(
        revenue=("instore_revenue","sum"),
        fuel_gallons=("fuel_gallons","sum"),
        site_count=("site_id","nunique"),
        avg_basket=("basket_size","mean"),
    ).reset_index()
    agg["revenue_vs_prior"] = agg["state"].map(VS_PRIOR).fillna(0.0)
    agg["lat"] = agg["state"].map({k: v[0] for k, v in STATE_COORDS.items()})
    agg["lon"] = agg["state"].map({k: v[1] for k, v in STATE_COORDS.items()})
    agg = agg.dropna(subset=["lat", "lon"])
    return agg


def get_site_type_breakdown() -> pd.DataFrame:
    merged = SALES_DF.merge(SITES_DF[["site_id","site_type"]], on="site_id")
    return merged.groupby("site_type").agg(
        revenue=("instore_revenue","sum"),
        site_count=("site_id","nunique"),
        avg_basket=("basket_size","mean"),
        fuel_gallons=("fuel_gallons","sum"),
    ).reset_index()


def get_top_bottom_stores(n=5):
    rng = np.random.default_rng(99)
    merged = SALES_DF.merge(SITES_DF[["site_id","name","region","state","city"]], on="site_id")
    by_site = merged.groupby(["site_id","name","region","state","city"]).agg(
        revenue=("instore_revenue","sum"),
        avg_basket=("basket_size","mean"),
    ).reset_index()
    by_site["revenue_vs_prior"] = rng.uniform(-5, 20, len(by_site)).round(1)
    top    = by_site.nlargest(n, "revenue").copy()
    bottom = by_site.nsmallest(n, "revenue").copy()
    for df in (top, bottom):
        df["Revenue (90d)"] = df["revenue"].apply(lambda x: f"${x/1000:.1f}K")
        df["Avg Basket"]    = df["avg_basket"].apply(lambda x: f"${x:.2f}")
        df["vs Prior"]      = df["revenue_vs_prior"].apply(lambda x: f"{x:+.1f}%")
        df.rename(columns={"name":"Store","city":"City","state":"State"}, inplace=True)
    cols = ["Store","City","State","Revenue (90d)","Avg Basket","vs Prior"]
    return top[cols].reset_index(drop=True), bottom[cols].reset_index(drop=True)


def get_active_campaigns() -> pd.DataFrame:
    return CAMPAIGNS_DF[CAMPAIGNS_DF.status == "Active"].copy()


def get_historic_campaigns() -> pd.DataFrame:
    return CAMPAIGNS_DF[CAMPAIGNS_DF.status == "Historic"].copy()


def get_all_campaigns() -> pd.DataFrame:
    return CAMPAIGNS_DF.copy()


def get_campaign_kpis(campaign_ids=None) -> dict:
    df = CAMPAIGNS_DF.copy()
    if campaign_ids:
        df = df[df.campaign_id.isin(campaign_ids)]
    if df.empty:
        df = CAMPAIGNS_DF[CAMPAIGNS_DF.status == "Active"]
    return {
        "avg_uplift":         round(df.campaign_uplift_pct.mean(), 1),
        "total_incr_rev_m":   round(df.incremental_revenue_m.sum(), 1),
        "avg_basket_increase":round(df.basket_size_increase.mean(), 2),
        "avg_participation":  round(df.participation_rate.mean(), 2),
        "campaign_count":     len(df),
    }


def get_campaign_comparison(campaign_ids) -> pd.DataFrame:
    return CAMPAIGNS_DF[CAMPAIGNS_DF.campaign_id.isin(campaign_ids)][
        ["campaign_id","name","campaign_uplift_pct","incremental_revenue_m",
         "basket_size_increase","participation_rate","channels","target_region"]
    ].copy()


def get_campaign_detail(campaign_id: str) -> dict:
    row = CAMPAIGNS_DF[CAMPAIGNS_DF.campaign_id == campaign_id].iloc[0]
    rng = np.random.default_rng(hash(campaign_id) % (2**31))

    target = SITES_DF.copy()
    if row.target_region not in ("all", None):
        target = target[target.region == row.target_region]
    if row.target_state not in ("all", None, "urban", "rural", "suburban"):
        target = target[target.state == row.target_state]
    elif row.target_state in ("urban", "rural", "suburban"):
        target = target[target.site_type == row.target_state]

    n_sites     = max(len(target), 1)
    n_customers = int(n_sites * rng.uniform(820, 1200))

    reg_part = target.groupby("region").size().reset_index(name="Stores Participating")
    reg_part["Participation Rate"] = rng.uniform(0.18, 0.38, len(reg_part)).round(2)
    reg_part.columns = ["Region","Stores Participating","Participation Rate"]

    days         = 30
    start_d      = row.start_date if isinstance(row.start_date, date) else date.fromisoformat(str(row.start_date))
    date_labels  = [(start_d + timedelta(days=i)).isoformat() for i in range(days)]
    base_daily   = row.incremental_revenue_m * 1000 / days
    forecast     = [round(base_daily * (1 + rng.normal(0, 0.05)), 1) for _ in range(days)]
    actual       = [round(f * rng.uniform(0.88, 1.18), 1) for f in forecast]

    basket_comp  = pd.DataFrame([
        ("Fuel",       45.2), ("Beverages", 18.4), ("Snacks",   12.1),
        ("Tobacco",     9.3), ("Food",       7.8),  ("Other",    7.2),
    ], columns=["Category", "Share %"])

    return {
        "campaign":             row.to_dict(),
        "n_customers":          n_customers,
        "n_sites":              n_sites,
        "regional_participation": reg_part,
        "revenue_dates":        date_labels,
        "revenue_forecast":     forecast,
        "revenue_actual":       actual,
        "basket_composition":   basket_comp,
        "avg_visits_per_cust":  round(rng.uniform(3.2, 5.8), 1),
        "basket_size_pre":      7.85,
        "basket_size_during":   round(7.85 + row.basket_size_increase, 2),
        "basket_pct_increase":  round(row.basket_size_increase / 7.85 * 100, 1),
        "cross_category_rate":  round(rng.uniform(0.31, 0.52), 2),
        "insights": [
            f"Houston sites outperformed forecast by 18% — expand {row['name']} to similar high-traffic urban corridors.",
            f"Rural participation {12}pp below urban average — consider adjusted incentive tier for low-density sites.",
            f"Basket uplift strongest 7–9am. Extend morning offer window to capture cross-category purchases.",
        ],
    }


def get_texas_detail() -> dict:
    rng    = np.random.default_rng(77)
    tx     = SALES_DF.merge(SITES_DF[SITES_DF.state == "TX"][["site_id","city"]], on="site_id")

    city_rev = tx.groupby("city").agg(
        revenue=("instore_revenue","sum"),
        fuel_gallons=("fuel_gallons","sum"),
        avg_basket=("basket_size","mean"),
        margin=("margin","sum"),
    ).reset_index()
    city_rev["revenue_vs_prior"] = rng.uniform(-5, 16, len(city_rev)).round(1)
    city_rev["margin_pct"] = (city_rev.margin / city_rev.revenue * 100).round(1)

    tx["week_num"] = tx["date"].apply(lambda d: d.isocalendar()[1])
    weekly = tx.groupby("week_num").agg(
        revenue=("instore_revenue","sum"),
        margin=("margin","sum"),
    ).reset_index().sort_values("week_num")
    weekly["margin_pct"] = (weekly.margin / weekly.revenue * 100).round(1)
    weekly["week_label"] = weekly["week_num"].apply(lambda w: f"W{w}")

    top_products = pd.DataFrame([
        ("Beverages","$142K",18.4,"↑ 4.2%"),
        ("Snacks",   "$98K", 12.6,"↑ 6.1%"),
        ("Tobacco",  "$72K",  9.3,"↓ 2.1%"),
        ("Food",     "$61K",  7.8,"↑ 11.3%"),
        ("Automotive","$34K",  4.4,"↑ 2.8%"),
    ], columns=["Product","Revenue","Share %","vs Prior"])

    campaign_start = TODAY - timedelta(days=24)
    pre_rev  = tx[tx.date < campaign_start].instore_revenue.mean()
    post_rev = tx[tx.date >= campaign_start].instore_revenue.mean()

    return {
        "city_revenue":         city_rev,
        "weekly_margin":        weekly,
        "top_products":         top_products,
        "avg_basket":           round(tx.basket_size.mean(), 2),
        "avg_txns_per_site_day":round(tx.groupby(["site_id","date"]).transaction_count.sum().mean(), 0),
        "revenue_total_m":      round(tx.instore_revenue.sum() / 1e6, 2),
        "fuel_gallons_m":       round(tx.fuel_gallons.sum() / 1e6, 1),
        "margin_pct":           round(tx.margin.sum() / tx.instore_revenue.sum() * 100, 1),
        "rev_vs_prior":         12.1,
        "fuel_vs_prior":        -0.4,
        "pre_campaign_daily_rev":  round(pre_rev, 2),
        "post_campaign_daily_rev": round(post_rev, 2),
        "campaign_lift":        round((post_rev / pre_rev - 1) * 100, 1) if pre_rev > 0 else 0.0,
        "anomalies": [
            (
                "Fuel flat, in-store surging",
                "Fuel gallons -0.4% while in-store revenue +12.1% — customers fuelling elsewhere but buying snacks/beverages here. Strong loyalty program impact on basket.",
                "Accelerate cross-sell prompts at pump to recover fuel volume.",
            ),
            (
                "El Paso outperforming by 22%",
                "QuickFuel El Paso is 22% above TX average since Fill & Refuel launch. High-traffic highway, 24hr operation, dual-language staff.",
                "Replicate El Paso model at Midland and Waco (similar highway traffic profile).",
            ),
            (
                "Afternoon dip 2–5pm across Texas",
                "Texas sites see 31% revenue decline 2–5pm vs morning peak. Competitors running afternoon promotions in this window.",
                "Test afternoon happy hour: 20% off hot food 2–5pm across top 20 TX sites in Q3.",
            ),
        ],
    }


def get_insights() -> list:
    return [
        {
            "id":    0,
            "title": "Fill & Refuel Outperforming — Expand to Midwest",
            "detail":"Fill & Refuel is generating 12.4% uplift in South. Midwest sites with similar traffic profiles show no active campaign — projected +$2.1M incremental revenue if extended.",
            "metric":"+$2.1M est. opportunity",
            "urgency":"High",
            "suggested_name":     "Midwest Fill & Refuel",
            "suggested_channels": ["Fuel loyalty", "POS", "SMS"],
            "suggested_region":   "Midwest",
        },
        {
            "id":    1,
            "title": "Afternoon Engagement Gap Across Urban Sites",
            "detail":"847 urban sites see 31% revenue decline 2–5pm. No active afternoon promotion. Competitors active in this window with food & beverage deals.",
            "metric":"847 affected sites",
            "urgency":"Medium",
            "suggested_name":     "Urban Afternoon Rush",
            "suggested_channels": ["In-store", "Digital", "App"],
            "suggested_region":   "all",
        },
        {
            "id":    2,
            "title": "Tobacco Decline — Basket Diversification Needed",
            "detail":"Tobacco category down 2.1% YoY in Texas & Southeast. 234 high-tobacco-dependency stores have 18% lower basket diversity. Cross-category promos show 3.4× ROI.",
            "metric":"234 high-risk sites",
            "urgency":"Medium",
            "suggested_name":     "Basket Builder",
            "suggested_channels": ["In-store", "Coupon", "Email"],
            "suggested_region":   "Southeast",
        },
    ]


def get_offer_strategy_data() -> dict:
    """Operational signals used by the offer decisioning and delivery surfaces."""
    return {
        "kpis": {
            "eligible_customers": 284600,
            "offers_ready": 18,
            "pump_to_store_rate": 34.8,
            "inventory_gated": 7,
            "margin_floor_pct": 5.0,
        },
        "pipeline": pd.DataFrame([
            {"stage": "Attract", "channel": "App + geofence", "metric": "New site visits", "value": "+8.4%", "status": "On track"},
            {"stage": "Nudge", "channel": "Pump screen + push", "metric": "Pump-to-store conversion", "value": "34.8%", "status": "Growing"},
            {"stage": "Convert", "channel": "POS + self-checkout", "metric": "Offer redemption", "value": "22.6%", "status": "On track"},
            {"stage": "Retain", "channel": "Loyalty + email", "metric": "30-day return rate", "value": "41.2%", "status": "Watch"},
        ]),
        "decisioning": pd.DataFrame([
            {"customer_id": "CUST-1001", "context": "Morning commuter", "offer": "$1 off usual coffee", "reason": "Coffee affinity + 07:00 daypart", "score": 0.92, "channel": "Pump screen"},
            {"customer_id": "CUST-1001", "context": "Morning commuter", "offer": "Coffee + breakfast bundle", "reason": "Similar Gold customers redeemed", "score": 0.84, "channel": "Mobile app"},
            {"customer_id": "CUST-1001", "context": "Morning commuter", "offer": "10c/gal fuel reward", "reason": "Spend threshold nearly met", "score": 0.71, "channel": "Pump screen"},
        ]),
        "triggers": pd.DataFrame([
            {"event": "Pump start", "window": "< 3 sec", "offer": "Personalized coffee", "fallback": "Generic coffee promo", "owner": "Pump CMS"},
            {"event": "Fueling complete", "window": "15 min", "offer": "In-store entry incentive", "fallback": "Standard store CTA", "owner": "Offer engine"},
            {"event": "Geofence entry", "window": "< 15 sec", "offer": "Nearby loyalty offer", "fallback": "Brand message", "owner": "Mobile app"},
            {"event": "Hot weather > 85F", "window": "Real time", "offer": "Cold beverage override", "fallback": "Daypart offer", "owner": "Context service"},
        ]),
        "bundles": pd.DataFrame([
            {"bundle": "Coffee + Breakfast", "affinity": "3.8x", "inventory_gate": "Pass", "margin": "18.4%", "prompt": "On beverage scan"},
            {"bundle": "Fuel + Snack", "affinity": "3.4x", "inventory_gate": "Pass", "margin": "16.1%", "prompt": "Post-fuel push"},
            {"bundle": "Cold Drink + Snack", "affinity": "2.9x", "inventory_gate": "Review", "margin": "7.2%", "prompt": "Hot weather"},
        ]),
        "fuel_rewards": pd.DataFrame([
            {"threshold": "$10 in-store spend", "reward": "10c/gal", "eligible_members": "Gold + Silver", "audit_state": "Tracked"},
            {"threshold": "$20 in-store spend", "reward": "20c/gal", "eligible_members": "All loyalty", "audit_state": "Tracked"},
            {"threshold": "3 qualifying visits", "reward": "5c/gal", "eligible_members": "Bronze", "audit_state": "Tracked"},
        ]),
        "visibility": pd.DataFrame([
            {"channel": "Pump screen", "coverage": "94%", "latency": "< 30 sec", "impression_tracking": "Enabled"},
            {"channel": "Mobile push", "coverage": "68%", "latency": "< 15 sec", "impression_tracking": "Enabled"},
            {"channel": "Digital shelf label", "coverage": "81%", "latency": "< 60 sec", "impression_tracking": "Planned"},
            {"channel": "Entrance signage", "coverage": "100%", "latency": "< 5 min", "impression_tracking": "Enabled"},
        ]),
    }


def get_pricing_data() -> dict:
    rng = np.random.default_rng(55)

    # State-level WTP and pricing (income index drives WTP and recommended price)
    state_info = [
        ("TX","South",      31.0,-100.0, 0.72),
        ("LA","South",      31.2, -92.4, 0.58),
        ("OK","South",      35.5, -97.5, 0.61),
        ("FL","Southeast",  27.8, -81.6, 0.74),
        ("GA","Southeast",  32.9, -83.4, 0.68),
        ("NC","Southeast",  35.6, -79.4, 0.67),
        ("TN","Southeast",  35.8, -86.7, 0.63),
        ("IL","Midwest",    40.0, -89.2, 0.76),
        ("OH","Midwest",    40.4, -82.7, 0.69),
        ("MI","Midwest",    44.3, -85.6, 0.68),
        ("MN","Midwest",    46.4, -93.1, 0.78),
        ("CA","West",       36.7,-119.4, 0.94),
        ("WA","West",       47.4,-120.5, 0.88),
        ("CO","West",       39.1,-105.4, 0.83),
        ("AZ","West",       34.3,-111.1, 0.71),
        ("NY","Northeast",  42.9, -75.5, 0.91),
        ("PA","Northeast",  40.9, -77.8, 0.73),
        ("NJ","Northeast",  40.1, -74.5, 0.92),
        ("MA","Northeast",  42.3, -71.8, 0.93),
        ("CT","Northeast",  41.6, -72.7, 0.94),
    ]
    records = []
    for state, region, lat, lon, income_idx in state_info:
        base_price      = round(3.20 + income_idx * 1.2 + rng.normal(0, 0.06), 2)
        wtp             = round(4.5 + income_idx * 5.2 + rng.normal(0, 0.25), 1)
        wtp             = float(np.clip(wtp, 4.0, 10.0))
        recommended     = round(base_price + (income_idx - 0.50) * 0.28 + 0.04, 2)
        competitor      = round(base_price + rng.uniform(-0.10, 0.14), 2)
        n_sites         = int(rng.integers(80, 420))
        opportunity_m   = round(max(0, (recommended - base_price) * n_sites * 14_000 / 1e6), 2)
        records.append({
            "state": state, "region": region, "lat": lat, "lon": lon,
            "income_index":      round(income_idx, 2),
            "wtp_score":         wtp,
            "current_price":     base_price,
            "recommended_price": recommended,
            "competitor_price":  competitor,
            "sites":             n_sites,
            "opportunity_m":     opportunity_m,
        })
    wtp_df = pd.DataFrame(records)

    # Regional aggregation for price sensitivity chart
    reg_df = wtp_df.groupby("region").agg(
        current_price    =("current_price",    "mean"),
        recommended_price=("recommended_price","mean"),
        competitor_price =("competitor_price", "mean"),
    ).round(3).reset_index()

    # Customer segment WTP
    segments = pd.DataFrame([
        {"segment": "Loyalty Gold",   "wtp_score": 8.9, "price_sensitivity": 0.22, "avg_spend": 68, "share_pct": 18},
        {"segment": "Loyalty Silver", "wtp_score": 7.8, "price_sensitivity": 0.35, "avg_spend": 52, "share_pct": 24},
        {"segment": "Loyalty Bronze", "wtp_score": 6.9, "price_sensitivity": 0.48, "avg_spend": 41, "share_pct": 19},
        {"segment": "Non-Loyalty",    "wtp_score": 5.4, "price_sensitivity": 0.72, "avg_spend": 29, "share_pct": 39},
    ])

    # Top site recommendations
    sample_sites = SITES_DF.sample(10, random_state=42).copy()
    sample_sites = sample_sites.merge(
        wtp_df[["state","current_price","recommended_price","wtp_score","income_index"]],
        on="state", how="left"
    ).dropna()
    sample_sites["confidence"] = rng.choice(["High","High","Medium","Medium","Low"], size=len(sample_sites))
    sample_sites["uplift_pct"] = (
        (sample_sites["recommended_price"] - sample_sites["current_price"])
        / sample_sites["current_price"] * 100
    ).round(1)
    sample_sites["action"] = sample_sites.apply(
        lambda r: "Increase" if r["recommended_price"] > r["current_price"] else "Hold", axis=1
    )
    recs = sample_sites[["name","region","state","current_price","recommended_price",
                          "uplift_pct","confidence","action"]].head(10).copy()
    recs.columns = ["Site","Region","State","Current $","Rec. $","Uplift %","Confidence","Action"]

    return {
        "wtp_by_state":      wtp_df,
        "region_pricing":    reg_df,
        "segments":          segments,
        "recommendations":   recs,
        "sim_regions":       ["South","Southeast","Midwest","West","Northeast"],
        "sim_base_volumes":  [4.2, 2.8, 3.1, 3.6, 2.2],   # M gal/month
        "sim_elasticities":  [-0.55, -0.62, -0.58, -0.45, -0.41],
        "sim_base_prices":   [3.45, 3.38, 3.52, 4.12, 3.89],
        "kpis": {
            "avg_wtp":            round(float(wtp_df.wtp_score.mean()), 1),
            "sites_opportunity":  int((wtp_df[wtp_df.recommended_price > wtp_df.current_price].sites.sum())),
            "est_uplift_m":       round(float(wtp_df.opportunity_m.sum()), 1),
            "model_coverage_pct": 94.2,
            "avg_price_gap_c":    round(float((wtp_df.recommended_price - wtp_df.current_price).mean() * 100), 1),
        }
    }


def get_whatif_base_data() -> dict:
    campaigns = get_active_campaigns()[
        ["campaign_id","name","campaign_uplift_pct","incremental_revenue_m",
         "basket_size_increase","participation_rate","target_region"]
    ].to_dict("records")

    channel_params = {
        "Fuel Loyalty": {"cpr": 0.12, "cvr": 0.31, "basket_lift": 1.8},
        "In-Store POS":  {"cpr": 0.08, "cvr": 0.24, "basket_lift": 1.4},
        "Digital":       {"cpr": 0.15, "cvr": 0.18, "basket_lift": 1.2},
        "SMS":           {"cpr": 0.09, "cvr": 0.27, "basket_lift": 1.5},
        "Email":         {"cpr": 0.06, "cvr": 0.22, "basket_lift": 1.3},
        "App Push":      {"cpr": 0.05, "cvr": 0.35, "basket_lift": 2.1},
    }

    channel_mixes = {
        "Balanced":       [25, 20, 20, 15, 15, 5],
        "Digital-First":  [15, 10, 35, 20, 15, 5],
        "Loyalty-First":  [40, 20, 10, 15, 10, 5],
        "In-Store Focus": [20, 40, 15, 10, 10, 5],
    }

    return {
        "campaigns":      campaigns,
        "channel_params": channel_params,
        "channel_mixes":  channel_mixes,
        "region_sites":   {"South":2800,"Southeast":1900,"Midwest":2100,"West":2400,"Northeast":1800},
        "region_basket":  {"South":8.20,"Southeast":7.85,"Midwest":8.45,"West":9.10,"Northeast":9.80},
    }


def get_loyalty_data() -> dict:
    months_cy = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    # CY 2026 YTD (Jan–May actual, Jun–Dec projected)
    reg_cy  = [142_000,148_000,155_000,161_000,168_000,175_000,182_000,190_000,197_000,204_000,211_000,218_000]
    act_cy  = [88_000, 94_000, 99_000,105_000,111_000,116_000,121_000,127_000,132_000,138_000,144_000,150_000]
    # PY 2025 (full year actuals)
    reg_py  = [81_000, 87_000, 92_000, 98_000,105_000,111_000,117_000,123_000,129_000,135_000,141_000,147_000]
    act_py  = [50_000, 54_000, 58_000, 62_000, 67_000, 71_000, 75_000, 79_000, 83_000, 87_000, 91_000, 95_000]

    ytd_months = 5  # Jan–May YTD
    cy_reg_ytm  = sum(reg_cy[:ytd_months])
    cy_act_ytm  = sum(act_cy[:ytd_months])
    py_reg_ytm  = sum(reg_py[:ytd_months])
    py_act_ytm  = sum(act_py[:ytd_months])

    # Site-level summary (top 15 sites)
    sites = [
        ("S001","QuickFuel Houston Galleria","South","TX",1_240,820,1_080,710,14.8,15.5),
        ("S003","QuickFuel Dallas Uptown","South","TX",1_180,760,1_010,660,16.8,15.2),
        ("S005","QuickFuel Austin Downtown","South","TX",1_090,720, 940,620,16.0,16.1),
        ("S041","QuickFuel Atlanta Midtown","Southeast","GA",1_050,680, 895,580,17.3,17.2),
        ("S061","QuickFuel Chicago Loop","Midwest","IL",1_120,740, 955,640,17.3,15.6),
        ("S081","QuickFuel LA Westside","West","CA",1_310,890,1_140,770,14.9,15.6),
        ("S083","QuickFuel LA Sherman Oaks","West","CA",1_200,810,1_020,700,17.6,15.7),
        ("S101","QuickFuel NYC Midtown","Northeast","NY",1_380,960,1_200,840,15.0,14.3),
        ("S021","QuickFuel Miami Beach","Southeast","FL",1_020,660, 870,565,17.2,16.8),
        ("S023","QuickFuel Tampa Ybor","Southeast","FL",  980,630, 835,540,17.4,16.7),
        ("S071","QuickFuel Phoenix Central","West","AZ",1_040,670, 890,580,16.9,15.5),
        ("S031","QuickFuel Denver LoDo","Midwest","CO",  990,640, 845,550,17.2,16.4),
        ("S111","QuickFuel Boston Back Bay","Northeast","MA",1_150,760,  980,660,17.3,15.2),
        ("S091","QuickFuel Seattle Capitol","West","WA",1_070,710,  910,615,17.6,15.4),
        ("S007","QuickFuel San Antonio Alamo","South","TX",  890,565,  760,485,17.1,16.5),
    ]
    site_df = pd.DataFrame(sites, columns=[
        "site_id","site_name","region","state",
        "reg_cy","act_cy","reg_py","act_py",
        "act_rate_cy","act_rate_py"
    ])
    site_df["reg_yoy_pct"]  = ((site_df.reg_cy - site_df.reg_py) / site_df.reg_py * 100).round(1)
    site_df["act_yoy_pct"]  = ((site_df.act_cy - site_df.act_py) / site_df.act_py * 100).round(1)

    # Regional rollup
    region_summary = pd.DataFrame([
        ("South",    3_850, 2_520, 3_290, 2_150),
        ("Southeast",2_980, 1_940, 2_540, 1_650),
        ("Midwest",  3_120, 2_050, 2_660, 1_750),
        ("West",     3_640, 2_410, 3_100, 2_050),
        ("Northeast",2_820, 1_870, 2_400, 1_590),
    ], columns=["region","reg_cy","act_cy","reg_py","act_py"])
    region_summary["reg_yoy"] = ((region_summary.reg_cy - region_summary.reg_py) / region_summary.reg_py * 100).round(1)
    region_summary["act_yoy"] = ((region_summary.act_cy - region_summary.act_py) / region_summary.act_py * 100).round(1)

    # Executive summary comparison (matches sample dashboard style)
    exec_summary = [
        ("Total Registrations CY YTM",         f"{cy_reg_ytm:,}",     f"{py_reg_ytm:,}",    f"+{(cy_reg_ytm-py_reg_ytm)/py_reg_ytm*100:.1f}%"),
        ("Total Loyalty Redeemed Activations",  f"{cy_act_ytm:,}",     f"{py_act_ytm:,}",    f"+{(cy_act_ytm-py_act_ytm)/py_act_ytm*100:.1f}%"),
        ("Activation Rate (Act/Reg)",           f"{cy_act_ytm/cy_reg_ytm*100:.1f}%", f"{py_act_ytm/py_reg_ytm*100:.1f}%", f"+{(cy_act_ytm/cy_reg_ytm - py_act_ytm/py_reg_ytm)*100:.1f}pp"),
        ("FR Redeemed Penetration",             "12.8%",  "11.6%",  "+1.2pp"),
        ("FR Redeemed Volume",                  "142.6M", "131.1M", "+8.8%"),
        ("FR Other Redeemer Penetration",       "3.2%",   "2.9%",   "+0.3pp"),
        ("FR Other Redeemer Volume",            "35.4M",  "31.1M",  "+13.8%"),
        ("Avg Activation Rate per Site",        "16.8%",  "14.2%",  "+2.6pp"),
        ("Site Count",                          "12,374", "12,244", "+130"),
    ]

    # ── Site × month detail tables (for exec summary drill-down) ────────────
    seasonal = [0.93,0.90,0.95,0.98,1.02,1.08,1.10,1.08,1.04,1.00,0.97,0.95]
    seasonal_sum = sum(seasonal)

    def _site_month_rows(annual_vals, fmt="int"):
        rows = []
        for (_, name, region, state, *_rest), annual in zip(sites, annual_vals):
            monthly = [round(annual * s / seasonal_sum) for s in seasonal]
            total   = sum(monthly)
            row = {"Site": name, "Region": region, "State": state}
            for m, v in zip(months_cy, monthly):
                row[m] = f"{v/1e6:.3f}M" if fmt == "M" else (f"{v:.1f}%" if fmt == "pct" else f"{v:,}")
            row["Total"] = f"{total/1e6:.2f}M" if fmt == "M" else (f"{total/len(months_cy):.1f}%" if fmt == "pct" else f"{total:,}")
            rows.append(row)
        return rows

    # FR Redeemed Volume: ~142.6M gallons/yr across 12,374 sites → top sites ~950K–1.1M gal/yr each
    fr_vol_annual = [1_080_000, 1_020_000, 950_000, 910_000, 975_000,
                     1_140_000, 1_050_000, 1_210_000, 880_000, 845_000,
                     900_000, 860_000, 1_000_000, 930_000, 780_000]
    # FR Other Volume: ~35.4M / 15 top sites ≈ ~300K each
    fr_other_annual = [310_000,295_000,275_000,265_000,280_000,
                       330_000,305_000,350_000,255_000,245_000,
                       260_000,250_000,290_000,270_000,225_000]

    detail_data = {
        "Total Registrations CY YTM":        {"unit": "count", "rows": _site_month_rows(list(site_df.reg_cy * 12 // 5))},
        "Total Loyalty Redeemed Activations": {"unit": "count", "rows": _site_month_rows(list(site_df.act_cy * 12 // 5))},
        "Activation Rate (Act/Reg)":          {"unit": "pct",   "rows": _site_month_rows([round(r,1) for r in site_df.act_rate_cy], fmt="pct")},
        "FR Redeemed Penetration":            {"unit": "pct",   "rows": _site_month_rows([12.8]*15, fmt="pct")},
        "FR Redeemed Volume":                 {"unit": "M gal", "rows": _site_month_rows(fr_vol_annual, fmt="M")},
        "FR Other Redeemer Penetration":      {"unit": "pct",   "rows": _site_month_rows([3.2]*15, fmt="pct")},
        "FR Other Redeemer Volume":           {"unit": "M gal", "rows": _site_month_rows(fr_other_annual, fmt="M")},
        "Avg Activation Rate per Site":       {"unit": "pct",   "rows": _site_month_rows(list(site_df.act_rate_cy), fmt="pct")},
        "Site Count":                         {"unit": "count", "rows": [{"Site": r["site_name"], "Region": r["region"],
                                                                           "State": r["state"], "Status": "Active",
                                                                           "Reg CY": f"{r['reg_cy']:,}",
                                                                           "Act CY": f"{r['act_cy']:,}",
                                                                           "Act Rate": f"{r['act_rate_cy']:.1f}%"}
                                                                          for r in site_df.to_dict("records")]},
    }

    return {
        "months":         months_cy,
        "reg_cy":         reg_cy,
        "act_cy":         act_cy,
        "reg_py":         reg_py,
        "act_py":         act_py,
        "ytd_months":     ytd_months,
        "kpis": {
            "cy_act_ytm":  cy_act_ytm,
            "py_act_ytm":  py_act_ytm,
            "act_yoy_pct": round((cy_act_ytm - py_act_ytm) / py_act_ytm * 100, 1),
            "cy_reg_ytm":  cy_reg_ytm,
            "py_reg_ytm":  py_reg_ytm,
            "reg_yoy_pct": round((cy_reg_ytm - py_reg_ytm) / py_reg_ytm * 100, 1),
        },
        "site_df":        site_df,
        "region_summary": region_summary,
        "exec_summary":   exec_summary,
        "detail_data":    detail_data,
    }


def get_customer_profile() -> pd.DataFrame:
    rows = [
        {
            "profile_sk": 1,
            "customer_id": "CUST-1001",
            "loyalty_id": "LOY-1001",
            "first_name": "James",
            "last_name": "Smith",
            "email": "5f5d525b0d5f91d9ec8d3b9a0d8af87d5d0a5a9d34d57343b9f8a494e1c8d8f",
            "phone_number": "64b4b7338f3b1d9b58dd8b45d86d820fa8f5c4ff0c85af75ef6c4cf8a44b83df",
            "home_zip": "77002",
            "preferred_store_id": "ST-7702",
            "preferred_channel": "APP",
            "enrollment_date": "2022-03-10",
            "loyalty_tier": "GOLD",
            "status": "ACTIVE",
            "push_opt_in_flag": True,
            "sms_opt_in_flag": True,
            "email_opt_in_flag": True,
            "app_user_flag": True,
            "created_ts": pd.Timestamp("2022-03-10 08:15:00"),
            "updated_ts": pd.Timestamp("2026-07-01 09:30:00"),
            "source_system": "LOYALTY_PLATFORM_V2",
            "effective_start_date": "2026-06-01",
            "effective_end_date": None,
            "is_current": True,
            "_change_hash": "d9f3ecf36bc2b9d8b4ad7d3d3f14c4b2",
            "_silver_loaded_at": pd.Timestamp("2026-07-01 10:00:00"),
        },
        {
            "profile_sk": 2,
            "customer_id": "CUST-1002",
            "loyalty_id": "LOY-1002",
            "first_name": "Maria",
            "last_name": "Garcia",
            "email": "68d1c9db2d60c7edcb57f3d4a4c7f34d62c9b7d91d0c2d726c2b6e6185cc6c3",
            "phone_number": "c1a2b4a30d5e9d08bde4f9bd6b9c4f0a39052f26ec3f5af5d8d7d9bd9e68214",
            "home_zip": "75001",
            "preferred_store_id": "ST-7501",
            "preferred_channel": "SMS",
            "enrollment_date": "2021-11-02",
            "loyalty_tier": "SILVER",
            "status": "ACTIVE",
            "push_opt_in_flag": False,
            "sms_opt_in_flag": True,
            "email_opt_in_flag": False,
            "app_user_flag": False,
            "created_ts": pd.Timestamp("2021-11-02 12:00:00"),
            "updated_ts": pd.Timestamp("2026-06-22 13:00:00"),
            "source_system": "LOYALTY_PLATFORM_V2",
            "effective_start_date": "2026-06-22",
            "effective_end_date": None,
            "is_current": True,
            "_change_hash": "0f6d008744e0fe4c0baa4d78df2d2db9",
            "_silver_loaded_at": pd.Timestamp("2026-06-22 13:10:00"),
        },
        {
            "profile_sk": 3,
            "customer_id": "CUST-1003",
            "loyalty_id": "LOY-1003",
            "first_name": "David",
            "last_name": "Nguyen",
            "email": "ab6e780b377f9d718f8f09c89a7ef4eb26d5c9970be5c26196e4e429093ab4d5",
            "phone_number": "12c0622d5f38bed7db4ed573d7d6665f13ea1f89b555523e96ba3ef1d0ecad6b",
            "home_zip": "77005",
            "preferred_store_id": "ST-7705",
            "preferred_channel": "EMAIL",
            "enrollment_date": "2020-09-18",
            "loyalty_tier": "BRONZE",
            "status": "SUSPENDED",
            "push_opt_in_flag": False,
            "sms_opt_in_flag": False,
            "email_opt_in_flag": True,
            "app_user_flag": False,
            "created_ts": pd.Timestamp("2020-09-18 07:45:00"),
            "updated_ts": pd.Timestamp("2026-06-30 08:45:00"),
            "source_system": "LOYALTY_PLATFORM_V2",
            "effective_start_date": "2026-06-30",
            "effective_end_date": None,
            "is_current": True,
            "_change_hash": "9af3e26e2f415d7a4b8d7a1589bc3b62",
            "_silver_loaded_at": pd.Timestamp("2026-06-30 09:00:00"),
        },
    ]
    return pd.DataFrame(rows)


def get_customer_profile_quarantine() -> pd.DataFrame:
    return pd.DataFrame([
        {
            "customer_id": "CUST-2001",
            "loyalty_id": None,
            "error_code": "NULL_LOYALTY_ID",
            "error_message": "customer_id valid but loyalty_id missing",
            "_silver_loaded_at": pd.Timestamp("2026-07-01 08:45:00"),
        },
        {
            "customer_id": "CUST-2002",
            "loyalty_id": "LOY-2002",
            "error_code": "INVALID_EMAIL_FORMAT",
            "error_message": "email did not match expected hash format after cleaning",
            "_silver_loaded_at": pd.Timestamp("2026-07-01 08:55:00"),
        },
    ])


def get_scd2_quality_summary() -> dict:
    return {
        "customer_records": 3,
        "current_records": 3,
        "duplicate_current_rows": 0,
        "unknown_loyalty_tier_count": 0,
        "quarantine_rows": 2,
        "scd2_columns": [
            "loyalty_tier",
            "status",
            "preferred_channel",
            "home_zip",
            "preferred_store_id",
            "push_opt_in_flag",
            "sms_opt_in_flag",
            "email_opt_in_flag",
        ],
        "validation_status": "pass",
    }


def get_scd2_quality_cards() -> dict:
    return {
        "total_customers": 3,
        "quality_score": 96,
        "quarantine_rate_pct": 66.7,
        "duplicate_current_rows": 0,
        "unknown_loyalty_tier_count": 0,
    }


def get_customer_profile_history(customer_id: str | None = None) -> pd.DataFrame:
    df = get_customer_profile()
    if customer_id:
        df = df[df["customer_id"] == customer_id].copy()
    return df[[
        "customer_id",
        "loyalty_tier",
        "status",
        "preferred_channel",
        "home_zip",
        "preferred_store_id",
        "push_opt_in_flag",
        "sms_opt_in_flag",
        "email_opt_in_flag",
        "effective_start_date",
        "effective_end_date",
        "is_current",
        "_change_hash",
    ]].sort_values(["customer_id", "effective_start_date"]).reset_index(drop=True)


def get_scd2_guide() -> dict:
    return {
        "title": "Shell Project - SCD2 & Data Quality Guide",
        "version": "2.0",
        "prepared_by": "Kenneth Sherrod",
        "audience": "Development Team",
        "overview": "Historical tracking, transformation rules, and validation applied to the official Shell data schema.",
        "scd2_tracked_columns": [
            "loyalty_tier",
            "status",
            "preferred_channel",
            "home_zip",
            "preferred_store_id",
            "push_opt_in_flag",
            "sms_opt_in_flag",
            "email_opt_in_flag",
        ],
        "scd1_columns": [
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "app_user_flag",
        ],
        "quality_checks": [
            "Exactly one current row per customer_id",
            "No open rows with effective_end_date populated",
            "No closed rows without an end date",
            "Hash-based change detection with COALESCE sentinel",
            "Quarantine rate under 5% of input rows",
        ],
    }


def get_current_user_from_headers(headers=None) -> dict:
    return {"email": "user@apexsystems.com", "name": "Local User"}
