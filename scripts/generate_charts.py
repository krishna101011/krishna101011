from __future__ import annotations

import html
import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "github-history.json"
ASSETS_DIR = ROOT / "assets"


BACKGROUND = "#0b0f12"
TEXT = "#e8edf2"
MUTED = "#7d8790"
GRID = "#293038"
GREEN = "#39e58c"


def load_history() -> dict:
    with DATA_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def svg_start(width: int, height: int, title: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">
<title>{html.escape(title)}</title>
<rect width="100%" height="100%" fill="{BACKGROUND}"/>
"""


def svg_end() -> str:
    return "</svg>\n"


def generate_activity_chart(history: dict) -> None:
    snapshots = history.get("snapshots", [])

    width = 1000
    height = 400

    padding_left = 60
    padding_right = 30
    padding_top = 70
    padding_bottom = 50

    values = [
        snapshot.get("activity", {}).get(
            "activity_index",
            0,
        )
        for snapshot in snapshots
    ]

    if not values:
        values = [0]

    maximum = max(100, max(values))

    chart_width = (
        width
        - padding_left
        - padding_right
    )

    chart_height = (
        height
        - padding_top
        - padding_bottom
    )

    points = []

    for index, value in enumerate(values):

        if len(values) == 1:
            x = (
                padding_left
                + chart_width / 2
            )
        else:
            x = padding_left + (
                index
                / (len(values) - 1)
            ) * chart_width

        y = (
            height
            - padding_bottom
            - (
                value
                / maximum
            ) * chart_height
        )

        points.append((x, y))

    polyline = " ".join(
        f"{x:.1f},{y:.1f}"
        for x, y in points
    )

    output = svg_start(
        width,
        height,
        "GitHub Activity Market",
    )

    output += f"""
<text
    x="{padding_left}"
    y="38"
    fill="{TEXT}"
    font-family="monospace"
    font-size="22"
    font-weight="bold">
    GITHUB ACTIVITY MARKET
</text>
"""

    for level in (
        0,
        25,
        50,
        75,
        100,
    ):
        y = (
            height
            - padding_bottom
            - (
                level
                / maximum
            ) * chart_height
        )

        output += f"""
<line
    x1="{padding_left}"
    y1="{y:.1f}"
    x2="{width - padding_right}"
    y2="{y:.1f}"
    stroke="{GRID}"
    stroke-width="1"/>

<text
    x="18"
    y="{y + 5:.1f}"
    fill="{MUTED}"
    font-family="monospace"
    font-size="12">
    {level}
</text>
"""

    output += f"""
<polyline
    points="{polyline}"
    fill="none"
    stroke="{GREEN}"
    stroke-width="4"
    stroke-linecap="round"
    stroke-linejoin="round"/>
"""

    for x, y in points:
        output += f"""
<circle
    cx="{x:.1f}"
    cy="{y:.1f}"
    r="4"
    fill="{GREEN}"/>
"""

    if snapshots:
        first_date = snapshots[0].get(
            "date",
            "",
        )

        latest_date = snapshots[-1].get(
            "date",
            "",
        )

        output += f"""
<text
    x="{padding_left}"
    y="{height - 15}"
    fill="{MUTED}"
    font-family="monospace"
    font-size="11">
    {html.escape(first_date)}
</text>

<text
    x="{width - padding_right - 70}"
    y="{height - 15}"
    fill="{MUTED}"
    font-family="monospace"
    font-size="11">
    {html.escape(latest_date)}
</text>
"""

    output += svg_end()

    (
        ASSETS_DIR / "activity-chart.svg"
    ).write_text(
        output,
        encoding="utf-8",
    )


def generate_heatmap(history: dict) -> None:
    snapshots = history.get("snapshots", [])

    width = 1000
    height = 250

    cell_size = 18
    gap = 4

    start_x = 60
    start_y = 75

    output = svg_start(
        width,
        height,
        "GitHub Activity Heatmap",
    )

    output += f"""
<text
    x="60"
    y="38"
    fill="{TEXT}"
    font-family="monospace"
    font-size="22"
    font-weight="bold">
    ACTIVITY GRID
</text>
"""

    recent = snapshots[-35:]

    for index in range(35):

        x = (
            start_x
            + index
            * (cell_size + gap)
        )

        score = 0

        if index < len(recent):
            score = recent[index].get(
                "activity",
                {},
            ).get(
                "activity_index",
                0,
            )

        if score == 0:
            fill = "#161c21"
        elif score <= 25:
            fill = "#173b2b"
        elif score <= 50:
            fill = "#17613c"
        elif score <= 75:
            fill = "#159451"
        else:
            fill = GREEN

        date = ""

        if index < len(recent):
            date = recent[index].get(
                "date",
                "",
            )

        output += f"""
<rect
    x="{x}"
    y="{start_y}"
    width="{cell_size}"
    height="{cell_size}"
    rx="3"
    fill="{fill}">
    <title>
        {html.escape(date)}
        — Activity Index: {score}
    </title>
</rect>
"""

    output += f"""
<text
    x="60"
    y="145"
    fill="{MUTED}"
    font-family="monospace"
    font-size="12">
    REAL ACTIVITY · HISTORICAL SNAPSHOTS
</text>
"""

    output += svg_end()

    (
        ASSETS_DIR / "activity-heatmap.svg"
    ).write_text(
        output,
        encoding="utf-8",
    )


def generate_constellation(history: dict) -> None:
    snapshots = history.get("snapshots", [])

    width = 1000
    height = 500

    output = svg_start(
        width,
        height,
        "Repository Constellation",
    )

    output += f"""
<text
    x="50"
    y="40"
    fill="{TEXT}"
    font-family="monospace"
    font-size="22"
    font-weight="bold">
    REPOSITORY CONSTELLATION
</text>
"""

    if not snapshots:
        output += f"""
<text
    x="50"
    y="100"
    fill="{MUTED}"
    font-family="monospace"
    font-size="14">
    No repository data available.
</text>
"""

    else:
        latest = snapshots[-1]

        repositories = latest.get(
            "repositories",
            [],
        )

        total = min(
            len(repositories),
            30,
        )

        center_x = width / 2
        center_y = height / 2

        if total:
            for index, repo in enumerate(
                repositories[:30]
            ):
                angle = (
                    2
                    * math.pi
                    * index
                    / total
                )

                ring = (
                    100
                    + (index % 4) * 45
                )

                x = (
                    center_x
                    + math.cos(angle)
                    * ring
                )

                y = (
                    center_y
                    + math.sin(angle)
                    * ring
                )

                stars = repo.get(
                    "stars",
                    0,
                )

                forks = repo.get(
                    "forks",
                    0,
                )

                weight = (
                    stars
                    + forks
                )

                radius = (
                    6
                    + min(
                        14,
                        math.log1p(
                            weight
                        ),
                    )
                )

                name = html.escape(
                    repo.get(
                        "name",
                        "unknown",
                    )
                )

                output += f"""
<circle
    cx="{x:.1f}"
    cy="{y:.1f}"
    r="{radius:.1f}"
    fill="{GREEN}"/>

<text
    x="{x + 14:.1f}"
    y="{y + 4:.1f}"
    fill="#cbd3da"
    font-family="monospace"
    font-size="12">
    {name}
</text>
"""

        else:
            output += f"""
<text
    x="50"
    y="100"
    fill="{MUTED}"
    font-family="monospace"
    font-size="14">
    No public repositories found.
</text>
"""

    output += svg_end()

    (
        ASSETS_DIR
        / "repo-constellation.svg"
    ).write_text(
        output,
        encoding="utf-8",
    )


def main() -> None:
    ASSETS_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    history = load_history()

    generate_activity_chart(
        history
    )

    generate_heatmap(
        history
    )

    generate_constellation(
        history
    )

    print(
        "SVG generation complete."
    )

    print(
        f"Assets written to: "
        f"{ASSETS_DIR}"
    )


if __name__ == "__main__":
    main()