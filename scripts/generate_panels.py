from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "github-history.json"
ASSETS_DIR = ROOT / "assets"

# ============================================================
# DESIGN SYSTEM
# ============================================================

BG = "#05070A"
PANEL = "#0A0E13"
PANEL_ALT = "#0D1218"
BORDER = "#202832"

TEXT = "#E8EDF2"
MUTED = "#77828D"

GREEN = "#57E6B1"
BLUE = "#6AA8FF"


# ============================================================
# HELPERS
# ============================================================

def esc(value: object) -> str:
    return html.escape(str(value))


def load_history() -> dict:
    if not DATA_FILE.exists():
        return {"snapshots": []}

    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def latest_snapshot(history: dict) -> dict:
    snapshots = history.get("snapshots", [])

    if not snapshots:
        return {}

    return snapshots[-1]


def text(
    x: float,
    y: float,
    value: str,
    size: int = 12,
    color: str = TEXT,
    weight: str = "400",
    anchor: str = "start",
    spacing: float = 0,
) -> str:
    return f"""
<text
    x="{x}"
    y="{y}"
    fill="{color}"
    font-family="monospace"
    font-size="{size}px"
    font-weight="{weight}"
    text-anchor="{anchor}"
    letter-spacing="{spacing}px">
    {esc(value)}
</text>
"""


def line(
    x1: float,
    y1: float,
    x2: float,
    y2: float,
    color: str = BORDER,
    width: int = 1,
) -> str:
    return f"""
<line
    x1="{x1}"
    y1="{y1}"
    x2="{x2}"
    y2="{y2}"
    stroke="{color}"
    stroke-width="{width}"/>
"""

def svg_end() -> str:
    return "</svg>\n"


def box(
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str = PANEL_ALT,
    stroke: str = BORDER,
    radius: int = 8,
) -> str:
    return f"""
<rect
    x="{x}"
    y="{y}"
    width="{width}"
    height="{height}"
    rx="{radius}"
    fill="{fill}"
    stroke="{stroke}"
    stroke-width="1"/>
"""


# ============================================================
# ACTIVITY CHART
# ============================================================

def activity_points(
    snapshots: list[dict],
    left: float,
    top: float,
    width: float,
    height: float,
) -> tuple[list[tuple[float, float]], int]:

    values = [
        int(
            snapshot.get(
                "activity",
                {},
            ).get(
                "activity_index",
                0,
            )
        )
        for snapshot in snapshots
    ]

    if not values:
        values = [0]

    maximum = max(values)

    if maximum <= 5:
        chart_max = 5
    elif maximum <= 10:
        chart_max = 10
    elif maximum <= 25:
        chart_max = 25
    elif maximum <= 50:
        chart_max = 50
    else:
        chart_max = 100

    points = []

    for index, value in enumerate(values):
        if len(values) == 1:
            x = left + width / 2
        else:
            x = left + (
                index / (len(values) - 1)
            ) * width

        y = (
            top
            + height
            - (
                value / chart_max
            ) * height
        )

        points.append((x, y))

    return points, chart_max


# ============================================================
# MAIN SVG
# ============================================================

def generate_control_room(
    history: dict,
) -> None:

    latest = latest_snapshot(history)

    snapshots = history.get(
        "snapshots",
        [],
    )

    repositories = latest.get(
        "repository_count",
        0,
    )

    active_repositories = latest.get(
        "active_repository_count",
        0,
    )

    stars = latest.get(
        "stars",
        0,
    )

    forks = latest.get(
        "forks",
        0,
    )

    activity = latest.get(
        "activity",
        {},
    )

    activity_index = activity.get(
        "activity_index",
        0,
    )

    commits = activity.get(
        "commits",
        0,
    )

    pull_requests = activity.get(
        "pull_requests",
        0,
    )

    issues = activity.get(
        "issues",
        0,
    )

    # --------------------------------------------------------
    # Canvas
    # --------------------------------------------------------

    width = 1100
    height = 650

    output = f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">

<title>ZENZIZENZIC // CONTROL ROOM</title>

<rect
    width="100%"
    height="100%"
    rx="18"
    fill="{BG}"/>

<rect
    x="1"
    y="1"
    width="{width - 2}"
    height="{height - 2}"
    rx="18"
    fill="none"
    stroke="{BORDER}"
    stroke-width="2"/>
"""

    # ========================================================
    # HEADER
    # ========================================================

    output += f"""
<rect
    x="24"
    y="24"
    width="{width - 48}"
    height="92"
    rx="12"
    fill="{PANEL}"
    stroke="{BORDER}"
    stroke-width="1"/>
"""

    output += text(
        48,
        58,
        "ZENZIZENZIC // CONTROL ROOM",
        24,
        TEXT,
        "700",
        spacing=1.5,
    )

    output += text(
        48,
        84,
        "BUILD  ·  RESEARCH  ·  ANALYZE  ·  EXPERIMENT",
        10,
        MUTED,
        "700",
        spacing=1,
    )

    output += f"""
<circle
    cx="{width - 72}"
    cy="56"
    r="6"
    fill="{GREEN}"/>
"""

    output += text(
        width - 56,
        60,
        "LIVE",
        10,
        GREEN,
        "700",
        spacing=1,
    )

    output += text(
        width - 48,
        86,
        "GITHUB",
        9,
        BLUE,
        "700",
        "end",
        1,
    )

    # ========================================================
    # METRIC STRIP
    # ========================================================

    metric_y = 140
    metric_w = 244
    metric_h = 92
    gap = 8
    start_x = 24

    metrics = [
        ("REPOSITORIES", repositories, GREEN),
        ("ACTIVE", active_repositories, GREEN),
        ("STARS", stars, BLUE),
        ("ACTIVITY INDEX", f"{activity_index}/100", GREEN),
    ]

    for index, (
        label,
        value,
        color,
    ) in enumerate(metrics):

        x = start_x + (
            index * (
                metric_w + gap
            )
        )

        output += box(
            x,
            metric_y,
            metric_w,
            metric_h,
        )

        output += text(
            x + 18,
            metric_y + 28,
            label,
            9,
            MUTED,
            "700",
            spacing=1,
        )

        output += text(
            x + 18,
            metric_y + 64,
            str(value),
            22,
            color,
            "700",
        )

    # ========================================================
    # ACTIVITY MARKET
    # ========================================================

    chart_x = 24
    chart_y = 254
    chart_w = 720
    chart_h = 210

    output += box(
        chart_x,
        chart_y,
        chart_w,
        chart_h,
    )

    output += text(
        chart_x + 20,
        chart_y + 28,
        "GITHUB ACTIVITY",
        11,
        TEXT,
        "700",
        spacing=1,
    )

    output += text(
        chart_x + chart_w - 20,
        chart_y + 28,
        "DERIVED SIGNAL",
        8,
        GREEN,
        "700",
        "end",
        1,
    )

    plot_left = chart_x + 20
    plot_top = chart_y + 52
    plot_w = chart_w - 40
    plot_h = 118

    points, chart_max = activity_points(
        snapshots,
        plot_left,
        plot_top,
        plot_w,
        plot_h,
    )

    for level in range(5):

        fraction = (
            level / 4
        )

        y = (
            plot_top
            + (
                fraction
                * plot_h
            )
        )

        value = int(
            chart_max
            - (
                fraction
                * chart_max
            )
        )

        output += line(
            plot_left,
            y,
            plot_left + plot_w,
            y,
            BORDER,
        )

        output += text(
            plot_left - 8,
            y + 4,
            str(value),
            8,
            MUTED,
            "700",
            "end",
        )

    polyline = " ".join(
        f"{x:.1f},{y:.1f}"
        for x, y in points
    )

    output += f"""
<polyline
    points="{polyline}"
    fill="none"
    stroke="{GREEN}"
    stroke-width="3"
    stroke-linecap="round"
    stroke-linejoin="round"/>
"""

    for index, (
        x,
        y,
    ) in enumerate(points):

        value = int(
            snapshots[index]
            .get(
                "activity",
                {},
            )
            .get(
                "activity_index",
                0,
            )
        )

        date = snapshots[index].get(
            "date",
            "",
        )

        output += f"""
<circle
    cx="{x:.1f}"
    cy="{y:.1f}"
    r="3.5"
    fill="{GREEN}">
    <title>
        {esc(date)}
        · Activity {value}/100
    </title>
</circle>
"""

    output += text(
        chart_x + 20,
        chart_y + 191,
        f"{len(snapshots)} SNAPSHOTS  ·  VISUAL RANGE 0–{chart_max}",
        8,
        MUTED,
        "700",
        spacing=1,
    )

    # ========================================================
    # TELEMETRY
    # ========================================================

    telemetry_x = 752
    telemetry_y = 254
    telemetry_w = 324
    telemetry_h = 210

    output += box(
        telemetry_x,
        telemetry_y,
        telemetry_w,
        telemetry_h,
    )

    output += text(
        telemetry_x + 20,
        telemetry_y + 28,
        "TELEMETRY",
        11,
        TEXT,
        "700",
        spacing=1,
    )

    telemetry_items = [
        ("COMMITS", commits, GREEN),
        ("PULL REQUESTS", pull_requests, BLUE),
        ("ISSUES", issues, BLUE),
        ("FORKS", forks, GREEN),
    ]

    for index, (
        label,
        value,
        color,
    ) in enumerate(telemetry_items):

        row_y = (
            telemetry_y
            + 58
            + (
                index * 34
            )
        )

        output += text(
            telemetry_x + 20,
            row_y,
            label,
            8,
            MUTED,
            "700",
            spacing=1,
        )

        output += text(
            telemetry_x
            + telemetry_w
            - 20,
            row_y,
            str(value),
            13,
            color,
            "700",
            "end",
        )

    output += line(
        telemetry_x + 20,
        telemetry_y + 186,
        telemetry_x + telemetry_w - 20,
        telemetry_y + 186,
    )

    output += text(
        telemetry_x + 20,
        telemetry_y + 203,
        "REAL DATA",
        8,
        GREEN,
        "700",
        spacing=1,
    )

    # ========================================================
    # SIGNAL STRIP
    # ========================================================

    signal_y = 486

    output += box(
        24,
        signal_y,
        width - 48,
        70,
    )

    output += text(
        44,
        signal_y + 26,
        "SIGNAL",
        9,
        MUTED,
        "700",
        spacing=1,
    )

    signals = [
        ("FINANCE", GREEN),
        ("TECHNOLOGY", BLUE),
        ("AI", GREEN),
        ("ANALYTICS", BLUE),
        ("RESEARCH", GREEN),
    ]

    x = 132

    for label, color in signals:

        badge_w = (
            len(label) * 8
        ) + 32

        output += f"""
<rect
    x="{x}"
    y="{signal_y + 14}"
    width="{badge_w}"
    height="30"
    rx="7"
    fill="{PANEL_ALT}"
    stroke="{color}"
    stroke-width="1"/>
"""

        output += text(
            x + (
                badge_w / 2
            ),
            signal_y + 34,
            label,
            8,
            color,
            "700",
            "middle",
            .5,
        )

        x += (
            badge_w
            + 10
        )

    # ========================================================
    # FOOTER
    # ========================================================

    footer_y = 584

    output += text(
        48,
        footer_y + 24,
        "GROWTH GRAPH",
        9,
        TEXT,
        "700",
        spacing=1,
    )

    output += text(
        190,
        footer_y + 24,
        "GITHUB ENGINE",
        9,
        BLUE,
        "700",
        spacing=1,
    )

    output += text(
        330,
        footer_y + 24,
        "HISTORICAL DATA",
        9,
        GREEN,
        "700",
        spacing=1,
    )

    output += text(
        width - 48,
        footer_y + 24,
        "ZENZIZENZIC / 2026",
        8,
        MUTED,
        "700",
        "end",
        1,
    )

    output += svg_end()

    (
        ASSETS_DIR / "control-room.svg"
    ).write_text(
        output,
        encoding="utf-8",
    )


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    history = load_history()

    generate_control_room(
        history
    )

    print()
    print(
        "======================================"
    )
    print(
        " ZENZIZENZIC // CONTROL ROOM"
    )
    print(
        " COMPACT VISUAL ENGINE"
    )
    print(
        "======================================"
    )
    print()
    print(
        "Generated:"
    )
    print(
        "  assets/control-room.svg"
    )
    print()
    print(
        f"Snapshots: "
        f"{len(history.get('snapshots', []))}"
    )
    print(
        f"Output: {ASSETS_DIR}"
    )


if __name__ == "__main__":
    main()