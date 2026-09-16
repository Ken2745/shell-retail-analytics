"""
genie_helper.py — Databricks AI/BI Genie for Shell Retail Intelligence
"""
import time
import os
import requests
import pandas as pd
from databricks import sql as dbsql

DATABRICKS_HOST  = os.getenv("DATABRICKS_HOST", "https://dbc-b7c54f7a-7524.cloud.databricks.com")
DATABRICKS_TOKEN = os.getenv("DATABRICKS_TOKEN", "")
GENIE_SPACE_ID   = "01f163791f3d17e795f7b3dedec1066f"
WAREHOUSE_ID     = os.getenv("DATABRICKS_SQL_WAREHOUSE_ID", "e2f2719979a11f9d")

_HEADERS = {
    "Authorization": f"Bearer {DATABRICKS_TOKEN}",
    "Content-Type":  "application/json",
}


def ask_genie(question: str) -> dict:
    """Returns {'sql': ..., 'dataframe': ..., 'text': ..., 'error': ...}."""
    try:
        result    = _get_genie_response(question)
        sql_query = result.get("sql")
        text_ans  = result.get("text")

        if not sql_query and not text_ans:
            return {"error": "Genie could not generate an answer. Try rephrasing."}

        out = {}
        if text_ans:
            out["text"] = text_ans
        if sql_query:
            out["sql"] = sql_query
            df = _execute_sql(sql_query)
            out["dataframe"] = df if df is not None else pd.DataFrame()
        return out
    except Exception as exc:
        return {"error": str(exc)}


def _get_genie_response(prompt: str) -> dict:
    try:
        url  = f"{DATABRICKS_HOST}/api/2.0/genie/spaces/{GENIE_SPACE_ID}/start-conversation"
        resp = requests.post(url, headers=_HEADERS, json={"content": prompt}, timeout=30)
        data = resp.json()

        conversation_id = data.get("conversation_id")
        message_id      = data.get("message_id")
        if not conversation_id or not message_id:
            return {}

        poll_url = (
            f"{DATABRICKS_HOST}/api/2.0/genie/spaces/{GENIE_SPACE_ID}"
            f"/conversations/{conversation_id}/messages/{message_id}"
        )
        for _ in range(24):
            r2    = requests.get(poll_url, headers=_HEADERS, timeout=20)
            data2 = r2.json()
            status = data2.get("status") or data2.get("message", {}).get("status")

            if status in ("COMPLETED", "EXECUTING_QUERY"):
                result = {}
                for att in data2.get("attachments", []):
                    if "query" in att:
                        result["sql"] = att["query"].get("query")
                    if "text" in att:
                        result["text"] = att["text"].get("content", "")
                return result

            if status in ("COMPLETED_WITH_ERROR", "FAILED"):
                return {}

            time.sleep(2.5)

        return {}
    except Exception as exc:
        print(f"[Genie] error: {exc}")
        return {}


def _execute_sql(sql_query: str) -> pd.DataFrame | None:
    try:
        hostname = DATABRICKS_HOST.replace("https://", "")
        with dbsql.connect(
            server_hostname=hostname,
            http_path=f"/sql/1.0/warehouses/{WAREHOUSE_ID}",
            access_token=DATABRICKS_TOKEN,
        ) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql_query)
                cols = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                return pd.DataFrame(rows, columns=cols)
    except Exception as exc:
        print(f"[Genie] SQL error: {exc}")
        return None
