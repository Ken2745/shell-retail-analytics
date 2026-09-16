"""
Shell Retail Intelligence Dashboard
Shell retail performance, pricing, and customer experience analytics
"""
import os
from datetime import date, timedelta
from dotenv import load_dotenv
load_dotenv()

_USE_MOCK = os.getenv("USE_MOCK_BACKEND", "true").lower() in ("true", "1", "yes")
if _USE_MOCK:
    import backend_mock as bk
else:
    import backend as bk

import dash
from dash import dcc, html, Input, Output, State, dash_table, ctx, ALL
import plotly.graph_objects as go
import plotly.express as px

try:
    from genie_helper import ask_genie
    _GENIE_OK = True
except ImportError:
    _GENIE_OK = False
    def ask_genie(p):
        return {"error": "Genie helper not available locally. Set GENIE_SPACE_ID and re-run."}

# ── Brand colours ────────────────────────────────────────────────────────────
PRIMARY    = "#009FE3"  # Bright blue
PRIMARY_DARK = "#006DAD"
ACCENT     = "#00CFE8"  # Electric cyan
ACCENT_LT  = "#8DEAF3"
SECONDARY  = "#083B66"  # Deep ocean blue
SIDEBAR_BG = "#075985"
WHITE      = "#FFFFFF"
NEAR_BLACK = "#102A43"
PAGE_BG    = "#F2FAFD"
CARD_BG    = "#FFFFFF"
BORDER     = "#B9DCEB"
MUTED      = "#58758A"
SUCCESS    = "#059669"
WARNING    = "#D97706"
DANGER     = "#DC2626"
CHART_COLORS = [PRIMARY, ACCENT, "#2176AE", "#4DABF7", "#75E6F2", "#58758A", "#2CA58D"]

_PRIMARY_15 = "rgba(0,217,255,0.15)"
_PRIMARY_30 = "rgba(0,217,255,0.30)"
_ACCENT_15  = "rgba(125,249,255,0.15)"
_ACCENT_30  = "rgba(125,249,255,0.30)"
_TRANSP     = "rgba(0,0,0,0)"

# ── Logo ────────────────────────────────────────────────────────────────────
try:
    _logo_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(_logo_dir, "everforth_b64.txt"), "r") as _f:
        _EF_LOGO_SRC = _f.read().strip()
except Exception:
    _EF_LOGO_SRC = ""

# ── Plotly base layout ────────────────────────────────────────────────────
PLOT_LAYOUT = dict(
    paper_bgcolor=_TRANSP,
    plot_bgcolor=_TRANSP,
    font=dict(color=NEAR_BLACK, family="-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif", size=12),
    margin=dict(l=40, r=20, t=40, b=40),
    legend=dict(bgcolor="rgba(255,255,255,0.96)", bordercolor=BORDER,
                borderwidth=1, font=dict(color=NEAR_BLACK)),
    colorway=CHART_COLORS,
    xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER,
               tickfont=dict(color=MUTED), linecolor=BORDER),
    yaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER,
               tickfont=dict(color=MUTED), linecolor=BORDER),
)

def _L(fig, **kw):
    fig.update_layout(**{**PLOT_LAYOUT, **kw})
    return fig

# ── Helper UI components ─────────────────────────────────────────────────
def _card(*children, style=None):
    base = {"background": CARD_BG, "border": f"1px solid {BORDER}",
            "borderRadius": "8px", "padding": "20px", "marginBottom": "16px"}
    if style:
        base.update(style)
    return html.Div(list(children), style=base)

def _row(*children, gap="16px", mb="16px"):
    return html.Div(list(children), style={"display":"flex","gap":gap,"flexWrap":"wrap","marginBottom":mb})

def _G(*children, flex=1, min_w="220px"):
    # flatten when called as _G([comp1, comp2], flex=N) — single list arg
    kids = children[0] if (len(children) == 1 and isinstance(children[0], list)) else list(children)
    return html.Div(kids, style={"flex":str(flex),"minWidth":min_w})

def _kpi(label, value, unit="", sub=None, color=PRIMARY, clickable_id=None):
    inner = html.Div([
        html.Div(label, style={"color":MUTED,"fontSize":"11px","fontWeight":"600",
                               "textTransform":"uppercase","letterSpacing":"0.8px","marginBottom":"6px"}),
        html.Div(str(value), style={"color":color,"fontSize":"26px","fontWeight":"800","lineHeight":"1.1"}),
        html.Div(unit, style={"color":MUTED,"fontSize":"11px","marginTop":"2px"}),
        html.Div(sub, style={"color":MUTED,"fontSize":"11px","marginTop":"4px"}) if sub else html.Div(),
    ], style={"background":CARD_BG,"border":f"1px solid {BORDER}",
               "borderLeft":f"3px solid {color}","borderRadius":"8px",
               "padding":"16px","flex":"1","minWidth":"160px",
               "cursor":"pointer" if clickable_id else "default"})
    if clickable_id:
        inner.id = clickable_id
        inner.n_clicks = 0
    return inner

def _badge(text, color=PRIMARY, bg=None):
    bg = bg or _PRIMARY_15
    return html.Span(text, style={"background":bg,"color":color,
                                   "border":f"1px solid {_PRIMARY_30}","borderRadius":"4px",
                                   "padding":"2px 8px","fontSize":"11px","fontWeight":"700"})

def _section_title(title):
    return html.Div(title, style={
        "color":PRIMARY_DARK,"fontWeight":"700","fontSize":"15px",
        "borderLeft":f"4px solid {ACCENT}","paddingLeft":"10px",
        "marginBottom":"14px","fontFamily":"-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    })

def _page_header(title, subtitle=None):
    return html.Div([
        html.Div(style={"width":"4px","borderRadius":"2px","background":ACCENT,
                        "minHeight":"32px","marginRight":"12px"}),
        html.Div([
            html.H2(title, style={"margin":"0","color":PRIMARY_DARK,"fontSize":"22px",
                                   "fontWeight":"700","fontFamily":"-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"}),
            html.Div(subtitle, style={"color":MUTED,"fontSize":"13px","marginTop":"2px"}) if subtitle else html.Div(),
        ]),
    ], style={"display":"flex","alignItems":"flex-start","marginBottom":"20px",
               "paddingBottom":"16px","borderBottom":f"1px solid {BORDER}"})

def _chart(fig, height=320):
    return dcc.Graph(figure=fig, config={"displayModeBar":False}, style={"height":f"{height}px"})

def _table(df, tbl_id="tbl", max_rows=20):
    cols = [{"name": c.replace("_"," ").title(), "id": c} for c in df.columns]
    return dash_table.DataTable(
        id=f"dt-{tbl_id}",
        columns=cols,
        data=df.head(max_rows).to_dict("records"),
        style_table={"overflowX":"auto"},
        style_header={"backgroundColor":PRIMARY_DARK,"color":WHITE,"fontWeight":"700",
                       "fontSize":"11px","textTransform":"uppercase","letterSpacing":"0.5px",
                       "border":f"1px solid {BORDER}"},
        style_cell={"backgroundColor":CARD_BG,"color":NEAR_BLACK,"fontSize":"12px",
                     "padding":"8px 12px","border":f"1px solid {BORDER}",
                     "textOverflow":"ellipsis","maxWidth":"200px"},
        style_data_conditional=[{"if":{"row_index":"odd"},"backgroundColor":"#F3FAFD"}],
        page_size=15, sort_action="native",
    )

def _urgency_color(u):
    return DANGER if u == "High" else (ACCENT if u == "Medium" else PRIMARY)

def _btn(label, btn_id, color=PRIMARY, small=False, n_clicks=0, **extra_style):
    size = "10px 16px" if small else "10px 20px"
    return html.Button(label, id=btn_id, n_clicks=n_clicks, style={
        "background": color, "color": WHITE, "border": "none",
        "borderRadius": "6px", "padding": size, "fontSize": "12px",
        "fontWeight": "600", "cursor": "pointer",
        "fontFamily": "-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif", **extra_style,
    })

# ── Nav ──────────────────────────────────────────────────────────────────────
NAV_ITEMS = [
    ("tab-overview",      "Network Performance",      "01"),
    ("tab-regional",      "Station Portfolio",        "02"),
    ("tab-campaigns",     "Promotions Hub",           "03"),
    ("tab-insights",      "Operations Center",        "04"),
    ("tab-loyalty",       "Customer Insights",        "05"),
    ("tab-pricing",       "Fuel Strategy",            "06"),
    ("tab-whatif",        "Scenario Planner",         "07"),
    ("tab-genie",         "AI Assistant",             "08"),
    ("tab-shell-project", "Data Quality",             "09"),
    ("tab-data-catalog",  "Data Catalog",             "10"),
    ("tab-data-freshness", "Data Freshness",           "11"),
]

NAV_DETAILS = {
    "tab-overview": "Network pulse and revenue",
    "tab-regional": "Sites, states, and territories",
    "tab-campaigns": "Offers and promotion results",
    "tab-insights": "Alerts and recommended actions",
    "tab-loyalty": "Customer engagement signals",
    "tab-pricing": "Price sensitivity and WTP",
    "tab-whatif": "Model campaign scenarios",
    "tab-genie": "Ask questions of retail data",
    "tab-shell-project": "SCD2 controls and validation",
    "tab-data-catalog": "Available retail data assets",
    "tab-data-freshness": "Pipeline update timestamps",
}

NAV_GROUPS = [
    ("PERFORMANCE", ["tab-overview", "tab-regional", "tab-campaigns", "tab-insights"]),
    ("CUSTOMER & VALUE", ["tab-loyalty", "tab-pricing", "tab-whatif"]),
    ("DECISION SUPPORT", ["tab-genie"]),
    ("DATA GOVERNANCE", ["tab-shell-project", "tab-data-catalog", "tab-data-freshness"]),
]

def _nav_item(tid, label, num, active):
    is_active = (tid == active)
    return html.Div([
        html.Span(num, style={"fontSize":"9px","color":PRIMARY if is_active else "rgba(255,255,255,0.35)",
                               "fontWeight":"700","marginRight":"10px","letterSpacing":"1px",
                               "minWidth":"16px","display":"inline-block"}),
        html.Div([
            html.Div(label, style={"fontSize":"12px","fontWeight":"700" if is_active else "500",
                                   "letterSpacing":"0.2px"}),
            html.Div(NAV_DETAILS.get(tid, ""), style={"fontSize":"10px","color":"rgba(255,255,255,0.45)",
                                                       "marginTop":"2px","whiteSpace":"nowrap"}),
        ]),
    ], id=f"nav-{tid}", n_clicks=0, style={
        "padding":"9px 16px 9px 20px","cursor":"pointer","display":"flex","alignItems":"center",
        "color": WHITE if is_active else "rgba(255,255,255,0.7)",
        "background": "rgba(0,217,255,0.14)" if is_active else _TRANSP,
        "borderLeft": f"3px solid {PRIMARY}" if is_active else "3px solid transparent",
        "borderRadius":"0 6px 6px 0","marginBottom":"3px","transition":"all 0.15s",
    })

def _nav_group(title):
    return html.Div(title, style={"color":ACCENT,"fontSize":"9px","fontWeight":"800",
                                  "letterSpacing":"1.8px","padding":"15px 20px 6px",
                                  "borderTop":f"1px solid rgba(0,217,255,0.12)"})

# ── Preset Genie questions ────────────────────────────────────────────────
PRESET_QS = [
    "Show total in-store revenue and fuel gallons by state",
    "List all campaigns that ran in Texas in the last 6 months with their uplift %",
    "Rank campaigns by total incremental revenue",
    "Show the top 10 stores by in-store revenue in Texas",
    "Compare average basket size across regions",
]

FOLLOWUP_MAP = {
    PRESET_QS[0]: [
        "Which states have the highest in-store revenue per site?",
        "Show me the states where fuel gallons are up but in-store revenue is flat",
        "List the bottom 5 states by average basket size",
    ],
    PRESET_QS[1]: [
        "Show daily revenue for Texas stores over the last 90 days",
        "Which Texas stores had the highest participation rate in campaigns?",
        "What was the average basket size in Texas during active campaigns vs no campaigns?",
    ],
    PRESET_QS[2]: [
        "Show revenue uplift % for each campaign broken down by region",
        "Which stores saw the highest incremental revenue from the Fill and Refuel campaign?",
        "List campaigns with participation rate above 25%",
    ],
    PRESET_QS[3]: [
        "Show revenue and basket size for all Texas stores sorted by revenue",
        "Which Texas stores are enrolled in active campaigns?",
        "Compare Texas store revenue to national average",
    ],
    PRESET_QS[4]: [
        "Show average basket size by site type — rural vs urban",
        "Which region has the highest average basket size?",
        "List stores with basket size above the national average",
    ],
}

def _get_followups(prompt: str) -> list:
    for k, v in FOLLOWUP_MAP.items():
        if k.lower()[:40] in prompt.lower():
            return v
    return [
        "Show me a breakdown of this data by region",
        "Which stores are outliers in this metric?",
        "List the top 10 results sorted by revenue",
    ]

# ── Chart builders ────────────────────────────────────────────────────────
def _make_revenue_map(df):
    fig = go.Figure()
    if df.empty or "lat" not in df.columns:
        return _L(fig)
    df = df.dropna(subset=["lat","lon"])
    max_rev = df.revenue.max() or 1
    fig.add_trace(go.Scattergeo(
        lat=df.lat, lon=df.lon,
        mode="markers+text",
        text=df.state,
        textposition="top center",
        textfont=dict(color=NEAR_BLACK, size=10),
        customdata=df[["state","revenue","revenue_vs_prior","site_count"]].values,
        marker=dict(
            size=(df.revenue / max_rev * 40 + 8).clip(8, 48),
            color=df.revenue_vs_prior,
            colorscale=[[0, DANGER],[0.5, ACCENT],[1, SUCCESS]],
            cmin=-5, cmax=15,
            colorbar=dict(
                title=dict(text="vs Prior %", font=dict(color=NEAR_BLACK)),
                tickfont=dict(color=NEAR_BLACK),
                len=0.6, x=1.02,
            ),
            line=dict(color=WHITE, width=1),
            opacity=0.85,
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Revenue: $%{customdata[1]:,.0f}<br>"
            "vs Prior: %{customdata[2]:+.1f}%<br>"
            "Sites: %{customdata[3]}<extra></extra>"
        ),
    ))
    fig.update_geos(
        scope="usa", showland=True, landcolor="#DCEFF6",
        showlakes=True, lakecolor="#C5EAF3",
        showcoastlines=True, coastlinecolor=BORDER,
        showsubunits=True, subunitcolor=BORDER,
        bgcolor=_TRANSP,
    )
    return _L(fig, height=350, geo=dict(bgcolor=_TRANSP),
              title=dict(text="Revenue by State (bubble = size, colour = vs prior)",
                         font=dict(color=PRIMARY_DARK, size=13), x=0))

def _make_site_type_chart(df):
    fig = go.Figure(data=[
        go.Bar(name="Revenue ($)", x=df.site_type, y=df.revenue / 1000,
               marker_color=PRIMARY, text=(df.revenue/1000).round(0),
               texttemplate="$%{text:.0f}K", textposition="outside"),
    ])
    return _L(fig, title=dict(text="Revenue by Site Type ($K)",
                               font=dict(color=PRIMARY_DARK, size=13), x=0),
              xaxis_title="", yaxis_title="Revenue ($K)",
              showlegend=False, margin=dict(l=40,r=10,t=40,b=30))

def _make_campaign_kpi_bar(kpi_df):
    metrics = ["Uplift %","Incr. Revenue ($M)","Basket Increase ($)","Participation Rate"]
    fig = go.Figure()
    colors = CHART_COLORS
    for i, row in kpi_df.iterrows():
        vals = [row.get("campaign_uplift_pct",0), row.get("incremental_revenue_m",0),
                row.get("basket_size_increase",0), row.get("participation_rate",0)]
        fig.add_trace(go.Bar(name=row["name"], x=metrics, y=vals,
                              marker_color=colors[i % len(colors)]))
    fig.update_layout(**{**PLOT_LAYOUT,
        "barmode":"group",
        "title": dict(text="Campaign Comparison",font=dict(color=PRIMARY_DARK,size=13),x=0),
        "margin":dict(l=40,r=10,t=40,b=60),
        "showlegend":True,
        "height": 300,
    })
    return fig

def _make_forecast_actual_chart(detail):
    dates = detail["revenue_dates"][:30]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=detail["revenue_forecast"][:30], name="Forecast",
            line=dict(color=MUTED, dash="dash", width=2),
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=detail["revenue_actual"][:30], name="Actual",
        line=dict(color=PRIMARY, width=2.5),
        fill="tonexty", fillcolor=_PRIMARY_15,
    ))
    return _L(fig, title=dict(text="Forecasted vs Actual Revenue ($K/day)",
                               font=dict(color=PRIMARY_DARK,size=13),x=0),
              xaxis_title="", yaxis_title="Revenue ($K)",
              legend=dict(orientation="h", y=1.1))

def _make_basket_pie(basket_df):
    fig = go.Figure(go.Pie(
        labels=basket_df["Category"], values=basket_df["Share %"],
        hole=0.42,
        marker=dict(colors=CHART_COLORS, line=dict(color=WHITE, width=2)),
        textfont=dict(color=NEAR_BLACK, size=11),
    ))
    return _L(fig, title=dict(text="Basket Composition",font=dict(color=PRIMARY_DARK,size=13),x=0),
              showlegend=True, margin=dict(l=20,r=20,t=40,b=20))

def _make_texas_city_chart(city_df):
    city_df = city_df.sort_values("revenue", ascending=True)
    colors = [SUCCESS if v >= 0 else DANGER for v in city_df.revenue_vs_prior]
    fig = go.Figure(go.Bar(
        y=city_df.city, x=city_df.revenue / 1000,
        orientation="h",
        marker_color=PRIMARY,
        text=city_df.revenue_vs_prior.apply(lambda v: f"{v:+.1f}%"),
        textposition="outside",
        textfont=dict(color=NEAR_BLACK, size=10),
        customdata=city_df[["city","revenue","revenue_vs_prior","margin_pct"]].values,
        hovertemplate="<b>%{customdata[0]}</b><br>Revenue: $%{customdata[1]:,.0f}<br>vs Prior: %{customdata[2]:+.1f}%<br>Margin: %{customdata[3]:.1f}%<extra></extra>",
    ))
    return _L(fig, title=dict(text="Revenue by City ($K) — colour indicates vs prior",
                               font=dict(color=PRIMARY_DARK,size=13),x=0),
              xaxis_title="Revenue ($K)", yaxis_title="",
              margin=dict(l=120,r=60,t=40,b=30))

def _make_margin_trend_chart(weekly_df):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=weekly_df.week_label, y=weekly_df.margin_pct,
        name="Margin %", line=dict(color=ACCENT, width=2.5),
        mode="lines+markers", marker=dict(color=ACCENT, size=6),
        fill="tozeroy", fillcolor=_ACCENT_15,
    ))
    fig.add_hline(y=weekly_df.margin_pct.mean(), line_dash="dot",
                  line_color=MUTED, annotation_text="Avg",
                  annotation_font=dict(color=MUTED))
    return _L(fig, title=dict(text="Weekly Margin % — Texas",font=dict(color=PRIMARY_DARK,size=13),x=0),
              xaxis_title="", yaxis_title="Margin %",
              yaxis=dict(range=[0, weekly_df.margin_pct.max() * 1.3],
                         gridcolor=BORDER, zerolinecolor=BORDER,
                         tickfont=dict(color=MUTED), linecolor=BORDER))

def _make_campaign_sim_chart(camp, region, n_sites, part_pct, base):
    avg_basket  = base["region_basket"].get(region, 8.5)
    basket_lift = camp["basket_size_increase"]
    part        = part_pct / 100
    weeks       = [f"W{i}" for i in range(1, 13)]
    ramp        = [min(1.0, (i + 1) / 4) for i in range(12)]
    base_wk     = round(n_sites * 820 * avg_basket * 4.0 / 1000, 1)
    sim_wk      = [round(base_wk * (1 + part * ramp[i] * basket_lift / max(avg_basket, 1)), 1)
                   for i in range(12)]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=weeks, y=[base_wk]*12, name="Baseline",
                              line=dict(color=MUTED, dash="dash", width=2)))
    fig.add_trace(go.Scatter(x=weeks, y=sim_wk, name="With Campaign",
                              line=dict(color=PRIMARY, width=2.5),
                              fill="tonexty", fillcolor=_PRIMARY_15))
    peak_lift = round(sim_wk[-1] - base_wk, 1)
    fig.add_annotation(x="W12", y=sim_wk[-1],
                       text=f"+${peak_lift:.1f}K/wk at peak",
                       showarrow=True, arrowhead=2,
                       font=dict(color=SUCCESS, size=11),
                       arrowcolor=SUCCESS)
    return _L(fig,
              title=dict(text="Projected Weekly Revenue ($K) — Ramp-Up Curve",
                         font=dict(color=PRIMARY_DARK, size=13), x=0),
              yaxis_title="Revenue ($K)",
              legend=dict(orientation="h", y=1.12))


def _make_channel_chart(budget_k, allocs_pct, base):
    channels = list(base["channel_params"].keys())
    reach, convs, rois, budgets_k = [], [], [], []
    for ch, alloc in zip(channels, allocs_pct):
        p       = base["channel_params"][ch]
        ch_bud  = budget_k * 1000 * alloc / 100
        ch_rch  = ch_bud / p["cpr"] if p["cpr"] else 0
        ch_con  = ch_rch * p["cvr"]
        ch_rev  = ch_con * p["basket_lift"] * 8.5
        reach.append(round(ch_rch / 1000, 1))
        convs.append(round(ch_con / 1000, 1))
        rois.append(round(ch_rev / ch_bud, 2) if ch_bud else 0)
        budgets_k.append(round(ch_bud / 1000, 1))
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Reach (000s)", x=channels, y=reach,
                          marker_color=PRIMARY_DARK, yaxis="y1",
                          text=[f"{v:.0f}K" for v in reach], textposition="outside"))
    fig.add_trace(go.Bar(name="Conversions (000s)", x=channels, y=convs,
                          marker_color=PRIMARY, yaxis="y1",
                          text=[f"{v:.1f}K" for v in convs], textposition="outside"))
    fig.add_trace(go.Scatter(name="ROI (×)", x=channels, y=rois,
                              mode="lines+markers", yaxis="y2",
                              line=dict(color=ACCENT, width=2.5),
                              marker=dict(color=ACCENT, size=8, line=dict(color=WHITE, width=1))))
    return _L(fig, barmode="group",
              title=dict(text="Channel Performance — Reach, Conversions & ROI",
                         font=dict(color=PRIMARY_DARK, size=13), x=0),
              yaxis =dict(title="Volume (000s)", gridcolor=BORDER, zerolinecolor=BORDER,
                          tickfont=dict(color=MUTED), linecolor=BORDER),
              yaxis2=dict(title="ROI (×)", overlaying="y", side="right",
                          tickfont=dict(color=ACCENT), showgrid=False,
                          range=[0, max(rois) * 1.5 if rois else 5]),
              margin=dict(l=50, r=60, t=50, b=50), showlegend=True,
              legend=dict(orientation="h", y=-0.18, font=dict(color=NEAR_BLACK)))


def _make_wtp_map(df):
    fig = go.Figure()
    if df.empty:
        return _L(fig)
    max_sites = df.sites.max() or 1
    fig.add_trace(go.Scattergeo(
        lat=df.lat, lon=df.lon,
        mode="markers+text",
        text=df.state,
        textposition="top center",
        textfont=dict(color=NEAR_BLACK, size=10),
        customdata=df[["state","wtp_score","income_index","recommended_price","current_price","sites"]].values,
        marker=dict(
            size=(df.sites / max_sites * 42 + 10).clip(10, 52),
            color=df.wtp_score,
            colorscale=[[0,DANGER],[0.4,WARNING],[0.7,PRIMARY],[1,SUCCESS]],
            cmin=4, cmax=10,
            colorbar=dict(
                title=dict(text="WTP Score", font=dict(color=NEAR_BLACK)),
                tickfont=dict(color=NEAR_BLACK), len=0.6, x=1.02,
            ),
            line=dict(color=WHITE, width=1), opacity=0.88,
        ),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "WTP Score: %{customdata[1]:.1f}/10<br>"
            "Income Index: %{customdata[2]:.2f}<br>"
            "Rec. Price: $%{customdata[3]:.2f}/gal<br>"
            "Current: $%{customdata[4]:.2f}/gal<br>"
            "Sites: %{customdata[5]}<extra></extra>"
        ),
    ))
    fig.update_geos(
        scope="usa", showland=True, landcolor="#DCEFF6",
        showlakes=True, lakecolor="#C5EAF3",
        showcoastlines=True, coastlinecolor=BORDER,
        showsubunits=True, subunitcolor=BORDER,
        bgcolor=_TRANSP,
    )
    return _L(fig, height=360, geo=dict(bgcolor=_TRANSP),
              title=dict(text="ML Predicted WTP Score by State (bubble = site count, colour = WTP)",
                         font=dict(color=PRIMARY_DARK, size=13), x=0))


def _make_price_sensitivity(reg_df):
    regions = reg_df.region.tolist()
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Current Price",    x=regions, y=reg_df.current_price,
                          marker_color=MUTED, text=reg_df.current_price.round(2),
                          texttemplate="$%{text}", textposition="outside"))
    fig.add_trace(go.Bar(name="Recommended Price",x=regions, y=reg_df.recommended_price,
                          marker_color=SUCCESS, text=reg_df.recommended_price.round(2),
                          texttemplate="$%{text}", textposition="outside"))
    fig.add_trace(go.Bar(name="Competitor Price", x=regions, y=reg_df.competitor_price,
                          marker_color=ACCENT, text=reg_df.competitor_price.round(2),
                          texttemplate="$%{text}", textposition="outside"))
    return _L(fig, barmode="group",
              title=dict(text="Price per Gallon — Current vs Recommended vs Competitor",
                         font=dict(color=PRIMARY_DARK, size=13), x=0),
              yaxis=dict(range=[3.0, 5.0], gridcolor=BORDER, zerolinecolor=BORDER,
                         tickfont=dict(color=MUTED), linecolor=BORDER),
              xaxis=dict(gridcolor=BORDER, zerolinecolor=BORDER,
                         tickfont=dict(color=MUTED), linecolor=BORDER),
              margin=dict(l=40, r=10, t=40, b=40), showlegend=True,
              legend=dict(orientation="h", y=-0.18, font=dict(color=NEAR_BLACK)))


def _make_segment_scatter(df):
    colors = [PRIMARY, ACCENT, PRIMARY_DARK, MUTED]
    fig = go.Figure()
    for i, (_, row) in enumerate(df.iterrows()):
        fig.add_trace(go.Scatter(
            x=[row.price_sensitivity], y=[row.wtp_score],
            mode="markers+text",
            name=row.segment,
            text=[row.segment],
            textposition="top center",
            textfont=dict(size=11, color=NEAR_BLACK),
            marker=dict(size=row.share_pct * 1.8, color=colors[i % len(colors)],
                        line=dict(color=WHITE, width=2), opacity=0.85),
            customdata=[[row.share_pct, row.avg_spend]],
            hovertemplate=(
                f"<b>{row.segment}</b><br>"
                "WTP Score: %{y:.1f}/10<br>"
                "Price Sensitivity: %{x:.2f}<br>"
                "Share: %{customdata[0]}%<br>"
                "Avg Spend: $%{customdata[1]}<extra></extra>"
            ),
        ))
    fig.add_annotation(x=0.72, y=5.4, text="← High sensitivity<br>lower WTP",
                       showarrow=False, font=dict(color=MUTED, size=10))
    fig.add_annotation(x=0.22, y=8.9, text="Low sensitivity<br>higher WTP →",
                       showarrow=False, font=dict(color=PRIMARY, size=10))
    return _L(fig,
              title=dict(text="Customer WTP vs Price Sensitivity (bubble = share of volume)",
                         font=dict(color=PRIMARY_DARK, size=13), x=0),
              xaxis=dict(title="Price Sensitivity", range=[0, 0.9],
                         gridcolor=BORDER, zerolinecolor=BORDER,
                         tickfont=dict(color=MUTED), linecolor=BORDER),
              yaxis=dict(title="WTP Score", range=[4, 10.5],
                         gridcolor=BORDER, zerolinecolor=BORDER,
                         tickfont=dict(color=MUTED), linecolor=BORDER),
              showlegend=False, margin=dict(l=50, r=20, t=40, b=50))


def _make_simulator_chart(regions, base_vols, elasticities, base_prices, delta_cents):
    delta = delta_cents / 100
    rev_changes, vol_changes = [], []
    for bv, el, bp in zip(base_vols, elasticities, base_prices):
        demand_chg  = el * (delta / bp)
        new_vol     = bv * (1 + demand_chg)
        base_rev    = bv * bp
        new_rev     = new_vol * (bp + delta)
        rev_changes.append(round((new_rev - base_rev), 3))   # $M/month
        vol_changes.append(round((new_vol - bv), 3))          # M gal
    colors = [SUCCESS if v >= 0 else DANGER for v in rev_changes]
    total  = round(sum(rev_changes), 2)
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=regions, y=rev_changes,
        marker_color=colors,
        text=[f"${v:+.2f}M" for v in rev_changes],
        textposition="outside",
        textfont=dict(color=NEAR_BLACK, size=11),
        customdata=list(zip(vol_changes, rev_changes)),
        hovertemplate="<b>%{x}</b><br>Rev change: $%{customdata[1]:+.2f}M/mo<br>Vol change: %{customdata[0]:+.2f}M gal<extra></extra>",
    ))
    fig.add_annotation(
        x=0.5, y=1.08, xref="paper", yref="paper",
        text=f"Total network impact at +{delta_cents}¢/gal: <b>${total:+.2f}M/month</b>",
        showarrow=False, font=dict(color=PRIMARY_DARK, size=13),
        bgcolor="rgba(255,255,255,0.85)", bordercolor=BORDER, borderwidth=1,
    )
    return _L(fig,
              title=dict(text=f"Projected Monthly Revenue Impact at +{delta_cents}¢/gal Price Adjustment",
                         font=dict(color=PRIMARY_DARK, size=13), x=0),
              yaxis=dict(title="Revenue Change ($M/month)", gridcolor=BORDER,
                         zerolinecolor=BORDER, tickfont=dict(color=MUTED), linecolor=BORDER),
              margin=dict(l=60, r=20, t=60, b=40), showlegend=False)


# ── Loyalty Analytics chart builders ─────────────────────────────────────────

def _make_loyalty_trend_chart(d, view="overall"):
    months = d["months"]
    reg_cy, act_cy = d["reg_cy"], d["act_cy"]
    reg_py, act_py = d["reg_py"], d["act_py"]
    fig = go.Figure()
    if view == "overall":
        fig.add_trace(go.Scatter(x=months, y=reg_py, name="Registrations PY",
                                  line=dict(color=MUTED, dash="dash", width=1.5),
                                  mode="lines+markers", marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=months, y=reg_cy, name="Registrations CY",
                                  line=dict(color=PRIMARY_DARK, width=2.5),
                                  mode="lines+markers", marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=months, y=act_py, name="Activations PY",
                                  line=dict(color=ACCENT_LT, dash="dash", width=1.5),
                                  mode="lines+markers", marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=months, y=act_cy, name="Activations CY",
                                  line=dict(color=PRIMARY, width=2.5),
                                  mode="lines+markers", marker=dict(size=6)))
        ytd = d["ytd_months"]
        fig.add_vrect(x0=months[ytd-1], x1=months[-1],
                      fillcolor="rgba(0,217,255,0.04)", line_width=0,
                      annotation_text="Projected", annotation_position="top right",
                      annotation_font=dict(color=MUTED, size=10))
    else:  # activation rate per site
        act_rate_cy = [round(a/r*100, 1) for a, r in zip(act_cy, reg_cy)]
        act_rate_py = [round(a/r*100, 1) for a, r in zip(act_py, reg_py)]
        fig.add_trace(go.Scatter(x=months, y=act_rate_py, name="Act Rate PY",
                                  line=dict(color=MUTED, dash="dash", width=1.5),
                                  mode="lines+markers", marker=dict(size=5)))
        fig.add_trace(go.Scatter(x=months, y=act_rate_cy, name="Act Rate CY",
                                  line=dict(color=ACCENT, width=2.5),
                                  mode="lines+markers", marker=dict(size=6)))
    return _L(fig,
              title=dict(text="Registrations & Activations — CY vs PY" if view=="overall"
                              else "Activation Rate per Site — CY vs PY",
                         font=dict(color=PRIMARY_DARK, size=13), x=0),
              yaxis=dict(title="Count" if view=="overall" else "Rate (%)",
                         gridcolor=BORDER, zerolinecolor=BORDER,
                         tickfont=dict(color=MUTED), linecolor=BORDER),
              legend=dict(orientation="h", y=1.12, font=dict(color=NEAR_BLACK, size=11)),
              margin=dict(l=50, r=20, t=55, b=40))


def _make_loyalty_region_chart(region_df):
    fig = go.Figure()
    fig.add_trace(go.Bar(name="Registrations CY", x=region_df.region, y=region_df.reg_cy,
                          marker_color=PRIMARY_DARK,
                          text=[f"{v/1000:.1f}K" for v in region_df.reg_cy],
                          textposition="outside"))
    fig.add_trace(go.Bar(name="Activations CY", x=region_df.region, y=region_df.act_cy,
                          marker_color=PRIMARY,
                          text=[f"{v/1000:.1f}K" for v in region_df.act_cy],
                          textposition="outside"))
    fig.add_trace(go.Scatter(name="YoY Reg %", x=region_df.region, y=region_df.reg_yoy,
                              mode="lines+markers", yaxis="y2",
                              line=dict(color=ACCENT, width=2),
                              marker=dict(size=7, color=ACCENT, line=dict(color=WHITE, width=1))))
    return _L(fig, barmode="group",
              title=dict(text="Store Registrations & Activations by Region — CY YTM",
                         font=dict(color=PRIMARY_DARK, size=13), x=0),
              yaxis=dict(title="Count", gridcolor=BORDER, zerolinecolor=BORDER,
                         tickfont=dict(color=MUTED), linecolor=BORDER),
              yaxis2=dict(title="YoY %", overlaying="y", side="right",
                          tickfont=dict(color=ACCENT), showgrid=False,
                          range=[0, max(region_df.reg_yoy) * 2]),
              legend=dict(orientation="h", y=-0.18, font=dict(color=NEAR_BLACK, size=11)),
              margin=dict(l=50, r=60, t=50, b=60))


def _make_pct_activations_chart(d):
    months = d["months"][:d["ytd_months"]]
    pct = [round(a/r*100, 1) for a, r in zip(d["act_cy"][:d["ytd_months"]],
                                               d["reg_cy"][:d["ytd_months"]])]
    colors = [PRIMARY if v >= 60 else ACCENT for v in pct]
    fig = go.Figure(go.Bar(x=months, y=pct, marker_color=colors,
                            text=[f"{v}%" for v in pct], textposition="outside",
                            textfont=dict(color=NEAR_BLACK, size=11)))
    return _L(fig,
              title=dict(text="% Activated of Registrations — CY YTD",
                         font=dict(color=PRIMARY_DARK, size=13), x=0),
              yaxis=dict(title="% Activated", range=[0, 80], gridcolor=BORDER,
                         tickfont=dict(color=MUTED), linecolor=BORDER),
              margin=dict(l=50, r=20, t=50, b=40), showlegend=False)


# ── App ──────────────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    title="Shell Retail Intelligence",
)

SIDEBAR = html.Div([
    html.Div([
        html.Div(
            html.Img(src=_EF_LOGO_SRC, style={"height":"26px","display":"block"}),
            style={"background":ACCENT,"borderRadius":"6px","padding":"6px 12px",
                   "display":"inline-block","marginBottom":"12px",
                   "boxShadow":"0 2px 6px rgba(0,0,0,0.15)"},
        ),
        html.Div(style={"height":"1px","background":"rgba(125,249,255,0.5)","marginBottom":"10px"}),
        html.Div("SHELL RETAIL", style={"color":WHITE,"fontWeight":"700",
                                        "fontSize":"12px","letterSpacing":"1.5px",
                                        "fontFamily":"-apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif"}),
        html.Div("OPERATIONS", style={"color":ACCENT,"fontSize":"9px",
                                        "fontWeight":"700","letterSpacing":"2px","marginTop":"2px"}),
        html.Div([
            html.Span("●", style={"color":SUCCESS,"fontSize":"9px","marginRight":"6px"}),
            html.Span("LIVE DATA" if not _USE_MOCK else "LOCAL PREVIEW",
                      style={"color":"rgba(255,255,255,0.55)","fontSize":"9px","fontWeight":"700",
                             "letterSpacing":"1px"}),
        ], style={"display":"flex","alignItems":"center","marginTop":"14px"}),
    ], style={"padding":"20px 20px 16px","borderBottom":"1px solid rgba(255,255,255,0.15)","marginBottom":"8px"}),
    html.Div(id="sidebar-nav"),
    html.Div(id="sidebar-user", style={"padding":"14px 16px","borderTop":"1px solid rgba(255,255,255,0.15)","marginTop":"8px"}),
], style={
    "width":"260px","minWidth":"260px","background":SIDEBAR_BG,
    "height":"100vh","position":"fixed","top":"0","left":"0",
    "overflowY":"auto","overflowX":"hidden",
    "borderRight":f"2px solid {PRIMARY}","zIndex":"100",
    "display":"flex","flexDirection":"column",
})

FOOTER = html.Div([
    html.Span("LIVE" if not _USE_MOCK else "",
              style={"color":SUCCESS,"fontSize":"11px",
                     "fontWeight":"700","padding":"2px 8px","borderRadius":"4px",
                     "background":"rgba(255,255,255,0.1)"}),
    html.Span("shell.com",
              style={"color":ACCENT,"fontSize":"11px","fontWeight":"700"}),
], style={
    "position":"fixed","bottom":"0","left":"260px","right":"0","height":"36px",
    "background":SECONDARY,"display":"flex","alignItems":"center",
    "justifyContent":"space-between","padding":"0 24px","zIndex":"99",
    "borderTop":f"2px solid {ACCENT}",
})

app.layout = html.Div([
    dcc.Store(id="store-active-tab",     data="tab-overview"),
    dcc.Store(id="store-drill-region",   data=None),
    dcc.Store(id="store-campaign-view",  data="active"),
    dcc.Store(id="store-selected-camps", data=[]),
    dcc.Store(id="store-campaign-detail",data=None),
    dcc.Store(id="store-new-campaigns",  data=[]),
    dcc.Store(id="store-insight-action", data=None),
    dcc.Store(id="store-build-form",     data={}),
    dcc.Interval(id="interval-refresh",  interval=300_000, n_intervals=0),
    SIDEBAR,
    html.Div([
        html.Div(id="main-content", style={"minHeight":"calc(100vh - 36px)"}),
        FOOTER,
    ], style={"marginLeft":"260px","paddingBottom":"36px","background":PAGE_BG}),
], style={"fontFamily":"-apple-system, BlinkMacSystemFont, 'Segoe UI', 'Helvetica Neue', sans-serif","background":PAGE_BG})

# ── Callbacks ────────────────────────────────────────────────────────────────

@app.callback(
    Output("store-active-tab",   "data", allow_duplicate=True),
    Output("store-drill-region", "data", allow_duplicate=True),
    [Input(f"nav-{tid}", "n_clicks") for tid, _, _ in NAV_ITEMS],
    prevent_initial_call=True,
)
def nav_click(*n_clicks_list):
    tid = ctx.triggered_id
    if not tid or not str(tid).startswith("nav-"):
        return dash.no_update, dash.no_update
    tab_id = str(tid)[4:]
    tab_ids = [t for t, _, _ in NAV_ITEMS]
    # Only act on REAL user clicks (n_clicks > 0).
    # When update_nav re-renders nav items it resets n_clicks to 0,
    # which would otherwise trigger this callback spuriously and wipe store-drill-region.
    if tab_id in tab_ids:
        idx = tab_ids.index(tab_id)
        if not n_clicks_list[idx] or n_clicks_list[idx] <= 0:
            return dash.no_update, dash.no_update
    return tab_id, None


@app.callback(
    Output("sidebar-nav", "children"),
    Input("store-active-tab", "data"),
)
def update_nav(active):
    active = active or "tab-overview"
    items = []
    labels = {tid: (label, num) for tid, label, num in NAV_ITEMS}
    for group, tab_ids in NAV_GROUPS:
        items.append(_nav_group(group))
        items.extend(_nav_item(tid, labels[tid][0], labels[tid][1], active) for tid in tab_ids)
    return items


@app.callback(
    Output("offer-decision-output", "children"),
    Input("offer-context-selector", "value"),
)
def update_offer_decision(customer_id):
    offer_ops = bk.get_offer_strategy_data()
    offers = offer_ops["decisioning"]
    offers = offers[offers["customer_id"] == customer_id] if customer_id else offers
    if offers.empty:
        offers = offer_ops["decisioning"].head(3)

    return html.Div([
        html.Div("Ranked candidates", style={"color":MUTED,"fontSize":"11px","fontWeight":"700",
                                             "textTransform":"uppercase","letterSpacing":"0.8px","marginBottom":"8px"}),
        html.Div([
            html.Div([
                html.Div([
                    html.Span(f"#{rank}", style={"color":PRIMARY,"fontWeight":"800","fontSize":"18px","width":"28px"}),
                    html.Div([
                        html.Div(row["offer"], style={"color":NEAR_BLACK,"fontWeight":"700","fontSize":"13px"}),
                        html.Div(f"{row['reason']} · {row['channel']}", style={"color":MUTED,"fontSize":"11px","marginTop":"3px"}),
                    ], style={"flex":"1"}),
                    html.Span(f"{float(row['score']):.0%}", style={"color":ACCENT,"fontWeight":"800","fontSize":"14px"}),
                ], style={"display":"flex","alignItems":"center","gap":"8px"}),
            ], style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderLeft":f"3px solid {PRIMARY}",
                      "borderRadius":"6px","padding":"10px 12px","marginBottom":"6px"})
            for rank, (_, row) in enumerate(offers.sort_values("score", ascending=False).iterrows(), start=1)
        ]),
    ])


@app.callback(
    Output("sidebar-user", "children"),
    Input("interval-refresh", "n_intervals"),
)
def update_user(_):
    return html.Div()


@app.callback(
    Output("main-content", "children"),
    Input("store-active-tab", "data"),
    Input("store-drill-region", "data"),
    Input("store-campaign-view", "data"),
    Input("store-selected-camps", "data"),
    Input("store-campaign-detail", "data"),
    Input("store-new-campaigns", "data"),
    Input("store-insight-action", "data"),
    Input("interval-refresh", "n_intervals"),
)
def route_content(tab, drill, camp_view, sel_camps, camp_detail, new_camps, insight_action, _n):
    tab = tab or "tab-overview"
    print(f"[route] tab={tab} drill={drill}")
    try:
        if tab == "tab-overview":      return render_overview()
        if tab == "tab-regional":      return render_regional(drill)
        if tab == "tab-campaigns":     return render_campaigns(camp_view, sel_camps or [], camp_detail, new_camps or [])
        if tab == "tab-insights":      return render_insights(insight_action)
        if tab == "tab-loyalty":       return render_loyalty()
        if tab == "tab-pricing":       return render_pricing()
        if tab == "tab-whatif":        return render_whatif()
        if tab == "tab-genie":         return render_genie()
        if tab == "tab-shell-project": return render_shell_project()
        if tab == "tab-data-catalog":  return render_data_catalog()
        if tab == "tab-data-freshness": return render_data_freshness()
        return render_overview()
    except Exception as exc:
        import traceback
        tb = traceback.format_exc()
        print(f"[route] ERROR tab={tab} drill={drill}: {tb}")
        return html.Div([
            html.Div(f"Error rendering tab={tab} drill={drill}", style={"fontWeight":"700","color":"red","fontSize":"14px"}),
            html.Pre(tb[:1500], style={"fontSize":"11px","color":"#333","whiteSpace":"pre-wrap"}),
        ], style={"padding":"24px","background":"#FFF5F5","border":"1px solid #FCA5A5","borderRadius":"8px","margin":"16px"})


# Clientside callback — runs in the browser, zero server round-trip, zero DB lookup.
# Extracts state code directly from the Plotly clickData structure.
app.clientside_callback(
    """
    function(clickData) {
        var no_update = window.dash_clientside.no_update;
        if (!clickData || !clickData.points || !clickData.points.length) {
            return [no_update, no_update];
        }
        var pt = clickData.points[0];
        console.log('[map_click] raw point:', JSON.stringify(pt));

        var state = null;

        // 1. customdata[0] — embedded in figure at render time
        if (pt.customdata && pt.customdata.length > 0) {
            var c = String(pt.customdata[0]).trim().toUpperCase();
            if (c.length === 2 && /^[A-Z]+$/.test(c)) { state = c; }
        }

        // 2. text — the label shown on the marker (df.state)
        if (!state && pt.text) {
            var t = String(pt.text).trim().toUpperCase();
            if (t.length === 2 && /^[A-Z]+$/.test(t)) { state = t; }
        }

        // 3. pointNumber → hardcoded state list (same order as mock data)
        if (!state && pt.pointNumber !== undefined) {
            var STATES = ['TX','CA','FL','GA','IL','OH','IN','MI','WI','NY',
                          'PA','MA','NJ','LA','OK','AZ','CO','WA','TN'];
            if (pt.pointNumber >= 0 && pt.pointNumber < STATES.length) {
                state = STATES[pt.pointNumber];
            }
        }

        if (state) {
            console.log('[map_click] resolved state=' + state);
            return [state, 'tab-regional'];
        }
        console.log('[map_click] UNRESOLVED:', JSON.stringify(pt));
        return [no_update, no_update];
    }
    """,
    Output("store-drill-region", "data", allow_duplicate=True),
    Output("store-active-tab",   "data", allow_duplicate=True),
    Input("map-overview", "clickData"),
    prevent_initial_call=True,
)


@app.callback(
    Output("store-drill-region", "data", allow_duplicate=True),
    Output("store-active-tab",   "data", allow_duplicate=True),
    Input("state-selector-dropdown", "value"),
    prevent_initial_call=True,
)
def drill_from_dropdown(state):
    if not state:
        return dash.no_update, dash.no_update
    return state, "tab-regional"


@app.callback(
    Output("store-drill-region",    "data", allow_duplicate=True),
    Output("store-campaign-view",   "data"),
    Output("store-campaign-detail", "data", allow_duplicate=True),
    Output("store-insight-action",  "data", allow_duplicate=True),
    Output("store-new-campaigns",   "data"),
    Output("store-active-tab",      "data", allow_duplicate=True),
    Input({"type":"btn-nav","index":ALL}, "n_clicks"),
    State("store-build-form", "data"),
    State("store-new-campaigns", "data"),
    prevent_initial_call=True,
)
def handle_nav_btns(n_clicks, form_data, existing):
    tid = ctx.triggered_id
    nu = dash.no_update
    if not isinstance(tid, dict) or not any(n for n in n_clicks if n):
        return nu, nu, nu, nu, nu, nu
    idx = tid.get("index", "")
    if idx == "drill-back":    return None,       nu,         nu,   nu,   nu, nu
    if idx == "camp-back":     return nu,         nu,         None, nu,   nu, nu
    if idx in ("cancel", "cancel-form"): return nu, nu, nu, None, nu, nu
    if idx == "camp-active":   return nu,         "active",   nu,   nu,   nu, nu
    if idx == "camp-historic": return nu,         "historic", nu,   nu,   nu, nu
    if idx == "submit-camp":
        today = date.today()
        fd = form_data or {}
        channels = fd.get("channels") or []
        new = {
            "campaign_id":           f"NEW{len(existing or [])+1:03d}",
            "name":                  fd.get("name") or "New Campaign",
            "target_region":         fd.get("region") or "all",
            "target_state":          "all",
            "channels":              ", ".join(channels if isinstance(channels, list) else [channels]),
            "status":                "Active",
            "start_date":            fd.get("start") or str(today),
            "end_date":              fd.get("end") or str(today + timedelta(days=90)),
            "campaign_uplift_pct":   0.0,
            "incremental_revenue_m": 0.0,
            "basket_size_increase":  0.0,
            "participation_rate":    0.0,
            "_new": True,
        }
        return nu, "active", nu, None, (existing or []) + [new], "tab-campaigns"
    return nu, nu, nu, nu, nu, nu


@app.callback(
    Output("store-insight-action", "data", allow_duplicate=True),
    Input({"type":"btn-insight","index":ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def insight_open(n_clicks):
    tid = ctx.triggered_id
    if isinstance(tid, dict) and tid.get("type") == "btn-insight" and any(n for n in n_clicks if n):
        return tid["index"]
    return dash.no_update


@app.callback(
    Output("store-campaign-detail", "data", allow_duplicate=True),
    Input({"type":"btn-camp-detail","index":ALL}, "n_clicks"),
    prevent_initial_call=True,
)
def camp_detail_select(n_clicks):
    tid = ctx.triggered_id
    if isinstance(tid, dict) and tid.get("type") == "btn-camp-detail" and any(n for n in n_clicks if n):
        return tid["index"]
    return dash.no_update


@app.callback(
    Output("store-selected-camps", "data"),
    Input({"type":"checklist","index":ALL}, "value"),
    prevent_initial_call=True,
)
def update_selected(vals_list):
    return (vals_list[0] or []) if vals_list else []


@app.callback(
    Output("store-build-form", "data"),
    Input({"type":"build-field","index":ALL}, "value"),
    State({"type":"build-field","index":ALL}, "id"),
    prevent_initial_call=True,
)
def update_build_form(values, ids):
    if not values or not ids:
        return {}
    return {id_["index"]: val for id_, val in zip(ids, values)}



@app.callback(
    Output({"type":"whatif-out","index":"camp-kpis"},  "children"),
    Output({"type":"whatif-out","index":"camp-chart"}, "figure"),
    Input({"type":"whatif-ctrl","index":"campaign"},     "value"),
    Input({"type":"whatif-ctrl","index":"region"},       "value"),
    Input({"type":"whatif-ctrl","index":"sites"},        "value"),
    Input({"type":"whatif-ctrl","index":"participation"},"value"),
    prevent_initial_call=True,
)
def update_campaign_sim(camp_id, region, n_sites, part_pct):
    base = bk.get_whatif_base_data()
    camps = {c["campaign_id"]: c for c in base["campaigns"]}
    camp  = camps.get(camp_id, base["campaigns"][0])
    region    = region    or "South"
    n_sites   = n_sites   or 200
    part_pct  = part_pct  or 25

    part        = part_pct / 100
    avg_basket  = base["region_basket"].get(region, 8.5)
    basket_lift = camp["basket_size_increase"]
    customers   = int(n_sites * 820 * part)
    incr_rev_m  = round(customers * 4.0 * basket_lift / 1e6, 2)
    uplift_pct  = round(camp["campaign_uplift_pct"] * (part / max(camp["participation_rate"], 0.01)) * 0.85, 1)
    est_cost_k  = round(n_sites * 1.2, 0)
    roi         = round(incr_rev_m * 1e6 / (est_cost_k * 1000), 1) if est_cost_k else 0

    kpis = _row(
        _kpi("Customers Reached", f"{customers:,}",         color=PRIMARY),
        _kpi("Incremental Revenue", f"+${incr_rev_m:.2f}M", color=SUCCESS),
        _kpi("Projected Uplift",  f"{uplift_pct:+.1f}%",    color=PRIMARY_DARK),
        _kpi("Est. Campaign Cost", f"${est_cost_k:,.0f}K",  color=ACCENT),
        _kpi("ROI",               f"{roi:.1f}×",            color=PRIMARY),
    )
    chart = _make_campaign_sim_chart(camp, region, n_sites, part_pct, base)
    return kpis, chart


@app.callback(
    Output({"type":"whatif-out","index":"channel-chart"}, "figure"),
    Input({"type":"whatif-budget","index":"0"}, "value"),
    Input({"type":"whatif-mix","index":"0"},    "value"),
    prevent_initial_call=True,
)
def update_channel_opt(budget_k, mix_name):
    base     = bk.get_whatif_base_data()
    budget_k = budget_k or 250
    mix_name = mix_name or "Balanced"
    allocs   = base["channel_mixes"].get(mix_name, [25,20,20,15,15,5])
    return _make_channel_chart(budget_k, allocs, base)


@app.callback(
    Output({"type":"pricing-chart","index":"sim"}, "figure"),
    Input({"type":"pricing-slider","index":"0"}, "value"),
    prevent_initial_call=True,
)
def update_pricing_sim(delta_cents):
    delta_cents = delta_cents or 5
    d = bk.get_pricing_data()
    return _make_simulator_chart(
        d["sim_regions"], d["sim_base_volumes"],
        d["sim_elasticities"], d["sim_base_prices"], delta_cents
    )


@app.callback(
    Output({"type":"genie-out","index":ALL}, "children"),
    Output({"type":"genie-in","index":ALL}, "value"),
    Input({"type":"genie-btn","index":ALL}, "n_clicks"),
    Input({"type":"genie-preset","index":ALL}, "n_clicks"),
    Input({"type":"genie-followup","index":ALL}, "n_clicks"),
    State({"type":"genie-in","index":ALL}, "value"),
    State({"type":"genie-out","index":ALL}, "children"),
    State({"type":"genie-followup","index":ALL}, "children"),
    prevent_initial_call=True,
)
def genie_query(btn_clicks, preset_clicks, follow_clicks, input_vals, output_vals, follow_labels):
    tid = ctx.triggered_id
    prompt = (input_vals[0] if input_vals else None) or ""
    history = (output_vals[0] if output_vals else None) or []
    if not isinstance(history, list):
        history = []

    if isinstance(tid, dict):
        t = tid.get("type")
        if t == "genie-preset":
            prompt = PRESET_QS[tid["index"]]
        elif t == "genie-followup":
            i = tid["index"]
            if follow_labels and i < len(follow_labels):
                prompt = follow_labels[i]
        elif t != "genie-btn":
            return [dash.no_update], [dash.no_update]

    if not prompt:
        return [dash.no_update], [dash.no_update]

    resp = ask_genie(prompt)

    kids = [html.Div(f"▶  {prompt}", style={"color":PRIMARY,"fontWeight":"600","fontSize":"13px",
                                               "marginBottom":"8px","fontStyle":"italic"})]
    if "error" in resp:
        kids.append(html.Div(resp["error"], style={"color":DANGER,"fontSize":"12px"}))
    else:
        if resp.get("text"):
            kids.append(html.Div(resp["text"], style={"color":NEAR_BLACK,"fontSize":"13px","lineHeight":"1.6","marginBottom":"8px"}))
        if resp.get("sql"):
            kids.append(html.Details([
                html.Summary("Show SQL", style={"color":MUTED,"fontSize":"11px","cursor":"pointer"}),
                html.Pre(resp["sql"], style={"color":PRIMARY,"fontSize":"11px","background":"rgba(0,217,255,0.10)",
                                              "padding":"8px","borderRadius":"4px","overflow":"auto","margin":"6px 0"}),
            ]))
        df = resp.get("dataframe")
        if df is not None and not df.empty:
            kids.append(html.Div(f"{len(df)} rows returned", style={"color":SUCCESS,"fontSize":"11px","fontWeight":"600","margin":"6px 0"}))
            kids.append(_table(df.head(50), "genie-result"))
        else:
            kids.append(html.Div("No tabular results for this query.", style={"color":MUTED,"fontSize":"12px"}))

    fups = _get_followups(prompt)
    kids.append(html.Div("Suggested follow-ups:", style={"color":MUTED,"fontSize":"11px","marginTop":"14px","marginBottom":"6px"}))
    kids.append(html.Div([
        html.Button(q, id={"type":"genie-followup","index":i}, n_clicks=0, style={
            "background":_PRIMARY_15,"border":f"1px solid {_PRIMARY_30}","color":PRIMARY,
            "borderRadius":"4px","padding":"5px 10px","fontSize":"11px",
            "cursor":"pointer","margin":"3px","fontFamily":"Arial, sans-serif",
        }) for i, q in enumerate(fups)
    ]))

    card = _card(*kids, style={"marginBottom":"12px","borderLeft":f"3px solid {PRIMARY}"})
    return [[card] + history], [""]


# ── Tab renderers ─────────────────────────────────────────────────────────

def render_overview():
    kpis    = bk.get_kpis()
    offer_ops = bk.get_offer_strategy_data()
    reg     = bk.get_regional_summary()
    stype   = bk.get_site_type_breakdown()
    top, bt = bk.get_top_bottom_stores()
    insights = bk.get_insights()

    rev_delta = kpis["rev_vs_prior"]
    fuel_delta = kpis["fuel_vs_prior"]
    rev_color = SUCCESS if rev_delta >= 0 else DANGER
    fuel_color = SUCCESS if fuel_delta >= 0 else DANGER

    return html.Div([
        _page_header("Marketing Analytics Overview",
                     f"{kpis['total_sites']:,} sites monitored · Last 90 days"),

           # KPI Row — CY YTM vs PY YTM style (matching client sample dashboards)
           _row(
              _kpi("In-Store Revenue CY YTM",
                  f"${kpis['total_revenue_m']:.1f}M",
                  sub=f"{rev_delta:+.1f}% vs PY YTM",
                  color=PRIMARY),
              _kpi("Avg Basket Size",
                  f"${kpis['basket_size']:.2f}",
                  sub=f"{kpis['basket_vs_prior']:+.1f}% vs PY",
                  color=PRIMARY_DARK),
              _kpi("Loyalty Activations CY",
                  f"{kpis.get('loyalty_activations_k', 497)}K",
                  sub=f"+{kpis.get('loyalty_act_yoy', 57.6):.1f}% vs PY YTM",
                  color=PRIMARY),
              _kpi("Loyalty Registrations CY",
                  f"{kpis.get('loyalty_reg_k', 774)}K",
                  sub=f"+{kpis.get('loyalty_reg_yoy', 64.5):.1f}% vs PY YTM",
                  color=PRIMARY_DARK),
              _kpi("Campaign Uplift",
                  f"{kpis['campaign_uplift']:+.1f}%",
                  sub=f"{kpis['active_campaigns']} active campaigns",
                  color=ACCENT),
           ),

        _section_title("Fuel-to-Store Conversion Pipeline"),
        _card(
            _table(offer_ops["pipeline"], "conversion-pipeline", max_rows=4),
            style={"borderTop":f"3px solid {PRIMARY}"},
        ),

        _section_title("Next Best Offer Decisioning"),
        _row(
            _G([
                html.Div("Preview a ranked offer list for a customer context", style={"color":MUTED,"fontSize":"12px","marginBottom":"8px"}),
                dcc.Dropdown(
                    id="offer-context-selector",
                    options=[
                        {"label":"CUST-1001 · Morning commuter", "value":"CUST-1001"},
                        {"label":"CUST-2048 · Afternoon traveler", "value":"CUST-2048"},
                    ],
                    value="CUST-1001", clearable=False, style={"fontSize":"12px"},
                ),
            ], flex=1, min_w="260px"),
            _G([html.Div(id="offer-decision-output")], flex=2, min_w="420px"),
        ),

        # Fuel context note
        html.Div([
            html.Span("Insight: ", style={"fontWeight":"700","color":PRIMARY_DARK}),
            html.Span(f"Fuel gallons {fuel_delta:+.1f}% vs prior while in-store revenue {rev_delta:+.1f}% — "
                      "customers buying in-store more but fuelling elsewhere. ",
                      style={"color":NEAR_BLACK}),
            html.Span("Click any state on the map to drill in.", style={"color":PRIMARY,"fontWeight":"600"}),
        ], style={"background":"#EAF8FC","border":f"1px solid {BORDER}","borderRadius":"8px",
                   "padding":"10px 16px","marginBottom":"16px","fontSize":"12px"}),

        # Map + Site type
        _row(
            _G([
                _row(
                    html.Span("Revenue by State", style={"fontWeight":"700","color":PRIMARY_DARK,
                                                          "fontSize":"13px","flex":"1"}),
                    dcc.Dropdown(
                        id="state-selector-dropdown",
                        options=[{"label":f"{v} ({k})","value":k}
                                 for k,v in sorted(_STATE_NAMES.items(), key=lambda x: x[1])],
                        placeholder="Select a state to drill in...",
                        clearable=True,
                        value=None,
                        style={"width":"220px","fontSize":"12px"},
                    ),
                    gap="12px", mb="8px",
                ),
                dcc.Graph(id="map-overview",
                          figure=_make_revenue_map(reg),
                          config={"displayModeBar":False},
                          style={"height":"350px"}),
            ], flex=3, min_w="360px"),
            _G([
                _section_title("Site Type Performance"),
                _chart(_make_site_type_chart(stype), height=200),
                _row(
                    _kpi("Active Campaigns", kpis["active_campaigns"], "campaigns", color=PRIMARY),
                    _kpi("Total Sites", f"{kpis['total_sites']:,}", "monitored", color=PRIMARY_DARK),
                    gap="8px",
                ),
            ], flex=1, min_w="220px"),
        ),

        # Top / Bottom stores
        _row(
            _G([_section_title("Top 5 Stores"), _table(top, "top5")], flex=1, min_w="300px"),
            _G([_section_title("Bottom 5 Stores"), _table(bt, "bot5")], flex=1, min_w="300px"),
        ),

        # Insights
        _section_title("AI-Driven Insights & Recommended Actions"),
        _row(*[_insight_card_sm(ins) for ins in insights]),
    ], style={"padding":"24px"})


def _insight_card_sm(ins):
    urg_color = _urgency_color(ins["urgency"])
    return html.Div([
        _row(
            html.Span(ins["title"], style={"color":PRIMARY_DARK,"fontWeight":"700","fontSize":"14px","flex":"1"}),
            _badge(ins["urgency"], urg_color, f"rgba(125,249,255,0.12)" if ins["urgency"]=="High" else _PRIMARY_15),
        gap="8px", mb="8px"),
        html.Div(ins["detail"], style={"color":NEAR_BLACK,"fontSize":"12px","lineHeight":"1.6","marginBottom":"10px"}),
        _row(
            html.Span(ins["metric"], style={"color":PRIMARY,"fontWeight":"700","fontSize":"12px"}),
            _btn("Build Campaign",
                 {"type":"btn-insight","index":ins["id"]},
                 color=PRIMARY_DARK, small=True),
        gap="8px", mb="0"),
    ], style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderLeft":f"3px solid {urg_color}",
               "borderRadius":"8px","padding":"16px","flex":"1","minWidth":"280px"})


def render_regional(drill_region=None):
    if drill_region:
        return _render_state_detail(drill_region)
    return _render_national_regional()


def _render_national_regional():
    reg = bk.get_regional_summary()
    offer_ops = bk.get_offer_strategy_data()
    return html.Div([
        _page_header("Regional Drill-Down", "Select a state from the dropdown or click a map bubble"),

        _card(
            _section_title("Regional Offer Readiness"),
            _table(offer_ops["visibility"], "regional-readiness", max_rows=10),
        ),

        # State selector + map
        _row(
            html.Span("Revenue by State", style={"fontWeight":"700","color":PRIMARY_DARK,"fontSize":"13px","flex":"1"}),
            dcc.Dropdown(
                id="state-selector-dropdown",
                options=[{"label":f"{v} ({k})","value":k}
                         for k,v in sorted(_STATE_NAMES.items(), key=lambda x: x[1])],
                placeholder="Select a state to drill in...",
                clearable=True, value=None,
                style={"width":"220px","fontSize":"12px"},
            ),
            gap="12px", mb="8px",
        ),
        dcc.Graph(id="map-overview",
                  figure=_make_revenue_map(reg),
                  config={"displayModeBar":False},
                  style={"height":"400px","marginBottom":"16px"}),

        # Regional summary table
        _section_title("Regional Summary"),
        _table(reg[["region","state","site_count","revenue","revenue_vs_prior","avg_basket"]].rename(columns={
            "region":"Region","state":"State","site_count":"Sites",
            "revenue":"Revenue ($)","revenue_vs_prior":"vs Prior %","avg_basket":"Avg Basket ($)",
        }), "regional"),
    ], style={"padding":"24px"})


_STATE_NAMES = {
    "TX":"Texas","CA":"California","FL":"Florida","GA":"Georgia","IL":"Illinois",
    "OH":"Ohio","IN":"Indiana","MI":"Michigan","WI":"Wisconsin","NY":"New York",
    "PA":"Pennsylvania","MA":"Massachusetts","NJ":"New Jersey","LA":"Louisiana",
    "OK":"Oklahoma","AZ":"Arizona","CO":"Colorado","WA":"Washington","TN":"Tennessee",
}

def _render_state_detail(state: str):
    if state == "TX":
        detail = bk.get_texas_detail()
        return _render_texas(detail)

    reg       = bk.get_regional_summary()
    row       = reg[reg.state == state]
    state_name = _STATE_NAMES.get(state, state)

    if row.empty:
        return html.Div([
            _row(_btn("← Back", {"type":"btn-nav","index":"drill-back"}, color=MUTED, small=True),
                 gap="8px", mb="16px"),
            _page_header(f"{state_name} Detail"),
            html.Div("No data available for this state.", style={"color":MUTED,"fontSize":"13px"}),
        ], style={"padding":"24px"})

    rev        = float(row["revenue"].iloc[0])
    vp         = float(row["revenue_vs_prior"].iloc[0])
    gal        = float(row["fuel_gallons"].iloc[0])
    basket     = float(row["avg_basket"].iloc[0])
    n_sites    = int(row["site_count"].iloc[0])
    region     = str(row["region"].iloc[0])
    vp_color   = SUCCESS if vp >= 0 else DANGER

    # Pull site-level data for this state
    sites_df   = bk.get_sites()
    state_sites = sites_df[sites_df.state == state]
    top_bottom  = bk.get_top_bottom_stores()
    top_df, bt_df = top_bottom
    state_top  = top_df[top_df["State"] == state] if not top_df.empty else top_df.head(0)
    state_bt   = bt_df[bt_df["State"]  == state] if not bt_df.empty  else bt_df.head(0)

    # Pull campaigns active in this region
    all_camps  = bk.get_active_campaigns()
    reg_camps  = all_camps[
        (all_camps.target_region.str.lower() == region.lower()) |
        (all_camps.target_region.str.lower() == "all")
    ]

    return html.Div([
        _row(
            _btn("← Back to National View", {"type":"btn-nav","index":"drill-back"},
                 color=MUTED, small=True),
            gap="8px", mb="16px",
        ),
        _page_header(f"{state_name} ({state}) — {region} Region",
                     f"{n_sites} sites · 90-day performance"),

        # KPI row
        _row(
            _kpi("In-Store Revenue",  f"${rev/1_000:.1f}K",  sub=f"{vp:+.1f}% vs prior", color=PRIMARY),
            _kpi("vs Prior Period",   f"{vp:+.1f}%",          sub="90-day rolling",         color=vp_color),
            _kpi("Fuel Gallons",      f"{gal/1_000:.1f}K",    sub="last 90 days",           color=MUTED),
            _kpi("Avg Basket Size",   f"${basket:.2f}",        sub="per transaction",         color=PRIMARY_DARK),
            _kpi("Active Sites",      f"{n_sites}",            sub=f"{region} region",        color=ACCENT),
        ),

        # Site map + active campaigns
        _row(
            _G([
                _section_title(f"Site Locations — {state_name}"),
                _card(html.Div(
                    f"{n_sites} Shell retail sites operating in {state_name}. "
                    f"{len(state_sites[state_sites.site_type=='urban']) if not state_sites.empty else 0} urban · "
                    f"{len(state_sites[state_sites.site_type=='suburban']) if not state_sites.empty else 0} suburban · "
                    f"{len(state_sites[state_sites.site_type=='rural']) if not state_sites.empty else 0} rural.",
                    style={"color":NEAR_BLACK,"fontSize":"13px","lineHeight":"1.7","padding":"8px 0"}
                )),
                _section_title("Active Campaigns in Region"),
                _card(*[
                    _row(
                        html.Span(c["name"], style={"fontWeight":"600","color":PRIMARY_DARK,"fontSize":"13px","flex":"1"}),
                        _badge(c.get("channels","—"), PRIMARY),
                        gap="8px", mb="0",
                    ) for _, c in reg_camps.iterrows()
                ] or [html.Div("No active campaigns in this region.",
                               style={"color":MUTED,"fontSize":"12px"})]),
            ], flex=1, min_w="280px"),

            _G([
                _section_title("Top Stores in State"),
                _table(state_top if not state_top.empty else top_df.head(3), f"top-{state}"),
                _section_title("Stores Needing Attention"),
                _table(state_bt  if not state_bt.empty  else bt_df.head(3),  f"bt-{state}"),
            ], flex=2, min_w="360px"),
        ),

    ], style={"padding":"24px"})


def _render_texas(detail):
    return html.Div([
        _row(
            _btn("← Back to National View", {"type":"btn-nav","index":"drill-back"}, color=MUTED, small=True),
            gap="8px", mb="16px",
        ),
        _page_header("Texas Detail View",
                     f"${detail['revenue_total_m']:.1f}M revenue · {detail['fuel_gallons_m']:.1f}M gallons"),

        # KPI strip
        _row(
            _kpi("TX In-Store Revenue", f"${detail['revenue_total_m']:.1f}M",
                 sub=f"{detail['rev_vs_prior']:+.1f}% vs prior", color=PRIMARY),
            _kpi("Fuel Gallons", f"{detail['fuel_gallons_m']:.1f}M",
                 sub=f"{detail['fuel_vs_prior']:+.1f}% vs prior", color=MUTED),
            _kpi("Avg Basket Size", f"${detail['avg_basket']:.2f}", color=PRIMARY_DARK),
            _kpi("Margin %", f"{detail['margin_pct']:.1f}%", color=ACCENT),
            _kpi("Campaign Lift", f"{detail['campaign_lift']:+.1f}%",
                 sub="since Texas Summer Drive", color=SUCCESS),
        ),

        # City revenue + margin trend
        _row(
            _G([_section_title("Revenue by City ($K)"),
                _chart(_make_texas_city_chart(detail["city_revenue"]), height=280)], flex=2, min_w="320px"),
            _G([_section_title("Weekly Margin Trend"),
                _chart(_make_margin_trend_chart(detail["weekly_margin"]), height=280)], flex=1, min_w="240px"),
        ),

        # Top products + behavior
        _row(
            _G([
                _section_title("Top Retail Products"),
                _table(detail["top_products"], "tx-products"),
            ], flex=1, min_w="280px"),
            _G([
                _section_title("Customer Behaviour Metrics"),
                _card(
                    _row(
                        _kpi("Avg Visits/Customer", detail["avg_txns_per_site_day"], "per site/day", color=PRIMARY),
                        _kpi("Avg Basket Size", f"${detail['avg_basket']:.2f}", color=PRIMARY_DARK),
                        gap="8px", mb="0",
                    ),
                    style={"padding":"0","border":"none","marginBottom":"0"},
                ),
            ], flex=1, min_w="240px"),
        ),

        # Before / After campaign
        _section_title("What's Changed: Before vs After Texas Summer Drive"),
        _card(
            _row(
                _kpi("Pre-Campaign Daily Rev",
                     f"${detail['pre_campaign_daily_rev']:,.2f}",
                     sub="avg daily (before campaign)", color=MUTED),
                _kpi("Post-Campaign Daily Rev",
                     f"${detail['post_campaign_daily_rev']:,.2f}",
                     sub="avg daily (since campaign)", color=SUCCESS),
                _kpi("Campaign Lift",
                     f"{detail['campaign_lift']:+.1f}%",
                     sub="incremental uplift", color=PRIMARY),
                gap="12px", mb="0",
            ),
        ),

        # Anomalies / Insights
        _section_title("Anomalies & Recommended Actions"),
        html.Div([
            html.Div([
                html.Div(title, style={"color":PRIMARY_DARK,"fontWeight":"700","fontSize":"14px","marginBottom":"6px"}),
                html.Div(detail_txt, style={"color":NEAR_BLACK,"fontSize":"12px","lineHeight":"1.6","marginBottom":"8px"}),
                html.Div(f"Recommended action: {action}", style={"color":PRIMARY,"fontWeight":"600","fontSize":"12px"}),
            ], style={"background":CARD_BG,"border":f"1px solid {BORDER}",
                       "borderLeft":f"3px solid {ACCENT}","borderRadius":"8px",
                       "padding":"16px","flex":"1","minWidth":"280px"})
            for title, detail_txt, action in detail["anomalies"]
        ], style={"display":"flex","gap":"16px","flexWrap":"wrap"}),
    ], style={"padding":"24px"})


def render_campaigns(view, sel_camps, camp_detail, new_camps):
    import pandas as pd
    active_df   = bk.get_active_campaigns()
    historic_df = bk.get_historic_campaigns()
    offer_ops = bk.get_offer_strategy_data()

    if new_camps:
        new_df    = pd.DataFrame(new_camps)
        active_df = pd.concat([active_df, new_df], ignore_index=True)

    current_df = historic_df if view == "historic" else active_df
    all_ids    = current_df.campaign_id.tolist()

    if not sel_camps:
        sel_camps = all_ids

    sel_camps = [c for c in sel_camps if c in all_ids] or all_ids

    camp_kpis = bk.get_campaign_kpis(sel_camps)

    # If viewing detail for a single campaign
    if camp_detail and camp_detail in bk.get_all_campaigns().campaign_id.tolist():
        return _render_campaign_detail(camp_detail)

    # Comparison view when 2+ selected
    show_comparison = len(sel_camps) >= 2

    return html.Div([
        _page_header("Campaign Monitor"),

        _card(
            _section_title("Offer Mechanics in Market"),
            html.Div("Personalized offers, trigger-based moments, bundles, fuel-linked rewards, and clear visibility are managed as one promotion system.",
                     style={"color":MUTED,"fontSize":"12px","lineHeight":"1.6","marginBottom":"10px"}),
            _table(offer_ops["triggers"], "offer-triggers", max_rows=4),
            html.Div(style={"height":"12px"}),
            _section_title("Bundle Affinity & POS Prompts"),
            _table(offer_ops["bundles"], "bundle-affinity", max_rows=5),
        ),

        # Toggle
        _row(
            html.Div([
                 _btn("Active Campaigns", {"type":"btn-nav","index":"camp-active"},
                     color=PRIMARY if view=="active" else MUTED, small=True),
                 _btn("Historic Campaigns", {"type":"btn-nav","index":"camp-historic"},
                     color=PRIMARY if view=="historic" else MUTED, small=True),
            ], style={"display":"flex","gap":"8px"}),
        gap="8px", mb="16px"),

        # Dynamic KPI row
        _section_title(f"Performance Summary — {len(sel_camps)} campaign{'s' if len(sel_camps)!=1 else ''} selected"),
        _row(
            _kpi("Avg Campaign Uplift", f"{camp_kpis['avg_uplift']:+.1f}%", color=PRIMARY),
            _kpi("Incremental Revenue", f"${camp_kpis['total_incr_rev_m']:.1f}M", color=PRIMARY_DARK),
            _kpi("Avg Basket Increase", f"${camp_kpis['avg_basket_increase']:.2f}", color=ACCENT),
            _kpi("Avg Participation Rate", f"{camp_kpis['avg_participation']:.0%}", color=PRIMARY),
            _kpi("Campaigns", camp_kpis["campaign_count"], "", color=PRIMARY_DARK),
        ),

        # Campaign selection checklist
        _section_title("Select Campaigns to Compare"),
        _card(
            html.Div([
                dcc.Checklist(
                    id={"type":"checklist","index":"campaigns"},
                    options=[{"label": f"  {r.name}  ({r.status})", "value": r.campaign_id}
                             for _, r in current_df.iterrows()],
                    value=sel_camps,
                    inline=True,
                    labelStyle={"marginRight":"20px","fontSize":"13px","color":NEAR_BLACK,
                                "cursor":"pointer","display":"inline-flex","alignItems":"center",
                                "gap":"4px"},
                    inputStyle={"accentColor":PRIMARY,"cursor":"pointer"},
                ),
            ]),
            html.Div("Select 1 campaign to view detail · 2+ campaigns to compare side-by-side",
                     style={"color":MUTED,"fontSize":"11px","marginTop":"8px"}),
        ),

        # Comparison chart
        html.Div([
            _section_title("Side-by-Side Campaign Comparison"),
            _chart(_make_campaign_kpi_bar(
                bk.get_campaign_comparison(sel_camps)
            ), height=300),
        ]) if show_comparison else html.Div(),

        # Campaign table with detail buttons
        _section_title("Campaign Details"),
        html.Div([
            html.Div([
                html.Div([
                    html.Div([
                        html.Span(r["name"], style={"fontWeight":"700","fontSize":"13px","color":PRIMARY_DARK}),
                        _badge(r.status, color=PRIMARY if r.status=="Active" else MUTED),
                    ], style={"display":"flex","gap":"8px","alignItems":"center","marginBottom":"6px"}),
                    html.Div(f"Region: {r.target_region} · Channels: {r.channels}",
                             style={"color":MUTED,"fontSize":"11px","marginBottom":"8px"}),
                    _row(
                        html.Span(f"Uplift: {r.campaign_uplift_pct:+.1f}%",
                                  style={"color":PRIMARY,"fontWeight":"700","fontSize":"12px"}),
                        html.Span(f"Incr. Rev: ${r.incremental_revenue_m:.1f}M",
                                  style={"color":PRIMARY_DARK,"fontWeight":"600","fontSize":"12px"}),
                        html.Span(f"Participation: {r.participation_rate:.0%}",
                                  style={"color":MUTED,"fontSize":"12px"}),
                        gap="16px", mb="8px",
                    ),
                    _btn("View Campaign Detail",
                         {"type":"btn-camp-detail","index":r.campaign_id},
                         color=PRIMARY_DARK, small=True),
                ], style={"flex":"1"}),
            ], style={"background":CARD_BG,"border":f"1px solid {BORDER}",
                       "borderLeft":f"3px solid {PRIMARY}","borderRadius":"8px",
                       "padding":"16px","marginBottom":"8px"})
            for _, r in current_df.iterrows()
        ]),
    ], style={"padding":"24px"})


def _render_campaign_detail(campaign_id):
    detail = bk.get_campaign_detail(campaign_id)
    camp   = detail["campaign"]

    return html.Div([
        _row(
            _btn("← Back to Campaigns", {"type":"btn-nav","index":"camp-back"}, color=MUTED, small=True),
            gap="8px", mb="16px",
        ),
        _page_header(camp["name"],
                     f"{camp['target_region']} region · {camp['channels']}"),

        # KPI strip
        _row(
            _kpi("Customers Reached", f"{detail['n_customers']:,}", color=PRIMARY),
            _kpi("Stores Participating", detail["n_sites"], color=PRIMARY_DARK),
            _kpi("Avg Visits/Customer", detail["avg_visits_per_cust"], color=ACCENT),
            _kpi("Basket Lift", f"{detail['basket_pct_increase']:+.1f}%",
                 sub=f"${detail['basket_size_pre']:.2f} → ${detail['basket_size_during']:.2f}", color=SUCCESS),
            _kpi("Cross-Category Rate", f"{detail['cross_category_rate']:.0%}", color=PRIMARY),
        ),

        # Forecast vs Actual + Basket composition
        _row(
            _G([_section_title("Forecasted vs Actual Revenue"),
                _chart(_make_forecast_actual_chart(detail), height=280)], flex=2, min_w="320px"),
            _G([_section_title("Basket Composition"),
                _chart(_make_basket_pie(detail["basket_composition"]), height=280)], flex=1, min_w="240px"),
        ),

        # Regional participation
        _section_title("Regional Participation"),
        _table(detail["regional_participation"], "camp-reg"),

        # AI Insights
        _section_title("AI Insights & Suggested Actions"),
        html.Div([
            html.Div(ins, style={"background":"#EAF8FC","border":f"1px solid {BORDER}","borderRadius":"6px",
                                  "color":NEAR_BLACK,"fontSize":"13px","lineHeight":"1.6",
                                  "padding":"12px 14px","marginBottom":"8px"})
            for ins in detail["insights"]
        ]),
    ], style={"padding":"24px"})


def render_insights(insight_action=None):
    insights = bk.get_insights()
    offer_ops = bk.get_offer_strategy_data()

    if insight_action is not None:
        try:
            ins = insights[int(insight_action)]
            return _render_campaign_builder(ins)
        except (IndexError, TypeError, ValueError):
            pass

    return html.Div([
        _page_header("Insights & Recommended Actions",
                     "AI-generated opportunities ranked by estimated revenue impact"),

        _card(
            _section_title("Decisioning Preview · Retrieve then Rank"),
            html.Div("Candidate offers combine similar-customer redemption behavior with category affinity and context before ranking.",
                     style={"color":MUTED,"fontSize":"12px","lineHeight":"1.6","marginBottom":"10px"}),
            _table(offer_ops["decisioning"], "decisioning-preview", max_rows=5),
        ),

        html.Div([
            _insight_card_full(ins) for ins in insights
        ], style={"display":"flex","gap":"16px","flexWrap":"wrap","marginBottom":"24px"}),

        html.Div([
            html.Span("Select an insight and click ", style={"color":NEAR_BLACK}),
            html.Span("Build Campaign", style={"color":PRIMARY,"fontWeight":"700"}),
            html.Span(" to create a campaign from this insight and add it to the Campaign Monitor.",
                      style={"color":NEAR_BLACK}),
        ], style={"background":"#EAF8FC","border":f"1px solid {BORDER}","borderRadius":"8px",
                   "padding":"12px 16px","fontSize":"12px"}),
    ], style={"padding":"24px"})


def _insight_card_full(ins):
    urg_color = _urgency_color(ins["urgency"])
    return html.Div([
        _row(
            html.Div([
                _row(
                    html.Span(ins["title"],
                              style={"color":PRIMARY_DARK,"fontWeight":"700","fontSize":"15px","flex":"1"}),
                    _badge(ins["urgency"], urg_color),
                    gap="8px", mb="0",
                ),
            ], style={"flex":"1"}),
            gap="12px", mb="12px",
        ),
        html.Div(ins["detail"],
                 style={"color":NEAR_BLACK,"fontSize":"13px","lineHeight":"1.7","marginBottom":"14px"}),
        html.Div(style={"height":"1px","background":BORDER,"marginBottom":"14px"}),
        _row(
            html.Div([
                html.Div("Suggested campaign:", style={"color":MUTED,"fontSize":"11px","marginBottom":"4px"}),
                html.Div(ins["suggested_name"], style={"color":PRIMARY_DARK,"fontWeight":"700","fontSize":"13px"}),
            ], style={"flex":"1"}),
            html.Div(ins["metric"],
                     style={"color":PRIMARY,"fontWeight":"700","fontSize":"14px","alignSelf":"center"}),
            gap="16px", mb="0",
        ),
        html.Div(style={"height":"12px"}),
        _btn("Build Campaign", {"type":"btn-insight","index":ins["id"]}, color=PRIMARY_DARK),
    ], style={"background":CARD_BG,"border":f"1px solid {BORDER}",
               "borderLeft":f"4px solid {urg_color}","borderRadius":"8px",
               "padding":"20px","flex":"1","minWidth":"300px"})


def _render_campaign_builder(ins):
    channels_opts = ["In-store discount","Fuel loyalty","SMS","Digital","Email","POS",
                     "Social","Display","Coupon","App","Billboard","Radio"]
    regions_opts  = ["all","South","Southeast","Midwest","West","Northeast"]
    today = date.today()

    return html.Div([
        _row(
            _btn("← Back to Insights", {"type":"btn-nav","index":"cancel"}, color=MUTED, small=True),
            gap="8px", mb="16px",
        ),
        _page_header(f"Campaign Builder — from: {ins['title']}"),

        html.Div([
            html.Div([
                # Background context
                html.Div([
                    html.Div("Insight Context", style={"color":PRIMARY_DARK,"fontWeight":"700","fontSize":"13px","marginBottom":"8px"}),
                    html.Div(ins["detail"], style={"color":NEAR_BLACK,"fontSize":"12px","lineHeight":"1.6"}),
                    html.Div(ins["metric"], style={"color":PRIMARY,"fontWeight":"700","fontSize":"13px","marginTop":"8px"}),
                ], style={"background":"#EAF8FC","border":f"1px solid {BORDER}","borderRadius":"8px",
                           "padding":"16px","marginBottom":"20px"}),

                # Campaign name
                html.Div("Campaign Name", style={"color":PRIMARY_DARK,"fontWeight":"600","fontSize":"12px","marginBottom":"6px"}),
                dcc.Input(id={"type":"build-field","index":"name"}, value=ins["suggested_name"], type="text",
                          style={"width":"100%","padding":"8px 12px","border":f"1px solid {BORDER}",
                                 "borderRadius":"6px","fontSize":"13px","marginBottom":"16px",
                                 "boxSizing":"border-box"}),

                # Channels
                html.Div("Channels", style={"color":PRIMARY_DARK,"fontWeight":"600","fontSize":"12px","marginBottom":"6px"}),
                dcc.Checklist(
                    id={"type":"build-field","index":"channels"},
                    options=[{"label": f"  {c}", "value": c} for c in channels_opts],
                    value=ins.get("suggested_channels", []),
                    inline=True,
                    labelStyle={"marginRight":"14px","fontSize":"12px","color":NEAR_BLACK,
                                "display":"inline-flex","alignItems":"center","gap":"4px","marginBottom":"6px"},
                    inputStyle={"accentColor":PRIMARY},
                    style={"marginBottom":"16px"},
                ),

                # Region + Dates
                _row(
                    html.Div([
                        html.Div("Target Region", style={"color":PRIMARY_DARK,"fontWeight":"600","fontSize":"12px","marginBottom":"6px"}),
                        dcc.Dropdown(id={"type":"build-field","index":"region"},
                                     options=[{"label":r,"value":r} for r in regions_opts],
                                     value=ins.get("suggested_region","all"),
                                     style={"fontSize":"13px"},
                                     clearable=False),
                    ], style={"flex":"1","minWidth":"140px"}),
                    html.Div([
                        html.Div("Start Date", style={"color":PRIMARY_DARK,"fontWeight":"600","fontSize":"12px","marginBottom":"6px"}),
                        dcc.Input(id={"type":"build-field","index":"start"}, type="text", value=str(today),
                                  placeholder="YYYY-MM-DD",
                                  style={"padding":"7px 10px","border":f"1px solid {BORDER}",
                                         "borderRadius":"6px","fontSize":"13px","width":"100%"}),
                    ], style={"flex":"1","minWidth":"140px"}),
                    html.Div([
                        html.Div("End Date", style={"color":PRIMARY_DARK,"fontWeight":"600","fontSize":"12px","marginBottom":"6px"}),
                        dcc.Input(id={"type":"build-field","index":"end"}, type="text", value=str(today + timedelta(days=90)),
                                  placeholder="YYYY-MM-DD",
                                  style={"padding":"7px 10px","border":f"1px solid {BORDER}",
                                         "borderRadius":"6px","fontSize":"13px","width":"100%"}),
                    ], style={"flex":"1","minWidth":"140px"}),
                    gap="12px",
                ),

                html.Div(style={"height":"20px"}),
                _row(
                    _btn("Add to Campaign Monitor", {"type":"btn-nav","index":"submit-camp"}, color=PRIMARY),
                    _btn("Cancel", {"type":"btn-nav","index":"cancel-form"}, color=MUTED),
                    gap="12px", mb="0",
                ),
            ]),
        ], style={"maxWidth":"700px","background":CARD_BG,"border":f"1px solid {BORDER}",
                   "borderRadius":"10px","padding":"28px"}),
    ], style={"padding":"24px"})


def render_whatif():
    base   = bk.get_whatif_base_data()
    offer_ops = bk.get_offer_strategy_data()
    camps  = base["campaigns"]
    regions= list(base["region_basket"].keys())

    # Default initial state
    default_camp = camps[0]
    default_reg  = "South"
    init_kpis    = _row(
        _kpi("Customers Reached",   f"{int(200*820*0.25):,}",  color=PRIMARY),
        _kpi("Incremental Revenue", f"+${round(200*820*0.25*4*default_camp['basket_size_increase']/1e6,2):.2f}M", color=SUCCESS),
        _kpi("Projected Uplift",    f"{default_camp['campaign_uplift_pct']:+.1f}%", color=PRIMARY_DARK),
        _kpi("Est. Campaign Cost",  "$240K",  color=ACCENT),
        _kpi("ROI", f"{round(200*820*0.25*4*default_camp['basket_size_increase']/(200*1200),1):.1f}×", color=PRIMARY),
    )
    init_chart = _make_campaign_sim_chart(default_camp, default_reg, 200, 25, base)
    init_ch    = _make_channel_chart(250, base["channel_mixes"]["Balanced"], base)

    _lbl = lambda t: html.Div(t, style={"color":PRIMARY_DARK,"fontWeight":"600","fontSize":"12px",
                                         "marginTop":"14px","marginBottom":"6px"})
    _sub = lambda t: html.Div(t, style={"color":MUTED,"fontSize":"11px","marginBottom":"4px"})

    return html.Div([
        _page_header("What-If Simulator",
                     "Model campaign scenarios and channel budgets before committing spend"),

        _card(
            _section_title("Moment Marketing Guardrails"),
            html.Div("Use the trigger context to test whether a promotion can be delivered within the required customer moment.",
                     style={"color":MUTED,"fontSize":"12px","lineHeight":"1.6","marginBottom":"10px"}),
            _table(offer_ops["triggers"], "scenario-triggers", max_rows=4),
        ),

        # ── Section 1: Campaign Expansion ─────────────────────────────────
        _section_title("Campaign Expansion Simulator"),
        _row(
            # Controls panel
            _G([_card(
                html.Div([
                    html.Div("Select a live campaign as the baseline, choose a new target region and "
                             "adjust sites and participation to see projected revenue impact.",
                             style={"color":MUTED,"fontSize":"12px","lineHeight":"1.6","marginBottom":"16px"}),

                    _lbl("Base Campaign"),
                    dcc.Dropdown(
                        id={"type":"whatif-ctrl","index":"campaign"},
                        options=[{"label":c["name"],"value":c["campaign_id"]} for c in camps],
                        value=camps[0]["campaign_id"], clearable=False,
                        style={"fontSize":"13px"},
                    ),

                    _lbl("Target Region"),
                    dcc.Dropdown(
                        id={"type":"whatif-ctrl","index":"region"},
                        options=[{"label":r,"value":r} for r in regions],
                        value="South", clearable=False,
                        style={"fontSize":"13px"},
                    ),

                    _lbl("Number of Sites"),
                    _sub("Drag to set how many sites to run the campaign across"),
                    dcc.Slider(id={"type":"whatif-ctrl","index":"sites"},
                               min=50, max=600, step=25, value=200,
                               marks={i:str(i) for i in [50,200,400,600]},
                               tooltip={"placement":"bottom","always_visible":True}),

                    _lbl("Participation Rate Target (%)"),
                    _sub("% of site customers expected to engage"),
                    dcc.Slider(id={"type":"whatif-ctrl","index":"participation"},
                               min=5, max=55, step=5, value=25,
                               marks={i:f"{i}%" for i in [5,15,25,35,45,55]},
                               tooltip={"placement":"bottom","always_visible":True}),
                ]),
            )], flex=1, min_w="280px"),

            # Results panel
            _G([
                html.Div(id={"type":"whatif-out","index":"camp-kpis"}, children=init_kpis),
                html.Div(style={"height":"12px"}),
                dcc.Graph(id={"type":"whatif-out","index":"camp-chart"},
                          figure=init_chart, config={"displayModeBar":False},
                          style={"height":"280px"}),
            ], flex=2, min_w="400px"),
        ),

        # ── Section 2: Channel Budget Optimizer ───────────────────────────
        _section_title("Channel Budget Optimizer"),
        _card(
            html.Div("Set your total campaign budget and choose a channel mix strategy to see "
                     "projected reach, conversions, and ROI per channel.",
                     style={"color":MUTED,"fontSize":"12px","lineHeight":"1.6","marginBottom":"16px"}),
            _row(
                html.Div([
                    _lbl("Total Campaign Budget ($K)"),
                    dcc.Slider(id={"type":"whatif-budget","index":"0"},
                               min=50, max=1000, step=50, value=250,
                               marks={i:f"${i}K" for i in [50,250,500,750,1000]},
                               tooltip={"placement":"bottom","always_visible":True}),
                ], style={"flex":"1","minWidth":"280px"}),
                html.Div([
                    _lbl("Channel Mix Strategy"),
                    dcc.RadioItems(
                        id={"type":"whatif-mix","index":"0"},
                        options=[{"label":f"  {m}","value":m}
                                 for m in base["channel_mixes"].keys()],
                        value="Balanced", inline=True,
                        labelStyle={"marginRight":"18px","fontSize":"13px","color":NEAR_BLACK,
                                    "display":"inline-flex","alignItems":"center","gap":"4px"},
                        inputStyle={"accentColor":PRIMARY},
                    ),
                    html.Div([
                        html.Div([
                            html.Span(m+": ", style={"color":PRIMARY_DARK,"fontWeight":"600","fontSize":"11px"}),
                            html.Span(", ".join(f"{ch} {v}%" for ch, v in
                                      zip(base["channel_params"].keys(), base["channel_mixes"][m])),
                                      style={"color":MUTED,"fontSize":"11px"}),
                        ])
                        for m in base["channel_mixes"].keys()
                    ]),
                ], style={"flex":"1","minWidth":"280px"}),
            gap="20px"),
            html.Div(style={"height":"8px"}),
            dcc.Graph(id={"type":"whatif-out","index":"channel-chart"},
                      figure=init_ch, config={"displayModeBar":False},
                      style={"height":"300px"}),
        ),

    ], style={"padding":"24px"})


def render_loyalty():
    d = bk.get_loyalty_data()
    offer_ops = bk.get_offer_strategy_data()
    k = d["kpis"]
    act_color  = SUCCESS if k["act_yoy_pct"] >= 0 else DANGER
    reg_color  = SUCCESS if k["reg_yoy_pct"] >= 0 else DANGER

    # Site-level table data
    site_df = d["site_df"]
    site_table_data = site_df[[
        "site_name","region","state","reg_cy","act_cy","reg_py","act_py","reg_yoy_pct","act_yoy_pct"
    ]].rename(columns={
        "site_name": "Site", "region": "Region", "state": "State",
        "reg_cy": "Reg CY", "act_cy": "Act CY",
        "reg_py": "Reg PY", "act_py": "Act PY",
        "reg_yoy_pct": "Reg YoY %", "act_yoy_pct": "Act YoY %",
    }).to_dict("records")

    return html.Div([
        _page_header("Loyalty Analytics",
                     "CY vs PY Year-to-Date — Registrations & Activations"),

        # KPI row matching "Leading with Loyalty" dashboard style
           _row(
              _kpi("Activations CY YTM",
                  f"{k['cy_act_ytm']:,}",
                  sub=f"PY YTM: {k['py_act_ytm']:,}",
                  color=PRIMARY),
              _kpi("Activations PY YTM",
                  f"{k['py_act_ytm']:,}",
                  sub="Prior year same period",
                  color=MUTED),
              _kpi("Activations CY vs PY",
                  f"{k['act_yoy_pct']:+.1f}%",
                  sub="Year-over-year growth",
                  color=act_color),
              _kpi("Registrations CY YTM",
                  f"{k['cy_reg_ytm']:,}",
                  sub=f"PY YTM: {k['py_reg_ytm']:,}",
                  color=PRIMARY_DARK),
              _kpi("Registrations PY YTM",
                  f"{k['py_reg_ytm']:,}",
                  sub="Prior year same period",
                  color=MUTED),
              _kpi("Registrations CY vs PY",
                  f"{k['reg_yoy_pct']:+.1f}%",
                  sub="Year-over-year growth",
                  color=reg_color),
           ),

        _section_title("Fuel-Linked Loyalty Rewards"),
        _card(
            html.Div("In-store spend earns cents-per-gallon savings. Every threshold is visible to the customer and auditable through redemption.",
                     style={"color":MUTED,"fontSize":"12px","lineHeight":"1.6","marginBottom":"10px"}),
            _table(offer_ops["fuel_rewards"], "fuel-rewards", max_rows=5),
        ),

        # View toggle + trend charts
        _section_title("Registrations & Activations Overall Summary"),
        _card(
            dcc.RadioItems(
                id="loyalty-view-toggle",
                options=[
                    {"label": "  Overall Volume", "value": "overall"},
                    {"label": "  Activation Rate per Site", "value": "rate"},
                ],
                value="overall", inline=True,
                labelStyle={"marginRight":"24px","fontSize":"13px","color":NEAR_BLACK,
                            "display":"inline-flex","alignItems":"center","gap":"4px"},
                inputStyle={"accentColor": PRIMARY},
            ),
            html.Div(style={"height":"10px"}),
            dcc.Graph(id="loyalty-trend-chart",
                      figure=_make_loyalty_trend_chart(d, "overall"),
                      config={"displayModeBar": False},
                      style={"height": "320px"}),
        ),

        # Regional + % Activations side-by-side
        _row(
            _G([
                _section_title("Performance by Region — CY YTM"),
                _card(dcc.Graph(figure=_make_loyalty_region_chart(d["region_summary"]),
                               config={"displayModeBar": False},
                               style={"height": "280px"})),
            ], flex=3, min_w="360px"),
            _G([
                _section_title("% Activations of Registrations"),
                _card(dcc.Graph(figure=_make_pct_activations_chart(d),
                               config={"displayModeBar": False},
                               style={"height": "280px"})),
            ], flex=2, min_w="280px"),
        ),

        # Executive Summary table — click any row to drill in
        html.Div([
            _section_title("Executive Summary — CY vs PY Comparison"),
            html.Span(" ↓ Click any metric row to see site & monthly detail",
                      style={"fontSize":"11px","color":MUTED,"fontStyle":"italic",
                             "marginLeft":"8px","verticalAlign":"middle"}),
        ], style={"display":"flex","alignItems":"baseline","marginBottom":"8px"}),
        _card(
            dash_table.DataTable(
                id="loyalty-exec-table",
                data=[{"Metric": row[0], "CY YTM": row[1], "PY YTM": row[2], "Δ YoY": row[3]}
                      for row in d["exec_summary"]],
                columns=[{"name": c, "id": c}
                         for c in ["Metric", "CY YTM", "PY YTM", "Δ YoY"]],
                row_selectable="single",
                selected_rows=[],
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": PRIMARY_DARK, "color": WHITE,
                              "fontWeight": "700", "fontSize": "12px",
                              "border": f"1px solid {BORDER}"},
                style_cell={"backgroundColor": CARD_BG, "color": NEAR_BLACK,
                            "fontSize": "12px", "padding": "8px 12px",
                            "border": f"1px solid {BORDER}", "textAlign": "left",
                            "cursor": "pointer"},
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": PAGE_BG},
                    {"if": {"filter_query": "{Δ YoY} contains '+'", "column_id": "Δ YoY"},
                     "color": SUCCESS, "fontWeight": "700"},
                    {"if": {"state": "selected"}, "backgroundColor": _PRIMARY_15,
                     "border": f"1px solid {PRIMARY}"},
                ],
                page_action="none",
            ),
        ),

        # Drill-down panel — shown when a row is selected
        html.Div(id="loyalty-detail-panel", style={"display": "none"}),

        # Site-level deep dive
        _section_title("Site-Level Loyalty Deep Dive"),
        _card(
            dash_table.DataTable(
                id="loyalty-site-table",
                data=site_table_data,
                columns=[{"name": c, "id": c, "type": "numeric" if "%" in c or c in ("Reg CY","Act CY","Reg PY","Act PY") else "text"}
                         for c in ["Site","Region","State","Reg CY","Act CY","Reg PY","Act PY","Reg YoY %","Act YoY %"]],
                sort_action="native",
                filter_action="native",
                page_size=15,
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": PRIMARY_DARK, "color": WHITE,
                              "fontWeight": "700", "fontSize": "12px",
                              "border": f"1px solid {BORDER}"},
                style_cell={"backgroundColor": CARD_BG, "color": NEAR_BLACK,
                            "fontSize": "12px", "padding": "8px 12px",
                            "border": f"1px solid {BORDER}", "textAlign": "left",
                            "maxWidth": "200px", "overflow": "hidden",
                            "textOverflow": "ellipsis"},
                style_data_conditional=[
                    {"if": {"row_index": "odd"}, "backgroundColor": PAGE_BG},
                    {"if": {"filter_query": "{Reg YoY %} > 0", "column_id": "Reg YoY %"},
                     "color": SUCCESS, "fontWeight": "700"},
                    {"if": {"filter_query": "{Act YoY %} > 0", "column_id": "Act YoY %"},
                     "color": SUCCESS, "fontWeight": "700"},
                ],
            )
        ),

    ], style={"padding": "24px"})


@app.callback(
    Output("loyalty-trend-chart", "figure"),
    Input("loyalty-view-toggle", "value"),
    prevent_initial_call=True,
)
def update_loyalty_trend(view):
    d = bk.get_loyalty_data()
    return _make_loyalty_trend_chart(d, view or "overall")


@app.callback(
    Output("loyalty-detail-panel", "children"),
    Output("loyalty-detail-panel", "style"),
    Input("loyalty-exec-table", "selected_rows"),
    State("loyalty-exec-table", "data"),
    prevent_initial_call=True,
)
def show_loyalty_detail(selected_rows, table_data):
    if not selected_rows:
        return [], {"display": "none"}

    row_idx  = selected_rows[0]
    metric   = table_data[row_idx]["Metric"]
    cy_val   = table_data[row_idx]["CY YTM"]
    py_val   = table_data[row_idx]["PY YTM"]
    delta    = table_data[row_idx]["Δ YoY"]

    d        = bk.get_loyalty_data()
    detail   = d["detail_data"].get(metric)
    if not detail:
        return [], {"display": "none"}

    rows = detail["rows"]
    unit = detail["unit"]

    # Build columns from first row keys
    all_cols = list(rows[0].keys()) if rows else []
    fixed    = [c for c in ["Site","Region","State","Status"] if c in all_cols]
    month_cols = [c for c in all_cols if c not in fixed and c != "Total"]
    total_col  = ["Total"] if "Total" in all_cols else []
    columns    = [{"name": c, "id": c} for c in fixed + month_cols + total_col]

    panel_content = html.Div([
        # Panel header
        html.Div([
            html.Div([
                html.Span("Detail View: ", style={"color": MUTED, "fontSize": "12px"}),
                html.Span(metric, style={"color": PRIMARY_DARK, "fontWeight": "700", "fontSize": "14px"}),
                html.Span(f"  |  CY YTM: {cy_val}  ·  PY YTM: {py_val}  ·  YoY: {delta}",
                          style={"color": MUTED, "fontSize": "12px", "marginLeft": "12px"}),
            ], style={"flex": "1"}),
            html.Button("✕ Close Detail", id="loyalty-detail-close", n_clicks=0,
                        style={"background": PAGE_BG, "border": f"1px solid {BORDER}",
                               "borderRadius": "6px", "padding": "5px 14px",
                               "fontSize": "12px", "color": PRIMARY_DARK, "cursor": "pointer",
                               "fontWeight": "600"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "12px"}),

        html.Div(f"Site-level monthly breakdown — {unit}. Top 15 sites shown. "
                 "Totals match CY YTM executive summary.",
                 style={"color": MUTED, "fontSize": "11px", "marginBottom": "10px",
                        "fontStyle": "italic"}),

        dash_table.DataTable(
            data=rows,
            columns=columns,
            sort_action="native",
            fixed_columns={"headers": True, "data": len(fixed)},
            style_table={"overflowX": "auto", "minWidth": "100%"},
            style_header={"backgroundColor": PRIMARY_DARK, "color": WHITE,
                          "fontWeight": "700", "fontSize": "11px",
                          "border": f"1px solid {BORDER}", "whiteSpace": "nowrap"},
            style_cell={"backgroundColor": CARD_BG, "color": NEAR_BLACK,
                        "fontSize": "11px", "padding": "6px 10px",
                        "border": f"1px solid {BORDER}", "textAlign": "right",
                        "minWidth": "70px", "maxWidth": "120px",
                        "whiteSpace": "nowrap", "overflow": "hidden"},
            style_cell_conditional=[
                {"if": {"column_id": "Site"},
                 "textAlign": "left", "minWidth": "200px", "maxWidth": "220px",
                 "fontWeight": "600", "color": PRIMARY_DARK},
                {"if": {"column_id": "Region"}, "textAlign": "left", "minWidth": "80px"},
                {"if": {"column_id": "State"},  "textAlign": "left", "minWidth": "60px"},
                {"if": {"column_id": "Status"}, "textAlign": "left", "minWidth": "70px"},
            ],
            style_data_conditional=[
                {"if": {"row_index": "odd"}, "backgroundColor": PAGE_BG},
                {"if": {"column_id": "Total"},
                 "fontWeight": "700", "backgroundColor": "#EAF8FC", "color": PRIMARY_DARK},
            ],
            page_action="none",
        ),
    ], style={"background": CARD_BG, "border": f"2px solid {PRIMARY}",
              "borderRadius": "8px", "padding": "20px", "marginBottom": "16px"})

    return panel_content, {"display": "block"}


@app.callback(
    Output("loyalty-exec-table", "selected_rows"),
    Input("loyalty-detail-close", "n_clicks"),
    prevent_initial_call=True,
)
def close_loyalty_detail(_):
    return []


def render_pricing():
    data = bk.get_pricing_data()
    offer_ops = bk.get_offer_strategy_data()
    kpis = data["kpis"]

    return html.Div([
        _page_header("Pricing Intelligence",
                     "ML-driven willingness-to-pay · Polaris Pricing Platform · bp CoE Preview"),

        # Model status banner
        html.Div([
            html.Span("ML MODEL ACTIVE", style={
                "background": PRIMARY, "color": WHITE, "fontWeight": "700",
                "fontSize": "10px", "padding": "3px 10px", "borderRadius": "4px",
                "letterSpacing": "1px", "marginRight": "12px",
            }),
            html.Span(
                "XGBoost · Features: neighbourhood income, competitor pricing, loyalty tier, "
                "traffic volume, site type · Last trained 7 days ago · Coverage 94.2%",
                style={"color": MUTED, "fontSize": "12px"},
            ),
        ], style={"background": CARD_BG, "border": f"1px solid {BORDER}", "borderRadius": "8px",
                   "padding": "10px 16px", "marginBottom": "16px", "display": "flex", "alignItems": "center"}),

        _card(
            _section_title("Offer Safety Gates"),
            _row(
                _kpi("Margin Floor", f"{offer_ops['kpis']['margin_floor_pct']:.1f}%", "minimum", color=ACCENT),
                _kpi("Inventory Gated", offer_ops["kpis"]["inventory_gated"], "offers suppressed", color=WARNING),
                _kpi("Pump-to-Store", f"{offer_ops['kpis']['pump_to_store_rate']:.1f}%", "conversion", color=PRIMARY),
            ),
            html.Div("Price and offer recommendations are suppressed when inventory is below threshold or effective margin falls below the configured floor.",
                     style={"color":MUTED,"fontSize":"11px","marginTop":"8px"}),
        ),

        # KPI strip
        _row(
            _kpi("Avg WTP Score",        f"{kpis['avg_wtp']}/10",            color=PRIMARY),
            _kpi("Sites w/ Opportunity", f"{kpis['sites_opportunity']:,}",    color=PRIMARY_DARK),
            _kpi("Est. Revenue Uplift",  f"+${kpis['est_uplift_m']:.1f}M",   color=SUCCESS),
            _kpi("Model Coverage",       f"{kpis['model_coverage_pct']:.1f}%",color=ACCENT),
            _kpi("Avg Price Gap",        f"+{kpis['avg_price_gap_c']}¢/gal", color=PRIMARY),
        ),

        # WTP map + price sensitivity
        _row(
            _G([
                _section_title("Willingness to Pay Score by State"),
                dcc.Graph(id="wtp-map", figure=_make_wtp_map(data["wtp_by_state"]),
                          config={"displayModeBar": False}, style={"height": "360px"}),
            ], flex=2, min_w="380px"),
            _G([
                _section_title("Current vs Recommended vs Competitor ($/gal)"),
                _chart(_make_price_sensitivity(data["region_pricing"]), height=360),
            ], flex=1, min_w="280px"),
        ),

        # Revenue uplift simulator
        _card(
            _section_title("Revenue Uplift Simulator — Price Adjustment Impact"),
            html.Div(
                "Drag the slider to model the network-wide revenue impact of a fuel price adjustment. "
                "Demand elasticity is applied per region based on historical price sensitivity.",
                style={"color": MUTED, "fontSize": "12px", "marginBottom": "16px"},
            ),
            dcc.Slider(
                id={"type": "pricing-slider", "index": "0"},
                min=0, max=15, step=1, value=5,
                marks={i: f"+{i}¢" for i in range(0, 16, 3)},
                tooltip={"placement": "bottom", "always_visible": True},
            ),
            html.Div(style={"height": "8px"}),
            dcc.Graph(
                id={"type": "pricing-chart", "index": "sim"},
                figure=_make_simulator_chart(
                    data["sim_regions"], data["sim_base_volumes"],
                    data["sim_elasticities"], data["sim_base_prices"], 5,
                ),
                config={"displayModeBar": False},
                style={"height": "280px"},
            ),
        ),

        # Segment scatter + recommendations
        _row(
            _G([
                _section_title("Customer WTP by Loyalty Segment"),
                _chart(_make_segment_scatter(data["segments"]), height=280),
            ], flex=1, min_w="320px"),
            _G([
                _section_title("Top Pricing Recommendations"),
                _table(data["recommendations"], "pricing-recs"),
                html.Div(
                    "Recommendations generated by Polaris Pricing Platform · "
                    "High confidence = 3+ corroborating features agree",
                    style={"color": MUTED, "fontSize": "11px", "marginTop": "8px"},
                ),
            ], flex=2, min_w="380px"),
        ),

    ], style={"padding": "24px"})


def render_genie():
    return html.Div([
        _page_header("Genie AI",
                     "Ask data questions about revenue, campaigns, stores and baskets — powered by Databricks AI/BI"),

        # Preset question buttons
        _section_title("Suggested Questions"),
        html.Div([
            html.Button(q, id={"type":"genie-preset","index":i}, n_clicks=0, style={
                "background":"rgba(0,217,255,0.10)","border":f"1px solid {BORDER}","color":PRIMARY_DARK,
                "borderRadius":"6px","padding":"8px 14px","fontSize":"12px","fontWeight":"600",
                "cursor":"pointer","margin":"4px","fontFamily":"Arial, sans-serif",
                "textAlign":"left","lineHeight":"1.4",
            }) for i, q in enumerate(PRESET_QS)
        ], style={"marginBottom":"20px","display":"flex","flexWrap":"wrap","gap":"4px"}),

        # Input area
        _card(
            html.Div("Ask your own question:", style={"color":PRIMARY_DARK,"fontWeight":"600","fontSize":"13px","marginBottom":"8px"}),
            _row(
                dcc.Input(id={"type":"genie-in","index":"0"}, type="text", debounce=False,
                          placeholder="e.g. Which Texas stores have the highest basket size?",
                          n_submit=0,
                          style={"flex":"1","padding":"10px 14px","border":f"1px solid {BORDER}",
                                 "borderRadius":"6px","fontSize":"13px","fontFamily":"Arial, sans-serif"}),
                _btn("Ask Genie", {"type":"genie-btn","index":"0"}, color=PRIMARY),
                gap="10px", mb="0",
            ),
            html.Div(
                "Genie is connected to your live Shell retail data in Databricks. "
                "Ask data questions — revenue, campaigns, stores, baskets.",
                style={"color":MUTED,"fontSize":"11px","marginTop":"8px"},
            ),
        ),

        # Response history with loading spinner
        dcc.Loading(
            html.Div(id={"type":"genie-out","index":"0"}),
            type="circle",
            color=PRIMARY,
            style={"marginTop":"16px"},
        ),
    ], style={"padding":"24px","maxWidth":"900px"})


def render_shell_project():
    guide = bk.get_scd2_guide()
    quality = bk.get_scd2_quality_summary()
    cards = bk.get_scd2_quality_cards()
    profile_df = bk.get_customer_profile()
    quarantine_df = bk.get_customer_profile_quarantine()
    history_df = bk.get_customer_profile_history("CUST-1001")

    tracked = guide.get("scd2_tracked_columns", [])
    scd1_cols = guide.get("scd1_columns", [])
    quality_checks = guide.get("quality_checks", [])

    quality_badge = "PASS" if quality.get("validation_status") == "pass" else "ALERT"
    quality_color = SUCCESS if quality_badge == "PASS" else WARNING

    return html.Div([
        _page_header(
            "Shell Project — SCD2 & Data Quality Guide",
            "Historical tracking, transformation rules, and validation applied to the workspace.retail_store schema"
        ),

        _row(
            _kpi("Total Customers", cards.get("total_customers", 0), "current", sub="active customer profile versions"),
            _kpi("Quality Score", f"{cards.get('quality_score', 0):.0f}%", "compliance", sub="SCD2 integrity score"),
            _kpi("Quarantine Rate", f"{cards.get('quarantine_rate_pct', 0):.1f}%", "input rows", sub="records flagged for review"),
            _kpi("Duplicate Current Rows", cards.get("duplicate_current_rows", 0), "violations", sub="must be zero for pass"),
        ),

        _row(
            _G([
                _section_title("Project Summary"),
                html.Div([
                    html.Div(f"Title: {guide.get('title', 'Shell Project')}", style={"fontWeight":"700","color":PRIMARY_DARK,"marginBottom":"6px"}),
                    html.Div(f"Version: {guide.get('version', '2.0')}", style={"fontSize":"12px","color":MUTED,"marginBottom":"6px"}),
                    html.Div(f"Prepared by: {guide.get('prepared_by', 'Kenneth Sherrod')}", style={"fontSize":"12px","color":MUTED,"marginBottom":"6px"}),
                    html.Div(f"Audience: {guide.get('audience', 'Development Team')}", style={"fontSize":"12px","color":MUTED,"marginBottom":"12px"}),
                    html.Div(guide.get("overview", "Historical SCD2 tracking for customer profile and consent history."), style={"fontSize":"12px","lineHeight":"1.6","color":NEAR_BLACK}),
                ]),
            ], flex=2, min_w="320px"),
            _G([
                _section_title("Validation Status"),
                html.Div([
                    html.Div(_badge(quality_badge, quality_color, "rgba(46,158,107,0.12)" if quality_badge == "PASS" else "rgba(231,121,43,0.12)"), style={"marginBottom":"10px"}),
                    html.Div(f"Current customers: {quality.get('current_records', 0)}", style={"fontSize":"12px","marginBottom":"4px"}),
                    html.Div(f"Quarantine rows: {quality.get('quarantine_rows', 0)}", style={"fontSize":"12px","marginBottom":"4px"}),
                    html.Div(f"Duplicate current rows: {quality.get('duplicate_current_rows', 0)}", style={"fontSize":"12px","marginBottom":"4px"}),
                    html.Div(f"Unknown loyalty tiers: {quality.get('unknown_loyalty_tier_count', 0)}", style={"fontSize":"12px"}),
                ], style={"padding":"4px 0"}),
            ], flex=1, min_w="220px"),
        ),

        _row(
            _G([
                _section_title("SCD2 Tracked Columns"),
                html.Ul([
                    html.Li(col, style={"fontSize":"12px","marginBottom":"6px"}) for col in tracked
                ], style={"paddingLeft":"18px","marginTop":"0","lineHeight":"1.6"}),
            ], flex=1, min_w="260px"),
            _G([
                _section_title("SCD1 In-Place Columns"),
                html.Ul([
                    html.Li(col, style={"fontSize":"12px","marginBottom":"6px"}) for col in scd1_cols
                ], style={"paddingLeft":"18px","marginTop":"0","lineHeight":"1.6"}),
            ], flex=1, min_w="260px"),
        ),

        _section_title("Quality Checklist"),
        html.Div([
            html.Div(item, style={"fontSize":"12px","padding":"6px 0","borderBottom":"1px solid #eef2f5"})
            for item in quality_checks
        ], style={"background":CARD_BG,"border":"1px solid #EAF0F5","borderRadius":"8px","padding":"0 16px"}),

        _row(
            _G([
                _section_title("customer_profile (Sample)"),
                _table(profile_df.head(10), "shell-profile", max_rows=10),
            ], flex=2, min_w="420px"),
            _G([
                _section_title("customer_profile_quarantine"),
                _table(quarantine_df.head(10), "shell-quarantine", max_rows=10),
            ], flex=1, min_w="280px"),
        ),

        _section_title("Point-in-Time Customer History"),
        html.Div(
            "Example validation of the customer version timeline for CUST-1001. This shows the active row and the effective range used to answer historical queries.",
            style={"fontSize":"12px","color":MUTED,"marginBottom":"10px"},
        ),
        _table(
            history_df[[
                "customer_id",
                "loyalty_tier",
                "status",
                "preferred_channel",
                "home_zip",
                "preferred_store_id",
                "effective_start_date",
                "effective_end_date",
                "is_current",
                "_change_hash",
            ]],
            "shell-history",
            max_rows=10,
        ),

        _section_title("Key SCD2 Rules"),
        html.Div([
            html.Div("• SCD2 preserves history by inserting a new row whenever a tracked field changes.", style={"fontSize":"12px","marginBottom":"6px"}),
            html.Div("• customer_id + effective_start_date identifies each version.", style={"fontSize":"12px","marginBottom":"6px"}),
            html.Div("• consent flags and loyalty_tier are audited with a change hash and versioned timeline.", style={"fontSize":"12px","marginBottom":"6px"}),
            html.Div("• PII is stored as SHA-256 hashes in Silver; plaintext is quarantined or rejected.", style={"fontSize":"12px"}),
        ], style={"background":CARD_BG,"border":f"1px solid {BORDER}","borderRadius":"8px","padding":"14px 16px"}),

    ], style={"padding":"24px","maxWidth":"1200px"})


def render_data_catalog():
    catalog = bk.get_data_catalog()
    return html.Div([
        _page_header("Data Catalog", "Registered tables available to Shell retail analytics"),
        _row(
            _kpi("Registered Tables", len(catalog), "tables", color=PRIMARY),
            _kpi("Catalog", "workspace", "retail_store", color=PRIMARY_DARK),
            _kpi("Warehouse", getattr(bk, "WAREHOUSE_ID", "Configured"), "SQL warehouse", color=ACCENT),
        ),
        _card(_section_title("Retail Data Assets"), _table(catalog, "data-catalog", max_rows=50)),
    ], style={"padding":"24px","maxWidth":"1200px"})


def render_data_freshness():
    freshness = bk.get_data_freshness()
    return html.Div([
        _page_header("Data Freshness", "Latest table updates from the connected Databricks catalog"),
        _card(
            _section_title("Pipeline Currency"),
            _table(freshness, "data-freshness", max_rows=50),
            html.Div(
                "Freshness is read from information_schema.last_altered. Tables without metadata are omitted.",
                style={"color": MUTED, "fontSize": "11px", "marginTop": "10px"},
            ),
        ),
    ], style={"padding":"24px","maxWidth":"1200px"})


# ── Entry point ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port  = int(os.getenv("PORT", 8050))
    debug = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")
    app.run(host="0.0.0.0", port=port, debug=debug)
