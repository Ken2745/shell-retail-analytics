"""
backend.py — Shell retail data access layer
Real Databricks SQL queries against the Shell workspace.
Falls back to mock data on query failure.
"""
import os
import pandas as pd
from databricks import sql as dbsql
from databricks.sdk.core import Config

import backend_mock as _mock

cfg          = Config()
CATALOG      = "workspace"
SCHEMA       = "retail_store"
BRONZE_SCHEMA = "bronze"
WAREHOUSE_ID = os.getenv("DATABRICKS_SQL_WAREHOUSE_ID", "e2f2719979a11f9d")
_WH_PATH     = f"/sql/1.0/warehouses/{WAREHOUSE_ID}"

KNOWN_TABLES = {
    "customer_profile",
    "customer_profile_quarantine",
    "loyalty_events_raw",
    "store_master",
    "product_master",
    "bundle_definition",
    "offers",
    "customer_preference",
    "daily_sales",
    "campaigns",
    "regional_summary",
    "sites",
}


def _conn():
    hostname = cfg.host.replace("https://", "").replace("http://", "").rstrip("/")
    return dbsql.connect(
        server_hostname=hostname,
        http_path=_WH_PATH,
        access_token=cfg.token,
    )


def _query(sql: str) -> pd.DataFrame:
    try:
        with _conn() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                cols = [d[0] for d in cur.description]
                rows = cur.fetchall()
                return pd.DataFrame(rows, columns=cols)
    except Exception as e:
        print(f"[backend] SQL error: {e}")
        return pd.DataFrame()


def _table_exists(table_name: str) -> bool:
    if not table_name:
        return False
    info = _query(
        f"SELECT table_name FROM system.information_schema.tables "
        f"WHERE table_catalog = '{CATALOG}' AND table_schema = '{SCHEMA}' AND table_name = '{table_name}'"
    )
    return not info.empty


def _safe_query(table_name: str, select_sql: str, fallback):
    if not _table_exists(table_name):
        return fallback()
    df = _query(select_sql)
    return df if not df.empty else fallback()


def get_sites() -> pd.DataFrame:
    return _safe_query("sites", f"SELECT * FROM {CATALOG}.{SCHEMA}.sites", _mock.get_sites)


def get_kpis() -> dict:
    if not _table_exists("daily_sales"):
        return _mock.get_kpis()
    df = _query(f"""
        SELECT
            SUM(instore_revenue)        AS total_revenue,
            AVG(basket_size)            AS avg_basket,
            SUM(fuel_gallons)           AS total_gallons,
            COUNT(DISTINCT site_id)     AS site_count
        FROM {CATALOG}.{SCHEMA}.daily_sales
        WHERE date >= CURRENT_DATE - INTERVAL 90 DAY
    """)
    if df.empty:
        return _mock.get_kpis()
    row = df.iloc[0]
    return {
        "total_revenue_m":   round(float(row.total_revenue) / 1e6, 2),
        "basket_size":       round(float(row.avg_basket), 2),
        "basket_vs_prior":   3.2,
        "repeat_visits":     67.3,
        "repeat_vs_prior":   2.4,
        "rev_vs_prior":      5.8,
        "campaign_uplift":   8.7,
        "fuel_gallons_m":    round(float(row.total_gallons) / 1e6, 1),
        "fuel_vs_prior":    -0.4,
        "active_campaigns":  4,
        "total_sites":       int(row.site_count),
    }


def get_regional_summary() -> pd.DataFrame:
    return _safe_query("regional_summary", f"SELECT * FROM {CATALOG}.{SCHEMA}.regional_summary", _mock.get_regional_summary)


def get_site_type_breakdown() -> pd.DataFrame:
    if not _table_exists("daily_sales") or not _table_exists("sites"):
        return _mock.get_site_type_breakdown()
    df = _query(f"""
        SELECT s.site_type,
               SUM(d.instore_revenue) AS revenue,
               COUNT(DISTINCT d.site_id) AS site_count,
               AVG(d.basket_size) AS avg_basket,
               SUM(d.fuel_gallons) AS fuel_gallons
        FROM {CATALOG}.{SCHEMA}.daily_sales d
        JOIN {CATALOG}.{SCHEMA}.sites s ON d.site_id = s.site_id
        WHERE d.date >= CURRENT_DATE - INTERVAL 90 DAY
        GROUP BY s.site_type
    """)
    return df if not df.empty else _mock.get_site_type_breakdown()


def get_top_bottom_stores(n=5):
    return _mock.get_top_bottom_stores(n)


def get_active_campaigns() -> pd.DataFrame:
    return _safe_query("campaigns", f"SELECT * FROM {CATALOG}.{SCHEMA}.campaigns WHERE status = 'Active'", _mock.get_active_campaigns)


def get_historic_campaigns() -> pd.DataFrame:
    return _safe_query("campaigns", f"SELECT * FROM {CATALOG}.{SCHEMA}.campaigns WHERE status = 'Historic'", _mock.get_historic_campaigns)


def get_all_campaigns() -> pd.DataFrame:
    return _safe_query("campaigns", f"SELECT * FROM {CATALOG}.{SCHEMA}.campaigns", _mock.get_all_campaigns)


def get_campaign_kpis(campaign_ids=None):     return _mock.get_campaign_kpis(campaign_ids)
def get_campaign_comparison(campaign_ids):    return _mock.get_campaign_comparison(campaign_ids)
def get_campaign_detail(campaign_id):         return _mock.get_campaign_detail(campaign_id)
def get_texas_detail():                       return _mock.get_texas_detail()
def get_insights():                           return _mock.get_insights()
def get_offer_strategy_data():                 return _mock.get_offer_strategy_data()
def get_pricing_data():                       return _mock.get_pricing_data()
def get_whatif_base_data():                   return _mock.get_whatif_base_data()
def get_loyalty_data():                       return _mock.get_loyalty_data()


def get_data_catalog() -> pd.DataFrame:
    df = _query(
        "SELECT table_name, table_type, comment "
        f"FROM {CATALOG}.information_schema.tables "
        f"WHERE table_schema = '{SCHEMA}' ORDER BY table_name"
    )
    return df if not df.empty else _mock.get_data_catalog()


def get_data_freshness() -> pd.DataFrame:
    df = _query(
        "SELECT table_name, last_altered "
        f"FROM {CATALOG}.information_schema.tables "
        f"WHERE table_schema = '{SCHEMA}' ORDER BY last_altered DESC"
    )
    return df if not df.empty else _mock.get_data_freshness()


def get_customer_profile() -> pd.DataFrame:
    return _safe_query(
        "customer_profile",
        f"SELECT * FROM {CATALOG}.{SCHEMA}.customer_profile ORDER BY customer_id, effective_start_date",
        _mock.get_customer_profile,
    )


def get_customer_profile_quarantine() -> pd.DataFrame:
    return _safe_query(
        "customer_profile_quarantine",
        f"SELECT * FROM {CATALOG}.{SCHEMA}.customer_profile_quarantine ORDER BY _silver_loaded_at DESC",
        _mock.get_customer_profile_quarantine,
    )


def get_scd2_quality_summary() -> dict:
    df = get_customer_profile()
    if df.empty:
        return _mock.get_scd2_quality_summary()

    current = df[df.is_current == True].copy() if "is_current" in df.columns else df.copy()
    current_counts = current["loyalty_tier"].value_counts() if "loyalty_tier" in current.columns else pd.Series(dtype=int)
    unknown_tier = int(current_counts.get("UNKNOWN", 0))
    duplicates = int((current.groupby("customer_id").size() > 1).sum()) if "customer_id" in current.columns else 0

    return {
        "customer_records": int(len(df)),
        "current_records": int(len(current)),
        "duplicate_current_rows": duplicates,
        "unknown_loyalty_tier_count": unknown_tier,
        "quarantine_rows": int(len(get_customer_profile_quarantine())),
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
        "validation_status": "pass" if duplicates == 0 and unknown_tier <= max(1, len(current) * 0.01) else "alert",
    }


def get_scd2_quality_cards() -> dict:
    summary = get_scd2_quality_summary()
    total_customers = max(1, summary.get("current_records", 0))
    qc = summary.get("quarantine_rows", 0)
    duplicates = summary.get("duplicate_current_rows", 0)
    unknown = summary.get("unknown_loyalty_tier_count", 0)
    quality_score = max(0, 100 - (qc * 5) - (duplicates * 15) - (unknown * 10))
    return {
        "total_customers": total_customers,
        "quality_score": min(100, quality_score),
        "quarantine_rate_pct": round((qc / total_customers) * 100, 2) if total_customers else 0.0,
        "duplicate_current_rows": duplicates,
        "unknown_loyalty_tier_count": unknown,
    }


def get_customer_profile_history(customer_id: str | None = None) -> pd.DataFrame:
    df = get_customer_profile()
    if customer_id:
        df = df[df["customer_id"] == customer_id].copy()
    if df.empty:
        return _mock.get_customer_profile_history(customer_id)
    cols = [
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
    ]
    cols = [c for c in cols if c in df.columns]
    return df[cols].sort_values(["customer_id", "effective_start_date"]).reset_index(drop=True)


def get_scd2_guide() -> dict:
    return _mock.get_scd2_guide()


def get_current_user_from_headers(headers=None) -> dict:
    if not headers:
        return {"email": "unknown", "name": "Unknown"}
    email = headers.get("x-forwarded-email", "unknown")
    name  = headers.get("x-forwarded-user-name", email)
    return {"email": email, "name": name}
