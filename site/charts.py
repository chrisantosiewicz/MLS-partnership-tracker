"""Chart and component code for the site.

Kept out of the .qmd pages so they stay readable and the charts can be
checked on their own (python site/charts.py writes previews to site/_preview/).

Every chart is returned as a `Chart`: the Plotly figure plus its title (the
finding, computed from the data), subtitle, an optional note and the data
table behind it. `card()` turns a Chart into the HTML card the pages show,
with a "View data" table under every chart (the accessible fallback, and the
relief the palette's contrast check asks for).

Colors follow the dataviz reference palette (validated for color-vision
deficiency in light and dark). Charts are drawn with the light values;
site/assets/theme.js swaps each one for its dark step when the reader
switches the site to dark mode.
"""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from html import escape
from pathlib import Path

import duckdb
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

DB_PATH = Path(__file__).resolve().parent.parent / "tracker.duckdb"

# Light-mode values. theme.js holds the matching dark values (keep in sync).
SERIES = ["#257de0", "#f47230", "#00b894"]   # categorical slots 1-3: blue, orange, aqua
NEGATIVE = "#ec4647"                          # diverging pole opposite blue
TEXT = "#191919"
TEXT_2 = "#666666"
MUTED = "#8c8c8c"                             # baselines, reference lines
GRID = "#e6e6e3"
SURFACE = "#ffffff"                           # card surface (gaps and rings)
FONT = "Inter, system-ui, -apple-system, Segoe UI, sans-serif"

PLOTLY_CONFIG = {"displayModeBar": False, "responsive": True}


@dataclass
class Chart:
    fig: go.Figure
    title: str
    subtitle: str
    note: str = ""
    table: pd.DataFrame | None = field(default=None, repr=False)


def query(sql: str, params: list | None = None) -> pd.DataFrame:
    """Run a read-only query against the warehouse built by python/build.py."""
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        return con.execute(sql, params or []).fetchdf()


def raw_html(html: str) -> str:
    """Wrap HTML so Quarto passes it through untouched (print it in an asis cell)."""
    return f"\n```{{=html}}\n{html}\n```\n"


# ---------------------------------------------------------------- layout ---

def _style(fig: go.Figure, height: int) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font={"family": FONT, "color": TEXT_2, "size": 13},
        margin={"l": 8, "r": 16, "t": 36, "b": 36},
        hoverlabel={"bgcolor": SURFACE, "bordercolor": GRID,
                    "font": {"family": FONT, "color": TEXT, "size": 13}},
        legend={"orientation": "h", "x": 0, "y": 1.0, "yanchor": "bottom",
                "font": {"color": TEXT_2}, "bgcolor": "rgba(0,0,0,0)"},
        bargap=0.28,
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, tickcolor=GRID,
                     tickfont={"color": TEXT_2})
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID, tickcolor=GRID,
                     tickfont={"color": TEXT_2})
    return fig


def card(chart: Chart | None, chart_id: str, empty: str = "No data loaded yet.",
         source: str = "") -> str:
    """HTML card: finding title, subtitle, chart, data table, note."""
    if chart is None:
        return f"<div class='viz-card viz-empty'>{escape(empty)}</div>"
    plot = chart.fig.to_html(full_html=False, include_plotlyjs=False,
                             div_id=chart_id, config=PLOTLY_CONFIG)
    table = ""
    if chart.table is not None and not chart.table.empty:
        table = ("<details class='viz-data'><summary>View data</summary>"
                 + chart.table.to_html(index=False, classes="table table-sm", border=0)
                 + "</details>")
    note = f"<p class='viz-note'>{chart.note}</p>" if chart.note else ""
    src = f"<p class='viz-source'>{source}</p>" if source else ""
    return (f"<figure class='viz-card' aria-labelledby='{chart_id}-title'>"
            f"<figcaption><h3 id='{chart_id}-title' class='viz-title'>{escape(chart.title)}</h3>"
            f"<p class='viz-subtitle'>{escape(chart.subtitle)}</p></figcaption>"
            f"<div class='viz-plot'>{plot}</div>{note}{table}{src}</figure>")


def possessive(name: str) -> str:
    return f"{name}'" if name.endswith("s") else f"{name}'s"


def pct(x: float) -> str:
    return f"{x:+.0%}"


# ------------------------------------------------------------ components ---

def status() -> pd.Series:
    """Headline numbers for the KPI row and the data-status line."""
    return query("""
        SELECT
            (SELECT COUNT(*) FROM partnership_history WHERE is_current)                AS current_deals,
            (SELECT COUNT(DISTINCT club_id) FROM partnership_history WHERE is_current) AS clubs_covered,
            (SELECT COUNT(*) FROM dim_club)                                            AS clubs_total,
            (SELECT COUNT(*) FROM stg_partnerships)                                    AS rows_total,
            (SELECT COUNT(*) FROM stg_partnerships WHERE source_url IS NOT NULL)       AS rows_sourced,
            (SELECT COUNT(DISTINCT brand_id) FROM partnership_history WHERE is_current) AS brands,
            (SELECT COUNT(*) FROM mart_match_day_lift
             WHERE lift_vs_baseline IS NOT NULL)                                       AS club_match_days,
            (SELECT MIN(view_date) FROM fact_pageviews_daily)                          AS pageviews_from,
            (SELECT MAX(view_date) FROM fact_pageviews_daily)                          AS pageviews_through,
            (SELECT MAX(date_checked) FROM stg_partnerships)                           AS last_checked
    """).iloc[0]


def show_date(value) -> str:
    return "n/a" if value is None or str(value) in ("NaT", "None") else f"{value:%b %-d, %Y}"


def kpi_row(items: list[tuple[str, str, str]]) -> str:
    """Stat tiles: (value, label, detail)."""
    tiles = "".join(
        f"<div class='kpi'><div class='kpi-value'>{escape(v)}</div>"
        f"<div class='kpi-label'>{escape(label)}</div>"
        f"<div class='kpi-detail'>{escape(detail)}</div></div>"
        for v, label, detail in items)
    return f"<div class='kpi-row'>{tiles}</div>"


def sponsor_directory() -> str | None:
    """Filterable HTML table: one row per club, its current partners and source."""
    df = query("""
        SELECT club_id, short_name, conference,
               front_of_kit_brand, front_of_kit_category,
               sleeve_brand, sleeve_category,
               stadium_brand, stadium_category, stadium_sold_by,
               front_of_kit_source, sleeve_source, stadium_source, date_checked
        FROM mart_sponsor_directory
        ORDER BY short_name
    """)
    if df.empty:
        return None

    def cell(brand, category, source, badge: str = "") -> str:
        if brand is None or pd.isna(brand):
            return "<td class='dir-missing'>Not recorded</td>"
        link = (f" <a class='dir-src' href='{escape(source)}' rel='noopener' "
                f"title='Source for this deal' aria-label='Source for {escape(brand)}'>↗</a>"
                if isinstance(source, str) else "")
        return (f"<td><span class='dir-brand'>{escape(brand)}{link}</span>{badge}"
                f"<span class='dir-cat'>{escape(category or '')}</span></td>")

    rows = []
    for r in df.itertuples():
        badge = ("<span class='badge-venue' title='Naming rights sold by the venue owner, "
                 "not the club'>venue-sold</span>" if r.stadium_sold_by == "stadium_owner" else "")
        checked = f"{r.date_checked:%b %-d, %Y}" if pd.notna(r.date_checked) else ""
        search = " ".join(str(x) for x in r[2:10] if isinstance(x, str)).lower()
        rows.append(
            f"<tr data-conf='{escape(r.conference)}' data-search='{escape(search)}'>"
            f"<th scope='row'><span class='dir-club'>{escape(r.short_name)}</span>"
            f"<span class='dir-cat'>{escape(r.conference)}</span></th>"
            f"{cell(r.front_of_kit_brand, r.front_of_kit_category, r.front_of_kit_source)}"
            f"{cell(r.sleeve_brand, r.sleeve_category, r.sleeve_source)}"
            f"{cell(r.stadium_brand, r.stadium_category, r.stadium_source, badge)}"
            f"<td class='dir-checked'>{checked}</td></tr>")

    controls = (
        "<div class='dir-controls' role='search'>"
        "<input type='search' class='form-control dir-search' placeholder='Search clubs, brands or categories' "
        "aria-label='Search the sponsor directory'>"
        "<div class='seg' role='group' aria-label='Conference'>"
        "<button type='button' class='seg-btn active' data-conf=''>All</button>"
        "<button type='button' class='seg-btn' data-conf='Eastern'>Eastern</button>"
        "<button type='button' class='seg-btn' data-conf='Western'>Western</button></div>"
        "<span class='dir-count' aria-live='polite'></span></div>")
    return (f"<div class='directory'>{controls}<div class='table-wrap'>"
            "<table class='table dir-table'><thead><tr><th scope='col'>Club</th>"
            "<th scope='col'>Front of kit</th><th scope='col'>Sleeve</th>"
            "<th scope='col'>Stadium</th><th scope='col'>Last checked</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table></div></div>")


# ---------------------------------------------------------------- charts ---

ASSETS = ["Front-of-kit partner", "Sleeve partner", "Stadium naming rights"]


def category_landscape() -> Chart | None:
    """Horizontal stacked bars: current deals per category, split by asset."""
    df = query("SELECT category_name, asset_name, deals FROM mart_category_share")
    if df.empty:
        return None

    totals = df.groupby("category_name")["deals"].sum().sort_values()
    top_category, top_n = totals.index[-1], int(totals.iloc[-1])
    all_deals = int(totals.sum())

    fig = go.Figure()
    present = [a for a in ASSETS if a in set(df["asset_name"])]
    for color, asset in zip(SERIES, ASSETS):
        if asset not in present:
            continue  # keep each asset's color fixed even when one is missing
        part = df[df["asset_name"] == asset].set_index("category_name").reindex(totals.index)
        fig.add_bar(
            y=totals.index, x=part["deals"].fillna(0), name=asset.replace(" partner", ""),
            orientation="h",
            marker={"color": color, "line": {"color": SURFACE, "width": 2},
                    "cornerradius": 3},
            hovertemplate="<b>%{y}</b><br>" + asset + ": %{x}<extra></extra>",
        )
    fig.update_layout(barmode="stack", hovermode="closest", legend_traceorder="normal")
    fig.update_xaxes(title=None, dtick=2)
    fig.update_yaxes(showgrid=False)
    _style(fig, max(380, 24 * len(totals) + 90))

    table = (df.pivot_table(index="category_name", columns="asset_name", values="deals",
                            aggfunc="sum", fill_value=0)
             .assign(Total=lambda t: t.sum(axis=1)).sort_values("Total", ascending=False)
             .reset_index().rename(columns={"category_name": "Category"}))
    return Chart(fig,
                 f"{top_category} holds the most major MLS sponsorships: {top_n} of {all_deals}",
                 "Current deals by the sponsor's category, split by asset", table=table)


def stadium_by_seller() -> Chart | None:
    """Small multiples: stadium naming categories, club-sold vs venue-sold."""
    df = query("""
        SELECT sold_by, category_name, deals, share_of_seller, deals_list
        FROM mart_stadium_naming_by_seller
    """)
    if df.empty:
        return None
    n = df.groupby("sold_by")["deals"].sum()
    order = (df.pivot_table(index="category_name", columns="sold_by", values="deals",
                            aggfunc="sum", fill_value=0)
             .assign(total=lambda t: t.sum(axis=1))
             .sort_values(["total", "club"] if "club" in df["sold_by"].values else ["total"])
             .index.tolist())
    labels = {"club": f"Sold by the club ({int(n.get('club', 0))} deals)",
              "stadium_owner": f"Sold by the venue owner ({int(n.get('stadium_owner', 0))} deals)"}
    sellers = [s for s in ["club", "stadium_owner"] if s in n.index]

    fig = make_subplots(rows=1, cols=len(sellers), shared_yaxes=True, horizontal_spacing=0.04,
                        subplot_titles=[labels[s] for s in sellers])
    for i, (seller, color) in enumerate(zip(sellers, SERIES), start=1):
        part = df[df["sold_by"] == seller].set_index("category_name").reindex(order)
        fig.add_bar(
            y=order, x=part["deals"], orientation="h", name=labels[seller],
            marker={"color": color, "cornerradius": 3},
            customdata=part[["deals_list", "share_of_seller"]].fillna({"deals_list": "none"}),
            hovertemplate="<b>%{y}</b><br>%{x} deal(s), %{customdata[1]:.0%} of this seller<br>"
                          "%{customdata[0]}<extra></extra>",
            showlegend=False, row=1, col=i,
        )
    fig.update_xaxes(dtick=1, range=[0, df["deals"].max() + 0.5])
    fig.update_yaxes(showgrid=False)
    _style(fig, max(380, 26 * len(order) + 90))
    fig.update_annotations(font={"size": 13, "color": TEXT}, xanchor="left", x=None)
    for i, ann in enumerate(fig.layout.annotations):
        ann.update(x=fig.layout[f"xaxis{'' if i == 0 else i + 1}"].domain[0])

    club = df[df["sold_by"] == "club"].sort_values("deals", ascending=False)
    venue = df[df["sold_by"] == "stadium_owner"]
    fin = int(club[club["category_name"].isin(
        ["Banking & Financial Services", "Crypto & Fintech"])]["deals"].sum())
    title = (f"Clubs sell stadium names to finance brands most ({fin} of {int(n['club'])}); "
             f"the {int(n.get('stadium_owner', 0))} venue-sold names span "
             f"{venue['category_name'].nunique()} different categories")
    table = (df.assign(sold_by=df["sold_by"].map({"club": "Club", "stadium_owner": "Venue owner"}))
             .sort_values(["sold_by", "deals"], ascending=[True, False])
             [["sold_by", "category_name", "deals", "deals_list"]]
             .rename(columns={"sold_by": "Sold by", "category_name": "Category",
                              "deals": "Deals", "deals_list": "Deals (club)"}))
    return Chart(fig, title,
                 "Current stadium naming rights by sponsor category and who sold them",
                 note=("Venue-sold means the club plays in an NFL or university stadium whose "
                       "naming rights belong to the venue. With only a handful of such deals, "
                       "this describes today's set; it is too small to generalise from."),
                 table=table)


def club_explorer(default_club: str = "STL", days: int = 365) -> tuple[Chart, str] | None:
    """Daily pageviews, 28-day baseline and match days for every club, one at a time.

    Returns the chart and the HTML <select> that switches clubs (theme.js wires it).
    """
    df = query("""
        SELECT a.entity_id AS club_id, a.view_date, a.views, a.baseline_28d
        FROM mart_attention_daily AS a
        WHERE a.entity_type = 'club'
          AND a.view_date > (SELECT MAX(view_date) FROM mart_attention_daily) - ?::INTEGER
        ORDER BY a.entity_id, a.view_date
    """, [days])
    if df.empty:
        return None
    matches = query("""
        SELECT l.club_id, l.attention_date_utc, l.views, l.lift_vs_baseline,
               o.short_name AS opponent, l.venue
        FROM mart_match_day_lift AS l
        LEFT JOIN dim_club AS o ON o.club_id = l.opponent_club_id
        WHERE l.attention_date_utc >= ?
    """, [df["view_date"].min()])
    clubs = query("SELECT club_id, short_name FROM dim_club ORDER BY short_name")
    clubs = clubs[clubs["club_id"].isin(df["club_id"])]
    if default_club not in set(clubs["club_id"]):
        default_club = clubs["club_id"].iloc[0]

    fig = go.Figure()
    titles = {}
    for club_id, name in clubs.itertuples(index=False):
        visible = club_id == default_club
        d = df[df["club_id"] == club_id]
        m = matches[matches["club_id"] == club_id]
        fig.add_scatter(x=d["view_date"], y=d["views"], name="Daily pageviews", mode="lines",
                        line={"color": SERIES[0], "width": 1.5}, visible=visible,
                        legendgroup="views", meta=club_id,
                        hovertemplate="%{x|%b %-d, %Y}: %{y:,} views<extra></extra>")
        fig.add_scatter(x=d["view_date"], y=d["baseline_28d"], name="28-day baseline",
                        mode="lines", line={"color": MUTED, "width": 2, "dash": "dot"},
                        visible=visible, legendgroup="base", meta=club_id,
                        hovertemplate="Baseline: %{y:,.0f}<extra></extra>")
        fig.add_scatter(
            x=m["attention_date_utc"], y=m["views"], name="Match day", mode="markers",
            marker={"color": SERIES[1], "size": 8, "line": {"color": SURFACE, "width": 2}},
            visible=visible, legendgroup="match", meta=club_id,
            customdata=m[["opponent", "venue", "lift_vs_baseline"]],
            hovertemplate=("%{x|%b %-d}: %{customdata[1]} vs %{customdata[0]}<br>"
                           "%{y:,} views (%{customdata[2]:+.0%} vs baseline)<extra></extra>"))
        med = m["lift_vs_baseline"].median()
        titles[club_id] = (f"{possessive(name)} Wikipedia page gets {pct(med)} views on a typical match day"
                           if pd.notna(med) else f"{name}: daily Wikipedia pageviews")
    fig.update_layout(hovermode="closest")
    fig.update_yaxes(rangemode="tozero", title=None)
    _style(fig, 420)

    options = "".join(
        f"<option value='{c}'{' selected' if c == default_club else ''}>{escape(n)}</option>"
        for c, n in clubs.itertuples(index=False))
    select = (f"<div class='viz-controls'><label for='club-select'>Club</label>"
              f"<select id='club-select' class='form-select' data-target='club-explorer' "
              f"data-titles='{escape(json.dumps(titles))}'>{options}</select></div>")
    return (Chart(fig, titles[default_club],
                  f"Last {days} days. Dots are match days; the dotted line is the average of "
                  "the 28 days before each day"), select)


def club_match_lift(season: int | None = None) -> Chart | None:
    """Dumbbell: each club's median match-day lift, home and away, for one season."""
    df = query("""
        SELECT l.season, c.short_name, l.matches,
               l.median_lift, l.median_lift_home, l.median_lift_away
        FROM mart_club_match_lift AS l
        JOIN dim_club AS c USING (club_id)
        WHERE l.season = COALESCE(?, (SELECT MAX(season) FROM mart_club_match_lift))
        ORDER BY l.median_lift
    """, [season])
    if df.empty:
        return None
    season = int(df["season"].iloc[0])

    fig = go.Figure()
    # One connector trace (None breaks the line between clubs) keeps the figure light.
    xs, ys = [], []
    for r in df.itertuples():
        xs += [r.median_lift_away, r.median_lift_home, None]
        ys += [r.short_name, r.short_name, None]
    fig.add_scatter(x=xs, y=ys, mode="lines", line={"color": GRID, "width": 3},
                    hoverinfo="skip", showlegend=False)
    for col, name, color in [("median_lift_away", "Away", SERIES[0]),
                             ("median_lift_home", "Home", SERIES[1])]:
        fig.add_scatter(x=df[col], y=df["short_name"], name=name, mode="markers",
                        marker={"color": color, "size": 10, "line": {"color": SURFACE, "width": 2}},
                        hovertemplate="%{y} " + name.lower() + ": %{x:+.0%}<extra></extra>")
    fig.add_scatter(x=df["median_lift"], y=df["short_name"], name="All matches", mode="markers",
                    marker={"color": TEXT, "size": 12, "symbol": "line-ns",
                            "line": {"color": TEXT, "width": 2}},
                    customdata=df["matches"],
                    hovertemplate="%{y}: %{x:+.0%} across %{customdata} matches<extra></extra>")
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(tickformat="+.0%", zeroline=True, zerolinecolor=MUTED)
    fig.update_yaxes(showgrid=False)
    _style(fig, 22 * len(df) + 110)

    top, bottom = df.iloc[-1], df.iloc[0]
    table = (df.sort_values("median_lift", ascending=False)
             .assign(**{c: lambda t, c=c: t[c].map(lambda v: "" if pd.isna(v) else pct(v))
                        for c in ["median_lift", "median_lift_home", "median_lift_away"]})
             [["short_name", "matches", "median_lift", "median_lift_home", "median_lift_away"]]
             .rename(columns={"short_name": "Club", "matches": "Matches",
                              "median_lift": "All", "median_lift_home": "Home",
                              "median_lift_away": "Away"}))
    return Chart(fig,
                 f"{possessive(top.short_name)} Wikipedia page gets the biggest match-day bump in "
                 f"{season} ({pct(top.median_lift)}); {possessive(bottom.short_name)} gets the "
                 f"smallest ({pct(bottom.median_lift)})",
                 "Median match day vs the prior 28-day average, completed matches only",
                 table=table)


RESULT_LABELS = {"win": "Win", "draw": "Draw", "loss": "Loss"}


def lift_by_result() -> Chart | None:
    """Grouped bars: median match-day lift after a win, draw or loss, home vs away."""
    df = query("SELECT result, venue, matches, median_lift FROM mart_lift_by_result")
    if df.empty:
        return None
    order = ["win", "draw", "loss"]

    fig = go.Figure()
    for venue, color in [("home", SERIES[1]), ("away", SERIES[0])]:
        part = df[df["venue"] == venue].set_index("result").reindex(order)
        fig.add_bar(
            x=[RESULT_LABELS[r] for r in order], y=part["median_lift"], name=venue.title(),
            marker={"color": color, "line": {"color": SURFACE, "width": 2}, "cornerradius": 4},
            text=[pct(v) for v in part["median_lift"]], textposition="outside",
            textfont={"color": TEXT}, cliponaxis=False,
            customdata=part["matches"],
            hovertemplate=venue.title() + " %{x}: %{y:+.0%} (%{customdata:,} matches)<extra></extra>",
        )
    fig.update_layout(barmode="group", bargroupgap=0.08)
    fig.update_yaxes(tickformat="+.0%", rangemode="tozero", dtick=0.1)
    fig.update_xaxes(showgrid=False)
    _style(fig, 380)

    home = df[df["venue"] == "home"].set_index("result")["median_lift"]
    seasons = query("SELECT MIN(season), MAX(season) FROM mart_match_day_lift").iloc[0]
    title = (f"A home win draws more attention ({pct(home['win'])}) than a home loss "
             f"({pct(home['loss'])})" if home["win"] > home["loss"]
             else "Match-day attention by result")
    table = (df.assign(result=df["result"].map(RESULT_LABELS), venue=df["venue"].str.title(),
                       median_lift=df["median_lift"].map(pct))
             .rename(columns={"result": "Result", "venue": "Venue", "matches": "Club-matches",
                              "median_lift": "Median lift"}))
    return Chart(fig, title,
                 f"Median match-day lift by the club's own result, all clubs, "
                 f"{seasons.iloc[0]} to {seasons.iloc[1]}",
                 note=("A pageview day covers the whole UTC day, including the hours before "
                       "kickoff, so this compares match days by result. It doesn't show that "
                       "the result caused the extra views."),
                 table=table)


def attention_by_season() -> Chart | None:
    """Diverging ranked bars: each club's change in average daily views vs last year."""
    df = query("""
        SELECT s.season, c.short_name, s.avg_daily_views, s.prev_avg_daily_views,
               s.change_vs_prev
        FROM mart_attention_by_season AS s
        JOIN dim_club AS c USING (club_id)
        WHERE s.season = (SELECT MAX(season) FROM mart_attention_by_season)
          AND s.change_vs_prev IS NOT NULL
        ORDER BY s.change_vs_prev
    """)
    if df.empty:
        return None
    season = int(df["season"].iloc[0])
    through = query("SELECT MAX(view_date) FROM mart_attention_daily").iloc[0, 0]

    fig = go.Figure()
    fig.add_bar(
        y=df["short_name"], x=df["change_vs_prev"], orientation="h",
        marker={"color": [SERIES[0] if v >= 0 else NEGATIVE for v in df["change_vs_prev"]],
                "cornerradius": 3},
        customdata=df[["avg_daily_views", "prev_avg_daily_views"]],
        hovertemplate=(f"<b>%{{y}}</b>: %{{x:+.0%}}<br>{season}: %{{customdata[0]:,.0f}} a day<br>"
                       f"{season - 1}: %{{customdata[1]:,.0f}} a day<extra></extra>"),
        showlegend=False,
    )
    fig.update_xaxes(tickformat="+.0%", zeroline=True, zerolinecolor=MUTED, zerolinewidth=1)
    fig.update_yaxes(showgrid=False)
    _style(fig, 21 * len(df) + 80)

    up = int((df["change_vs_prev"] > 0).sum())
    top = df.iloc[-1]
    table = (df.sort_values("change_vs_prev", ascending=False)
             .assign(avg_daily_views=df["avg_daily_views"].round(0).astype(int),
                     prev_avg_daily_views=df["prev_avg_daily_views"].round(0).astype(int),
                     change_vs_prev=df["change_vs_prev"].map(pct))
             [["short_name", "avg_daily_views", "prev_avg_daily_views", "change_vs_prev"]]
             .rename(columns={"short_name": "Club", "avg_daily_views": f"{season} views/day",
                              "prev_avg_daily_views": f"{season - 1} views/day",
                              "change_vs_prev": "Change"}))
    return Chart(fig,
                 f"{up} of {len(df)} clubs get more Wikipedia views than last year; "
                 f"{top.short_name} is up most ({pct(top.change_vs_prev)})",
                 f"Average daily pageviews, Jan 1 to {through:%b %-d}, {season} vs {season - 1}. "
                 "Blue is up, red is down",
                 note=("Each year is compared over the same calendar window, so a partial "
                       "season isn't compared with a full one."),
                 table=table)


def _sign_test_p(k: int, n: int) -> float:
    """Two-sided exact binomial test of k successes in n trials at p = 0.5."""
    if n == 0:
        return 1.0
    tail = sum(math.comb(n, i) for i in range(0, min(k, n - k) + 1)) / 2 ** n
    return min(1.0, 2 * tail)


def _bh_q(p: pd.Series) -> pd.Series:
    """Benjamini-Hochberg adjusted p-values (false discovery rate)."""
    order = p.sort_values()
    m = len(order)
    q = (order * m / range(1, m + 1))[::-1].cummin()[::-1].clip(upper=1)
    return q.reindex(p.index)


def sponsor_match_day_tests() -> pd.DataFrame:
    """One row per club x sponsor brand with its sign test, FDR-adjusted, and group."""
    df = query("""
        SELECT m.*, b.brand_name, c.short_name
        FROM mart_sponsor_match_day_attention AS m
        JOIN dim_brand AS b USING (brand_id)
        JOIN dim_club  AS c USING (club_id)
        WHERE m.match_days >= 10
    """)
    if df.empty:
        return df
    df["p"] = [_sign_test_p(int(k), int(n)) for k, n in zip(df["days_above_norm"], df["match_days"])]
    df["q"] = _bh_q(df["p"])
    df["share_above"] = df["days_above_norm"] / df["match_days"]
    df["label"] = df["brand_name"] + " · " + df["short_name"]
    df = df.sort_values("median_excess_lift").reset_index(drop=True)
    df["group"] = "No clear difference"
    df.loc[(df["q"] < 0.10) & (df["median_excess_lift"] > 0), "group"] = "Reliably higher"
    df.loc[(df["q"] < 0.10) & (df["median_excess_lift"] < 0), "group"] = "Reliably lower"
    return df


def sponsor_match_day() -> Chart | None:
    """Ranked dots: each sponsor brand's weekday-adjusted match-day attention."""
    df = sponsor_match_day_tests()
    if df.empty:
        return None

    fig = go.Figure()
    for group, color, size in [("No clear difference", MUTED, 9),
                               ("Reliably higher", SERIES[0], 12),
                               ("Reliably lower", NEGATIVE, 12)]:
        part = df[df["group"] == group]
        if part.empty:
            continue
        fig.add_scatter(
            x=part["median_excess_lift"], y=part["label"], mode="markers", name=group,
            marker={"color": color, "size": size, "line": {"color": SURFACE, "width": 2}},
            customdata=part[["assets", "match_days", "share_above", "avg_daily_views", "q"]],
            hovertemplate=("<b>%{y}</b> (%{customdata[0]})<br>"
                           "Median match day vs same-weekday norm: %{x:+.0%}<br>"
                           "%{customdata[2]:.0%} of %{customdata[1]} match days above the norm<br>"
                           "Typical day: %{customdata[3]:,.0f} views · adjusted p = %{customdata[4]:.2f}"
                           "<extra></extra>"))
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(tickformat="+.0%", zeroline=True, zerolinecolor=MUTED, zerolinewidth=1.5)
    fig.update_yaxes(showgrid=False, tickfont={"size": 11})
    fig.update_yaxes(categoryorder="array", categoryarray=df["label"].tolist())
    _style(fig, 17 * len(df) + 110)

    nominal = int((df["p"] < 0.05).sum())
    expected = 0.05 * len(df)
    higher = df[df["group"] == "Reliably higher"].sort_values("median_excess_lift", ascending=False)
    lower = df[df["group"] == "Reliably lower"]
    n_none = int((df["group"] == "No clear difference").sum())
    title = (f"Once weekends are accounted for, {n_none} of {len(df)} sponsors show no clear "
             "match-day difference")
    if len(higher):
        names = [f"{r.brand_name} ({r.short_name})" for r in higher.head(3).itertuples()]
        title += (f". Biggest bumps: {', '.join(names[:-1])} and {names[-1]}"
                  if len(names) > 1 else f". The exception: {names[0]}")
    table = (df.sort_values("median_excess_lift", ascending=False)
             .assign(median_excess_lift=lambda t: t["median_excess_lift"].map(pct),
                     share_above=lambda t: t["share_above"].map("{:.0%}".format),
                     avg_daily_views=lambda t: t["avg_daily_views"].round(0).astype(int),
                     q=lambda t: t["q"].map("{:.3f}".format))
             [["brand_name", "short_name", "assets", "match_days", "median_excess_lift",
               "share_above", "avg_daily_views", "q"]]
             .rename(columns={"brand_name": "Brand", "short_name": "Club", "assets": "Assets",
                              "match_days": "Match days", "median_excess_lift": "Median vs norm",
                              "share_above": "Days above norm", "avg_daily_views": "Views/day",
                              "q": "Adjusted p"}))
    return Chart(fig, title,
                 "Each sponsor brand's Wikipedia views on its club's match days, compared with "
                 "its own non-match days on the same weekday during the deal",
                 note=((f"{int(higher['assets'].str.contains('Stadium').sum())} of the {len(higher)} "
                        "brands with a reliable bump are stadium names, where the venue carries "
                        "the brand's name; fans looking up the venue may land on the brand's page. "
                        "That is a hypothesis, not something this test shows. "
                        if len(higher) else "")
                       + f"Sign test per brand, adjusted for testing {len(df)} brands at once "
                       f"(Benjamini-Hochberg, 10% false discovery rate). {nominal} brands pass a "
                       f"plain 5% test, against about {expected:.0f} expected by chance alone, "
                       "which is why the adjustment matters. "
                       + (f"{len(lower)} brands sit reliably below their norm on match days; with "
                          "no obvious mechanism, treat those as a prompt to look closer, not a "
                          "finding. " if len(lower) else "")
                       + "Brands with fewer than 10 match days are left out. Public attention "
                       "only, not sponsorship value."),
                 table=table)


def weekend_effect() -> Chart | None:
    """Two panels: when matches happen (UTC weekday) and how brand pages move by weekday."""
    df = query("""
        WITH matches AS (
            SELECT DAYOFWEEK(attention_date_utc) AS wd, COUNT(DISTINCT match_id) AS n
            FROM mart_match_day_lift GROUP BY 1
        ),
        brands AS (
            SELECT DAYOFWEEK(view_date) AS wd, MEDIAN(lift_vs_baseline) AS lift
            FROM mart_attention_daily
            WHERE entity_type = 'brand' AND lift_vs_baseline IS NOT NULL
            GROUP BY 1
        )
        SELECT b.wd, COALESCE(m.n, 0) AS matches, b.lift
        FROM brands AS b LEFT JOIN matches AS m USING (wd)
        ORDER BY (b.wd + 6) % 7
    """)
    if df.empty:
        return None
    names = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    df["day"] = df["wd"].map(lambda d: names[int(d)])
    df["share"] = df["matches"] / df["matches"].sum()

    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.12,
                        subplot_titles=["Share of MLS matches, by the UTC day they are played",
                                        "Typical sponsor-brand page vs its 28-day average"])
    fig.add_bar(x=df["day"], y=df["share"], marker={"color": SERIES[1], "cornerradius": 3},
                customdata=df["matches"], showlegend=False, row=1, col=1,
                hovertemplate="%{x}: %{y:.0%} of matches (%{customdata:,})<extra></extra>")
    fig.add_bar(x=df["day"], y=df["lift"], showlegend=False, row=1, col=2,
                marker={"color": [SERIES[0] if v >= 0 else NEGATIVE for v in df["lift"]],
                        "cornerradius": 3},
                hovertemplate="%{x}: %{y:+.0%} vs 28-day average<extra></extra>")
    fig.update_yaxes(tickformat=".0%", row=1, col=1)
    fig.update_yaxes(tickformat="+.0%", zeroline=True, zerolinecolor=MUTED, row=1, col=2)
    fig.update_xaxes(showgrid=False)
    _style(fig, 300)
    fig.update_annotations(font={"size": 13, "color": TEXT})
    fig.update_layout(margin={"t": 48})

    weekend = df[df["day"].isin(["Sat", "Sun"])]
    return Chart(fig,
                 f"{weekend['share'].sum():.0%} of matches fall on a UTC weekend, exactly when "
                 f"company pages get fewer views ({pct(weekend['lift'].median())})",
                 "Why a naive match-day comparison makes sponsors look ignored on match day")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "_preview"
    out.mkdir(exist_ok=True)
    explorer = club_explorer()
    charts = [("landscape", category_landscape()), ("stadium", stadium_by_seller()),
              ("attention", explorer[0] if explorer else None),
              ("match_lift", club_match_lift()), ("result", lift_by_result()),
              ("season", attention_by_season()), ("sponsor", sponsor_match_day()),
              ("weekend", weekend_effect())]
    for name, chart in charts:
        if chart is not None:
            chart.fig.update_layout(title=chart.title)
            chart.fig.write_html(out / f"{name}.html", include_plotlyjs=True)
            print(f"wrote {out / name}.html  |  {chart.title}")
