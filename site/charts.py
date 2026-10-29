"""Plot setup for the site: data access and the two Plotly charts.

Kept out of index.qmd so the page stays readable and the charts can be
tested on their own (python site/charts.py writes both to site/_preview/).
"""

from pathlib import Path

import duckdb
import pandas as pd
import plotly.graph_objects as go

DB_PATH = Path(__file__).resolve().parent.parent / "tracker.duckdb"

# Colors: categorical slots 1-3 of a palette validated for color-vision
# deficiency, plus muted ink for secondary lines and text.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a"]
MUTED = "#8a8984"
TEXT = "#0b0b0b"
TEXT_2 = "#52514e"
GRID = "#e8e7e3"
SURFACE = "#fcfcfb"


def query(sql: str, params: list | None = None) -> pd.DataFrame:
    """Run a read-only query against the warehouse built by python/build.py."""
    with duckdb.connect(str(DB_PATH), read_only=True) as con:
        return con.execute(sql, params or []).fetchdf()


def _base_layout(fig: go.Figure, title: str, subtitle: str) -> go.Figure:
    fig.update_layout(
        title={"text": f"{title}<br><sup style='color:{TEXT_2}'>{subtitle}</sup>",
               "x": 0, "xanchor": "left", "font": {"size": 18, "color": TEXT}},
        plot_bgcolor=SURFACE, paper_bgcolor=SURFACE,
        font={"family": "system-ui, sans-serif", "color": TEXT_2, "size": 13},
        margin={"l": 10, "r": 10, "t": 80, "b": 40},
        hoverlabel={"bgcolor": "white", "font_color": TEXT},
        legend={"orientation": "h", "y": -0.15, "x": 0, "traceorder": "normal"},
    )
    fig.update_xaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    fig.update_yaxes(gridcolor=GRID, zeroline=False, linecolor=GRID)
    return fig


def category_landscape() -> go.Figure | None:
    """Horizontal stacked bars: current deals per category, split by asset."""
    df = query("""
        SELECT category_name, asset_name, deals
        FROM mart_category_share
    """)
    if df.empty:
        return None

    totals = df.groupby("category_name")["deals"].sum().sort_values()
    top_category, top_n = totals.index[-1], int(totals.iloc[-1])
    all_deals = int(totals.sum())

    fig = go.Figure()
    assets = ["Front-of-kit partner", "Sleeve partner", "Stadium naming rights"]
    present = [a for a in assets if a in set(df["asset_name"])]
    for color, asset in zip(SERIES, assets):
        if asset not in present:
            continue  # keep each asset's color fixed even when one is missing
        part = df[df["asset_name"] == asset].set_index("category_name").reindex(totals.index)
        fig.add_bar(
            y=totals.index, x=part["deals"].fillna(0), name=asset, orientation="h",
            marker={"color": color, "line": {"color": SURFACE, "width": 2}},
            hovertemplate="%{y}<br>" + asset + ": %{x}<extra></extra>",
        )
    fig.update_layout(barmode="stack", height=max(360, 28 * len(totals) + 140))
    return _base_layout(
        fig,
        f"{top_category} holds the most major MLS sponsorships ({top_n} of {all_deals})",
        f"Current deals by sponsor category: {', '.join(a.lower() for a in present)}",
    )


def club_attention(club_id: str, days: int = 365) -> go.Figure | None:
    """Daily pageviews for one club, its 28-day baseline, and match days."""
    df = query("""
        SELECT view_date, views, baseline_28d
        FROM mart_attention_daily
        WHERE entity_type = 'club' AND entity_id = ?
          AND view_date > (SELECT MAX(view_date) FROM mart_attention_daily) - ?::INTEGER
        ORDER BY view_date
    """, [club_id, days])
    if df.empty:
        return None
    matches = query("""
        SELECT l.match_date_utc, l.views, l.lift_vs_baseline, o.short_name AS opponent, l.venue
        FROM mart_match_day_lift AS l
        LEFT JOIN dim_club AS o ON o.club_id = l.opponent_club_id
        WHERE l.club_id = ? AND l.match_date_utc >= ?
    """, [club_id, df["view_date"].min()])
    club = query("SELECT short_name FROM dim_club WHERE club_id = ?", [club_id]).iloc[0, 0]

    fig = go.Figure()
    fig.add_scatter(x=df["view_date"], y=df["views"], name="Daily pageviews", mode="lines",
                    line={"color": SERIES[0], "width": 2},
                    hovertemplate="%{x|%b %d, %Y}: %{y:,} views<extra></extra>")
    fig.add_scatter(x=df["view_date"], y=df["baseline_28d"], name="28-day baseline", mode="lines",
                    line={"color": MUTED, "width": 2, "dash": "dot"},
                    hovertemplate="Baseline: %{y:,.0f}<extra></extra>")
    if not matches.empty:
        fig.add_scatter(
            x=matches["match_date_utc"], y=matches["views"], name="Match day", mode="markers",
            marker={"color": SERIES[1], "size": 9, "line": {"color": SURFACE, "width": 2}},
            customdata=matches[["opponent", "venue", "lift_vs_baseline"]],
            hovertemplate=("%{x|%b %d}: %{customdata[1]} vs %{customdata[0]}<br>"
                           "%{y:,} views (%{customdata[2]:+.0%} vs baseline)<extra></extra>"),
        )
    fig.update_layout(height=420, hovermode="closest")
    fig.update_yaxes(rangemode="tozero", title=None)

    median_lift = matches["lift_vs_baseline"].median() if not matches.empty else None
    title = (f"{club}'s Wikipedia page gets {median_lift:+.0%} views on a typical match day"
             if median_lift is not None and pd.notna(median_lift)
             else f"{club}: daily Wikipedia pageviews")
    return _base_layout(fig, title, f"Last {days} days. Median match day vs the prior 28-day average")


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "_preview"
    out.mkdir(exist_ok=True)
    for name, fig in [("landscape", category_landscape()), ("attention", club_attention("STL"))]:
        if fig is not None:
            fig.write_html(out / f"{name}.html", include_plotlyjs=True)
            print(f"wrote {out / name}.html")
