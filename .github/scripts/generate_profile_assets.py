#!/usr/bin/env python3
"""Generate GitHub-like contribution cards from the public profile calendar."""

from __future__ import annotations

import argparse
import html
import math
import re
import sys
import urllib.request
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape


@dataclass(frozen=True)
class ContributionDay:
    day: date
    count: int
    level: int


THEMES = {
    "dark": {
        "background": "#0D1117",
        "border": "#30363D",
        "text": "#F0F6FC",
        "muted": "#8B949E",
        "accent": "#00F5FF",
        "secondary": "#7C3AED",
        "levels": ["#161B22", "#0E4429", "#006D32", "#26A641", "#39D353"],
    },
    "light": {
        "background": "#FFFFFF",
        "border": "#D0D7DE",
        "text": "#1F2328",
        "muted": "#656D76",
        "accent": "#0969DA",
        "secondary": "#8250DF",
        "levels": ["#EBEDF0", "#9BE9A8", "#40C463", "#30A14E", "#216E39"],
    },
}


def fetch_contributions(username: str) -> tuple[int, list[ContributionDay]]:
    url = f"https://github.com/users/{username}/contributions"
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "text/html",
            "User-Agent": "miqbaltrim-profile-contribution-generator/1.0",
        },
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        page = response.read().decode("utf-8")

    total = None
    for heading in re.findall(r"<h2\b[^>]*>(.*?)</h2>", page, flags=re.DOTALL):
        text = re.sub(r"<[^>]+>", "", heading)
        match = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", text, re.I)
        if match:
            total = int(match.group(1).replace(",", ""))
            break

    tooltips: dict[str, int] = {}
    tooltip_pattern = r"<tool-tip\b([^>]*)>(.*?)</tool-tip>"
    for attributes, content in re.findall(tooltip_pattern, page, flags=re.DOTALL):
        target = re.search(r'\bfor="([^"]+)"', attributes)
        label = html.unescape(re.sub(r"<[^>]+>", "", content)).strip()
        count = re.match(r"(No|[\d,]+) contributions?", label)
        if target and count:
            tooltips[target.group(1)] = (
                0 if count.group(1) == "No" else int(count.group(1).replace(",", ""))
            )

    days: list[ContributionDay] = []
    for tag in re.findall(r"<td\b[^>]*ContributionCalendar-day[^>]*>", page):
        attributes = dict(re.findall(r'([\w:-]+)="([^"]*)"', tag))
        if not {"data-date", "data-level", "id"} <= attributes.keys():
            continue
        days.append(
            ContributionDay(
                day=date.fromisoformat(attributes["data-date"]),
                count=tooltips.get(attributes["id"], 0),
                level=int(attributes["data-level"]),
            )
        )

    days.sort(key=lambda item: item.day)
    if total is None or len(days) < 365:
        raise RuntimeError("GitHub contribution calendar could not be parsed safely")

    return total, days


def format_date(value: date, include_year: bool = False) -> str:
    formatted = value.strftime("%b %d, %Y" if include_year else "%b %d")
    return formatted.replace(" 0", " ")


def calculate_streaks(days: list[ContributionDay]) -> tuple[list[ContributionDay], list[ContributionDay]]:
    by_date = {item.day: item for item in days}
    last_day = days[-1].day
    cursor = last_day if by_date[last_day].count > 0 else last_day - timedelta(days=1)

    current: list[ContributionDay] = []
    while cursor in by_date and by_date[cursor].count > 0:
        current.append(by_date[cursor])
        cursor -= timedelta(days=1)
    current.reverse()

    longest: list[ContributionDay] = []
    candidate: list[ContributionDay] = []
    previous = None
    for item in days:
        if item.count > 0 and (previous is None or item.day == previous + timedelta(days=1)):
            candidate.append(item)
        elif item.count > 0:
            candidate = [item]
        else:
            candidate = []
        if len(candidate) > len(longest):
            longest = candidate.copy()
        previous = item.day

    return current, longest


def svg_header(width: int, height: int, title: str) -> list[str]:
    return [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">',
        f'<title id="title">{escape(title)}</title>',
        '<desc id="desc">Automatically generated from the public GitHub contribution calendar.</desc>',
        '<style>text{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}</style>',
    ]


def render_calendar(total: int, days: list[ContributionDay], mode: str) -> str:
    theme = THEMES[mode]
    width, height = 900, 190
    left, top, step, cell = 65, 67, 14, 11
    first_day = days[0].day
    lines = svg_header(width, height, f"{total} contributions in the last year")
    lines.extend(
        [
            f'<rect width="{width}" height="{height}" fill="{theme["background"]}"/>',
            f'<rect x="0.5" y="32.5" width="899" height="150" rx="7" fill="{theme["background"]}" stroke="{theme["border"]}"/>',
            f'<text x="1" y="21" fill="{theme["text"]}" font-size="17" font-weight="600">{total:,} contributions in the last year</text>',
        ]
    )

    seen_months: set[tuple[int, int]] = set()
    for item in days:
        month = (item.day.year, item.day.month)
        if month in seen_months:
            continue
        seen_months.add(month)
        week = (item.day - first_day).days // 7
        x = left + week * step
        if x <= width - 35:
            lines.append(
                f'<text x="{x}" y="55" fill="{theme["text"]}" font-size="12">{item.day.strftime("%b")}</text>'
            )

    for label, weekday in (("Mon", 1), ("Wed", 3), ("Fri", 5)):
        y = top + weekday * step + 9
        lines.append(f'<text x="18" y="{y}" fill="{theme["text"]}" font-size="11">{label}</text>')

    for item in days:
        week = (item.day - first_day).days // 7
        weekday = (item.day.weekday() + 1) % 7
        x, y = left + week * step, top + weekday * step
        color = theme["levels"][max(0, min(item.level, 4))]
        lines.append(
            f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" rx="2" fill="{color}">'
            f'<title>{item.count} contributions on {item.day.isoformat()}</title></rect>'
        )

    legend_y = 177
    legend_x = width - 190
    lines.append(f'<text x="{legend_x}" y="{legend_y}" fill="{theme["muted"]}" font-size="11">Less</text>')
    for level, color in enumerate(theme["levels"]):
        x = legend_x + 32 + level * 15
        lines.append(f'<rect x="{x}" y="{legend_y - 10}" width="11" height="11" rx="2" fill="{color}"/>')
    lines.append(f'<text x="{legend_x + 112}" y="{legend_y}" fill="{theme["muted"]}" font-size="11">More</text>')
    lines.append("</svg>")
    return "\n".join(lines)


def streak_range(items: list[ContributionDay]) -> str:
    if not items:
        return "No active streak"
    if len(items) == 1:
        return format_date(items[0].day)
    return f"{format_date(items[0].day)} – {format_date(items[-1].day)}"


def render_streak(total: int, days: list[ContributionDay], mode: str) -> str:
    theme = THEMES[mode]
    current, longest = calculate_streaks(days)
    width, height = 900, 205
    third = width / 3
    lines = svg_header(width, height, "GitHub contributions and streaks for the last year")
    lines.extend(
        [
            f'<rect x="0.5" y="0.5" width="899" height="204" rx="8" fill="{theme["background"]}" stroke="{theme["border"]}"/>',
            f'<line x1="{third}" y1="28" x2="{third}" y2="177" stroke="{theme["secondary"]}"/>',
            f'<line x1="{third * 2}" y1="28" x2="{third * 2}" y2="177" stroke="{theme["secondary"]}"/>',
            f'<circle cx="450" cy="76" r="48" fill="none" stroke="{theme["accent"]}" stroke-width="7"/>',
            f'<text x="150" y="91" text-anchor="middle" fill="{theme["text"]}" font-size="34" font-weight="700">{total:,}</text>',
            f'<text x="150" y="128" text-anchor="middle" fill="{theme["secondary"]}" font-size="16">Contributions in the Last Year</text>',
            f'<text x="150" y="160" text-anchor="middle" fill="{theme["muted"]}" font-size="13">{format_date(days[0].day, True)} – {format_date(days[-1].day, True)}</text>',
            f'<text x="450" y="88" text-anchor="middle" fill="{theme["text"]}" font-size="34" font-weight="700">{len(current)}</text>',
            f'<text x="450" y="143" text-anchor="middle" fill="{theme["accent"]}" font-size="16" font-weight="600">Current Streak</text>',
            f'<text x="450" y="171" text-anchor="middle" fill="{theme["muted"]}" font-size="13">{escape(streak_range(current))}</text>',
            f'<text x="750" y="91" text-anchor="middle" fill="{theme["text"]}" font-size="34" font-weight="700">{len(longest)}</text>',
            f'<text x="750" y="128" text-anchor="middle" fill="{theme["secondary"]}" font-size="16">Longest Streak</text>',
            f'<text x="750" y="160" text-anchor="middle" fill="{theme["muted"]}" font-size="13">{escape(streak_range(longest))}</text>',
            '</svg>',
        ]
    )
    return "\n".join(lines)


def render_activity(days: list[ContributionDay], mode: str) -> str:
    theme = THEMES[mode]
    recent = days[-30:]
    width, height = 900, 225
    left, right, top, bottom = 58, 24, 55, 38
    chart_width = width - left - right
    chart_height = height - top - bottom
    raw_max = max((item.count for item in recent), default=1)
    chart_max = max(5, int(math.ceil(raw_max / 5)) * 5)
    total = sum(item.count for item in recent)

    points: list[tuple[float, float]] = []
    for index, item in enumerate(recent):
        x = left + index * chart_width / max(1, len(recent) - 1)
        y = top + chart_height - (item.count / chart_max * chart_height)
        points.append((x, y))

    line_points = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    baseline = top + chart_height
    area_path = (
        f"M {points[0][0]:.1f} {baseline:.1f} "
        + " ".join(f"L {x:.1f} {y:.1f}" for x, y in points)
        + f" L {points[-1][0]:.1f} {baseline:.1f} Z"
    )

    lines = svg_header(width, height, "GitHub contribution activity for the last 30 days")
    lines.extend(
        [
            '<defs><linearGradient id="activity-fill" x1="0" y1="0" x2="0" y2="1">'
            f'<stop offset="0" stop-color="{theme["accent"]}" stop-opacity="0.35"/>'
            f'<stop offset="1" stop-color="{theme["accent"]}" stop-opacity="0.02"/>'
            '</linearGradient></defs>',
            f'<rect width="{width}" height="{height}" rx="8" fill="{theme["background"]}"/>',
            f'<rect x="0.5" y="0.5" width="899" height="224" rx="8" fill="none" stroke="{theme["border"]}"/>',
            f'<text x="24" y="31" fill="{theme["text"]}" font-size="16" font-weight="600">Contribution Activity · Last 30 Days</text>',
            f'<text x="876" y="31" text-anchor="end" fill="{theme["muted"]}" font-size="13">{total:,} contributions</text>',
        ]
    )

    for tick in range(6):
        value = chart_max * tick / 5
        y = baseline - chart_height * tick / 5
        label = str(int(value))
        lines.append(f'<line x1="{left}" y1="{y:.1f}" x2="{width - right}" y2="{y:.1f}" stroke="{theme["border"]}" stroke-dasharray="3 5"/>')
        lines.append(f'<text x="{left - 12}" y="{y + 4:.1f}" text-anchor="end" fill="{theme["muted"]}" font-size="10">{label}</text>')

    lines.append(f'<path d="{area_path}" fill="url(#activity-fill)"/>')
    lines.append(f'<polyline points="{line_points}" fill="none" stroke="{theme["accent"]}" stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>')
    for x, y in points:
        lines.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.5" fill="{theme["background"]}" stroke="{theme["accent"]}" stroke-width="2"/>')

    for index in (0, 7, 14, 21, 29):
        x = left + index * chart_width / max(1, len(recent) - 1)
        lines.append(f'<text x="{x:.1f}" y="{height - 14}" text-anchor="middle" fill="{theme["muted"]}" font-size="10">{format_date(recent[index].day)}</text>')

    lines.append('</svg>')
    return "\n".join(lines)


def write_asset(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8", newline="\n")
    print(f"Generated {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    parser.add_argument("--output-dir", default="dist")
    args = parser.parse_args()

    try:
        total, days = fetch_contributions(args.user)
    except Exception as error:
        print(f"Could not generate contribution assets: {error}", file=sys.stderr)
        return 1

    output = Path(args.output_dir)
    write_asset(output / "github-contribution-calendar-dark.svg", render_calendar(total, days, "dark"))
    write_asset(output / "github-contribution-calendar.svg", render_calendar(total, days, "light"))
    write_asset(output / "github-streak-dark.svg", render_streak(total, days, "dark"))
    write_asset(output / "github-streak.svg", render_streak(total, days, "light"))
    write_asset(output / "github-activity-dark.svg", render_activity(days, "dark"))
    write_asset(output / "github-activity.svg", render_activity(days, "light"))
    print(f"Source total: {total} contributions in the last year")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
