"""Plot setup for the site: data access, the Plotly charts and the sponsor table.

Kept out of index.qmd so the page stays readable and the charts can be
tested on their own (python site/charts.py writes them to site/_preview/).
"""

from html import escape
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


RESULT_LABELS = {"win": "Win", "draw": "Draw", "loss": "Loss"}


def sponsor_directory() -> str | None:
    """HTML table: one row per club with its current kit partners and source."""
    df = query("""
        SELECT short_name, conference,
               front_of_kit_brand, front_of_kit_category,
               sleeve_brand, sleeve_category,
               source_url, date_checked
        FROM mart_sponsor_directory
        ORDER BY conference, short_name
    """)
    if df.empty:
        return None

    def cell(brand, category) -> str:
        if brand is None or pd.isna(brand):
            return f"<td style='color:{MUTED}'>Not recorded</td>"
        return (f"<td>{escape(brand)}<br>"
                f"<small style='color:{TEXT_2}'>{escape(category or '')}</small></td>")

    rows = []
    for r in df.itertuples():
        source = (f"<a href='{escape(r.source_url)}'>source</a>, "
                  f"checked {r.date_checked:%b %d, %Y}" if pd.notna(r.source_url) else "")
        rows.append(f"<tr><td><strong>{escape(r.short_name)}</strong><br>"
                    f"<small style='color:{TEXT_2}'>{escape(r.conference)}</small></td>"
                    f"{cell(r.front_of_kit_brand, r.front_of_kit_category)}"
                    f"{cell(r.sleeve_brand, r.sleeve_category)}"
                    f"<td><small>{source}</small></td></tr>")
    return ("<table class='table table-sm'><thead><tr><th>Club</th><th>Front of kit</th>"
            "<th>Sleeve</th><th>Source</th></tr></thead><tbody>"
            + "".join(rows) + "</tbody></table>")


def club_match_lift(season: int | None = None) -> go.Figure | None:
    """Dot plot: each club's median match-day lift, home and away, for one season."""
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
    # Thin line from away to home dot, so the gap between them reads at a glance.
    for r in df.itertuples():
        fig.add_scatter(x=[r.median_lift_away, r.median_lift_home], y=[r.short_name] * 2,
                        mode="lines", line={"color": GRID, "width": 3},
                        hoverinfo="skip", showlegend=False)
    for col, name, color in [("median_lift_away", "Away", SERIES[0]),
                             ("median_lift_home", "Home", SERIES[1])]:
        fig.add_scatter(x=df[col], y=df["short_name"], name=name, mode="markers",
                        marker={"color": color, "size": 9, "line": {"color": SURFACE, "width": 1}},
                        hovertemplate="%{y} " + name.lower() + ": %{x:+.0%}<extra></extra>")
    fig.add_scatter(x=df["median_lift"], y=df["short_name"], name="All matches", mode="markers",
                    marker={"color": TEXT, "size": 7, "symbol": "line-ns",
                            "line": {"color": TEXT, "width": 2}},
                    customdata=df["matches"],
                    hovertemplate="%{y}: %{x:+.0%} across %{customdata} matches<extra></extra>")
    fig.update_layout(height=28 * len(df) + 160, hovermode="closest")
    fig.update_xaxes(tickformat="+.0%", zeroline=True, zerolinecolor=MUTED)

    top = df.iloc[-1]
    fig = _base_layout(
        fig,
        f"{top.short_name}'s Wikipedia page gets the biggest match-day bump in {season} "
        f"({top.median_lift:+.0%})",
        "Median match day vs the prior 28-day average, completed matches only",
    )
    fig.update_layout(legend={"y": -0.06})  # tall chart: keep the legend close to the axis
    return fig


def lift_by_result() -> go.Figure | None:
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
            marker={"color": color, "line": {"color": SURFACE, "width": 2}},
            text=[f"{v:+.0%}" for v in part["median_lift"]], textposition="outside",
            customdata=part["matches"],
            hovertemplate=venue.title() + " %{x}: %{y:+.0%} (%{customdata:,} matches)<extra></extra>",
        )
    fig.update_layout(barmode="group", height=400)
    fig.update_yaxes(tickformat="+.0%", rangemode="tozero")

    home = df[df["venue"] == "home"].set_index("result")["median_lift"]
    seasons = query("SELECT MIN(season), MAX(season) FROM mart_match_day_lift").iloc[0]
    title = (f"A home win draws more attention ({home['win']:+.0%}) than a home loss "
             f"({home['loss']:+.0%})" if home["win"] > home["loss"]
             else "Match-day attention by result")
    return _base_layout(fig, title,
                        f"Median match-day lift by the club's result, all clubs, "
                        f"{seasons.iloc[0]} to {seasons.iloc[1]}")


def attention_by_season() -> go.Figure | None:
    """Ranked bars: each club's change in average daily views, this season vs last."""
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
        marker={"color": [SERIES[0] if v >= 0 else SERIES[1] for v in df["change_vs_prev"]]},
        customdata=df[["avg_daily_views", "prev_avg_daily_views"]],
        hovertemplate=(f"%{{y}}: %{{x:+.0%}}<br>{season}: %{{customdata[0]:,.0f}} a day<br>"
                       f"{season - 1}: %{{customdata[1]:,.0f}} a day<extra></extra>"),
        showlegend=False,
    )
    fig.update_layout(height=24 * len(df) + 160)
    fig.update_xaxes(tickformat="+.0%", zeroline=True, zerolinecolor=MUTED)

    up = int((df["change_vs_prev"] > 0).sum())
    top = df.iloc[-1]
    return _base_layout(
        fig,
        f"{up} of {len(df)} clubs get more Wikipedia views than last year; "
        f"{top.short_name} is up most ({top.change_vs_prev:+.0%})",
        f"Average daily pageviews, Jan 1 to {through:%b %d}, {season} vs {season - 1}",
    )


if __name__ == "__main__":
    out = Path(__file__).resolve().parent / "_preview"
    out.mkdir(exist_ok=True)
    figs = [("landscape", category_landscape()), ("attention", club_attention("STL")),
            ("match_lift", club_match_lift()), ("result", lift_by_result()),
            ("season", attention_by_season())]
    for name, fig in figs:
        if fig is not None:
            fig.write_html(out / f"{name}.html", include_plotlyjs=True)
            print(f"wrote {out / name}.html")
