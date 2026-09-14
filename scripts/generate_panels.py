from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DATA_FILE = ROOT / "data" / "github-history.json"
ASSETS_DIR = ROOT / "assets"


# ============================================================
# CONTROL ROOM DESIGN SYSTEM
# ============================================================

BG = "#07090C"
PANEL = "#0D1117"
PANEL_2 = "#11161D"
BORDER = "#252C34"

TEXT = "#E6EDF3"
MUTED = "#7D8790"

GREEN = "#39E58C"
CYAN = "#39D9FF"
BLUE = "#5AA9FF"
AMBER = "#F4C95D"
RED = "#FF5C5C"

FONT = "monospace"


# ============================================================
# DATA
# ============================================================

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


def esc(value: object) -> str:
    return html.escape(str(value))


# ============================================================
# SVG HELPERS
# ============================================================

def svg_start(
    width: int,
    height: int,
    title: str,
) -> str:
    return f"""<svg
xmlns="http://www.w3.org/2000/svg"
width="{width}"
height="{height}"
viewBox="0 0 {width} {height}">

<title>{esc(title)}</title>

<rect
    width="100%"
    height="100%"
    rx="14"
    fill="{BG}"/>

<rect
    x="1"
    y="1"
    width="{width - 2}"
    height="{height - 2}"
    rx="14"
    fill="none"
    stroke="{BORDER}"
    stroke-width="2"/>
"""


def svg_end() -> str:
    return "</svg>\n"


def text(
    x: float,
    y: float,
    content: str,
    size: int = 14,
    color: str = TEXT,
    weight: str = "400",
    anchor: str = "start",
    letter_spacing: str = "0",
) -> str:
    return f"""
<text
    x="{x}"
    y="{y}"
    fill="{color}"
    font-family="{FONT}"
    font-size="{size}px"
    font-weight="{weight}"
    text-anchor="{anchor}"
    letter-spacing="{letter_spacing}px">
    {esc(content)}
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


def panel_header(
    width: int,
    section: str,
    title: str,
    status: str | None = None,
    status_color: str = GREEN,
) -> str:
    output = ""

    output += text(
        32,
        36,
        section,
        11,
        GREEN,
        "700",
        letter_spacing="2",
    )

    output += text(
        32,
        64,
        title,
        22,
        TEXT,
        "700",
    )

    if status is not None:
        output += f"""
<circle
    cx="{width - 48}"
    cy="48"
    r="6"
    fill="{status_color}"/>
"""

        output += text(
            width - 62,
            53,
            status,
            11,
            status_color,
            "700",
            "end",
            "1",
        )

    output += line(
        32,
        82,
        width - 32,
        82,
    )

    return output


def metric_card(
    x: float,
    y: float,
    width: float,
    label: str,
    value: str,
    accent: str = GREEN,
) -> str:
    output = f"""
<rect
    x="{x}"
    y="{y}"
    width="{width}"
    height="88"
    rx="10"
    fill="{PANEL_2}"
    stroke="{BORDER}"
    stroke-width="1"/>
"""

    output += text(
        x + 18,
        y + 24,
        label,
        10,
        MUTED,
        "700",
        letter_spacing="1",
    )

    output += text(
        x + 18,
        y + 58,
        value,
        23,
        accent,
        "700",
    )

    return output


# ============================================================
# CONTROL HEADER
# ============================================================

def generate_control_header(
    history: dict,
) -> None:
    width = 1000
    height = 210

    latest = latest_snapshot(history)

    repositories = latest.get(
        "repository_count",
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

    output = svg_start(
        width,
        height,
        "KRISHNA Control Room",
    )

    # Accent line
    output += f"""
<rect
    x="32"
    y="30"
    width="5"
    height="150"
    rx="2"
    fill="{GREEN}"/>
"""

    output += text(
        58,
        60,
        "KRISHNA // CONTROL ROOM",
        27,
        TEXT,
        "700",
        letter_spacing="2",
    )

    output += text(
        58,
        88,
        "GITHUB OPERATIONS // PERSONAL RESEARCH SYSTEM",
        10,
        MUTED,
        "700",
        letter_spacing="2",
    )

    # Live indicator
    output += f"""
<circle
    cx="920"
    cy="54"
    r="7"
    fill="{GREEN}"/>
"""

    output += text(
        942,
        58,
        "LIVE",
        11,
        GREEN,
        "700",
        letter_spacing="1",
    )

    # Signal line
    output += line(
        58,
        112,
        942,
        112,
        BORDER,
        1,
    )

    output += text(
        58,
        142,
        "BUILD",
        10,
        GREEN,
        "700",
        letter_spacing="1",
    )

    output += text(
        135,
        142,
        "RESEARCH",
        10,
        CYAN,
        "700",
        letter_spacing="1",
    )

    output += text(
        245,
        142,
        "ANALYZE",
        10,
        BLUE,
        "700",
        letter_spacing="1",
    )

    output += text(
        345,
        142,
        "EXPERIMENT",
        10,
        AMBER,
        "700",
        letter_spacing="1",
    )

    output += metric_card(
        58,
        155,
        180,
        "PUBLIC REPOSITORIES",
        str(repositories),
        GREEN,
    )

    output += metric_card(
        258,
        155,
        180,
        "ACTIVITY INDEX",
        f"{activity_index}/100",
        CYAN,
    )

    output += metric_card(
        458,
        155,
        180,
        "DATA SOURCE",
        "GITHUB",
        BLUE,
    )

    output += metric_card(
        658,
        155,
        180,
        "SYSTEM",
        "ONLINE",
        GREEN,
    )

    output += svg_end()

    (
        ASSETS_DIR / "control-header.svg"
    ).write_text(
        output,
        encoding="utf-8",
    )


# ============================================================
# SYSTEM STATUS
# ============================================================

def generate_system_status(
    history: dict,
) -> None:
    width = 1000
    height = 315

    latest = latest_snapshot(history)

    repositories = latest.get(
        "repository_count",
        0,
    )

    active = latest.get(
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

    output = svg_start(
        width,
        height,
        "System Status",
    )

    output += panel_header(
        width,
        "01 // SYSTEM",
        "SYSTEM STATUS",
        "ONLINE",
    )

    output += metric_card(
        32,
        108,
        205,
        "REPOSITORIES",
        str(repositories),
        GREEN,
    )

    output += metric_card(
        255,
        108,
        205,
        "ACTIVE",
        str(active),
        GREEN,
    )

    output += metric_card(
        478,
        108,
        205,
        "STARS",
        str(stars),
        AMBER,
    )

    output += metric_card(
        701,
        108,
        205,
        "FORKS",
        str(forks),
        CYAN,
    )

    output += text(
        32,
        238,
        "PRIMARY",
        10,
        MUTED,
        "700",
        letter_spacing="1",
    )

    output += text(
        115,
        238,
        "PYTHON",
        12,
        GREEN,
        "700",
    )

    output += text(
        235,
        238,
        "SECONDARY",
        10,
        MUTED,
        "700",
        letter_spacing="1",
    )

    output += text(
        328,
        238,
        "JAVASCRIPT / TYPESCRIPT / SQL",
        12,
        CYAN,
        "700",
    )

    output += text(
        32,
        273,
        "MODE",
        10,
        MUTED,
        "700",
        letter_spacing="1",
    )

    output += text(
        85,
        273,
        "RESEARCH · BUILD · EXPERIMENT",
        12,
        TEXT,
        "700",
    )

    output += svg_end()

    (
        ASSETS_DIR / "system-status.svg"
    ).write_text(
        output,
        encoding="utf-8",
    )


# ============================================================
# TELEMETRY
# ============================================================

def generate_telemetry(
    history: dict,
) -> None:
    width = 1000
    height = 355

    snapshots = history.get(
        "snapshots",
        [],
    )

    latest = latest_snapshot(history)

    activity = latest.get(
        "activity",
        {},
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

    events = activity.get(
        "recent_events",
        0,
    )

    output = svg_start(
        width,
        height,
        "GitHub Telemetry",
    )

    output += panel_header(
        width,
        "03 // TELEMETRY",
        "LIVE TELEMETRY",
        "REAL DATA",
        CYAN,
    )

    output += metric_card(
        32,
        108,
        205,
        "COMMITS",
        str(commits),
        GREEN,
    )

    output += metric_card(
        255,
        108,
        205,
        "PULL REQUESTS",
        str(pull_requests),
        BLUE,
    )

    output += metric_card(
        478,
        108,
        205,
        "ISSUES",
        str(issues),
        AMBER,
    )

    output += metric_card(
        701,
        108,
        205,
        "EVENTS",
        str(events),
        CYAN,
    )

    output += text(
        32,
        245,
        "HISTORY LENGTH",
        10,
        MUTED,
        "700",
        letter_spacing="1",
    )

    output += text(
        170,
        245,
        f"{len(snapshots)} SNAPSHOT(S)",
        12,
        TEXT,
        "700",
    )

    output += text(
        32,
        280,
        "COLLECTION ENGINE",
        10,
        MUTED,
        "700",
        letter_spacing="1",
    )

    output += text(
        190,
        280,
        "PYTHON / GITHUB API",
        12,
        GREEN,
        "700",
    )

    output += text(
        32,
        315,
        "CLASSIFICATION",
        10,
        MUTED,
        "700",
        letter_spacing="1",
    )

    output += text(
        150,
        315,
        "REAL DATA · DERIVED SIGNAL · PERSONAL CONTEXT",
        11,
        CYAN,
        "700",
    )

    output += svg_end()

    (
        ASSETS_DIR / "telemetry.svg"
    ).write_text(
        output,
        encoding="utf-8",
    )


# ============================================================
# CURRENT SIGNAL
# ============================================================

def generate_signals(
    history: dict,
) -> None:
    width = 1000
    height = 245

    signals = [
        ("FINANCE", GREEN),
        ("TECHNOLOGY", CYAN),
        ("AI", BLUE),
        ("CYBERSECURITY", RED),
        ("ANALYTICS", AMBER),
        ("RESEARCH", TEXT),
    ]

    output = svg_start(
        width,
        height,
        "Current Signal",
    )

    output += panel_header(
        width,
        "04 // SIGNAL",
        "CURRENT SIGNAL",
        "ACTIVE",
        GREEN,
    )

    x = 32
    y = 112

    for index, (label, color) in enumerate(
        signals
    ):
        approximate_width = (
            len(label) * 8
        ) + 38

        output += f"""
<rect
    x="{x}"
    y="{y}"
    width="{approximate_width}"
    height="42"
    rx="8"
    fill="{PANEL_2}"
    stroke="{color}"
    stroke-width="1"/>
"""

        output += text(
            x + 16,
            y + 27,
            label,
            11,
            color,
            "700",
            letter_spacing="1",
        )

        x += approximate_width + 12

        if x > width - 180:
            x = 32
            y += 58

    output += text(
        32,
        214,
        "SIGNAL PROFILE // FINANCE × TECHNOLOGY × AI × SECURITY × RESEARCH",
        10,
        MUTED,
        "700",
        letter_spacing="1",
    )

    output += svg_end()

    (
        ASSETS_DIR / "signals.svg"
    ).write_text(
        output,
        encoding="utf-8",
    )


# ============================================================
# ACTIVE LAB
# ============================================================

def generate_active_lab(
    history: dict,
) -> None:
    width = 1000
    height = 345

    output = svg_start(
        width,
        height,
        "Active Lab",
    )

    output += panel_header(
        width,
        "06 // LAB",
        "ACTIVE LAB",
        "RUNNING",
        GREEN,
    )

    output += text(
        32,
        119,
        "GROWTH GRAPH",
        16,
        TEXT,
        "700",
        letter_spacing="1",
    )

    output += text(
        32,
        148,
        "PERSONAL PERFORMANCE ANALYTICS",
        10,
        CYAN,
        "700",
        letter_spacing="1",
    )

    features = [
        "GOALS / ACTUALS",
        "0–100 GROWTH SCORE",
        "MULTI-TIMELINE ANALYSIS",
        "HISTORICAL DATA",
        "TRADING-STYLE CHARTS",
        "AI REVIEW",
        "PROVIDER FAILOVER",
        "LOCAL-FIRST STORAGE",
    ]

    x = 32
    y = 190

    for index, item in enumerate(
        features
    ):
        column = index % 2
        row = index // 2

        x = 32 + (column * 455)
        current_y = (
            y + (row * 30)
        )

        output += f"""
<circle
    cx="{x}"
    cy="{current_y - 4}"
    r="3"
    fill="{GREEN}"/>
"""

        output += text(
            x + 14,
            current_y,
            item,
            11,
            TEXT,
            "700",
        )

    output += text(
        32,
        322,
        "EXPERIMENT STATUS // ACTIVE DEVELOPMENT",
        10,
        GREEN,
        "700",
        letter_spacing="1",
    )

    output += svg_end()

    (
        ASSETS_DIR / "active-lab.svg"
    ).write_text(
        output,
        encoding="utf-8",
    )


# ============================================================
# EXPERIMENT LOG
# ============================================================

def generate_experiment_log(
    history: dict,
) -> None:
    width = 1000
    height = 330

    snapshots = history.get(
        "snapshots",
        [],
    )

    output = svg_start(
        width,
        height,
        "Experiment Log",
    )

    output += panel_header(
        width,
        "07 // ARCHIVE",
        "EXPERIMENT LOG",
        "LIVE",
        AMBER,
    )

    experiments = [
        (
            "01",
            "GITHUB CONTROL ROOM",
            "ACTIVE",
            GREEN,
        ),
        (
            "02",
            "GROWTH GRAPH",
            "ACTIVE",
            CYAN,
        ),
        (
            "03",
            "HISTORICAL DATA ENGINE",
            f"{len(snapshots)} SNAPSHOTS",
            BLUE,
        ),
    ]

    y = 120

    for code, name, status, color in experiments:

        output += f"""
<rect
    x="32"
    y="{y - 24}"
    width="874"
    height="48"
    rx="7"
    fill="{PANEL_2}"
    stroke="{BORDER}"
    stroke-width="1"/>
"""

        output += text(
            50,
            y + 5,
            code,
            10,
            MUTED,
            "700",
            letter_spacing="1",
        )

        output += text(
            95,
            y + 5,
            name,
            11,
            TEXT,
            "700",
            letter_spacing="1",
        )

        output += text(
            865,
            y + 5,
            status,
            10,
            color,
            "700",
            "end",
            "1",
        )

        y += 62

    output += text(
        32,
        312,
        "ARCHIVE PRINCIPLE // PRESERVE · MEASURE · ITERATE",
        10,
        MUTED,
        "700",
        letter_spacing="1",
    )

    output += svg_end()

    (
        ASSETS_DIR / "experiment-log.svg"
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

    generate_control_header(history)
    generate_system_status(history)
    generate_telemetry(history)
    generate_signals(history)
    generate_active_lab(history)
    generate_experiment_log(history)

    print()
    print("======================================")
    print(" KRISHNA // CONTROL ROOM V2")
    print(" VISUAL ENGINE")
    print("======================================")
    print()
    print("Generated:")
    print("  control-header.svg")
    print("  system-status.svg")
    print("  telemetry.svg")
    print("  signals.svg")
    print("  active-lab.svg")
    print("  experiment-log.svg")
    print()
    print("Output:")
    print(ASSETS_DIR)


if __name__ == "__main__":
    main()