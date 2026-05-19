#!/usr/bin/env python3
from __future__ import annotations

import argparse
import html
import re
from datetime import datetime, timezone
from pathlib import Path


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower()).strip("-")
    return slug or "goal"


def write_new(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(text, encoding="utf-8")


def append_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as file:
        file.write(text)


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a goal ledger scaffold.")
    parser.add_argument("--root", default=".", help="Project root where .agent should live.")
    parser.add_argument("--goal-id", required=True, help="Stable goal id, lowercase-with-hyphens preferred.")
    parser.add_argument("--title", required=True, help="Human title for the goal.")
    parser.add_argument("--objective", required=True, help="One sentence objective.")
    parser.add_argument("--mode", choices=["light", "full"], default="light")
    parser.add_argument("--parent", default="", help="Parent goal id for chained goals.")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    goal_id = slugify(args.goal_id)
    run_dir = root / ".agent" / "runs" / goal_id
    timestamp = now_iso()

    evidence_dir = run_dir / "evidence"
    evidence_dir.mkdir(parents=True, exist_ok=True)

    parent_line = args.parent.strip() or "none"
    relative_ledger_path = f".agent/runs/{goal_id}/"
    absolute_ledger_path = run_dir.as_posix()
    escaped_title = html.escape(args.title)
    escaped_objective = html.escape(args.objective)
    escaped_goal_id = html.escape(goal_id)
    escaped_parent = html.escape(parent_line)
    escaped_mode = html.escape(args.mode)
    write_new(
        run_dir / "GOAL.md",
        f"""# {args.title}

Goal ID: `{goal_id}`
Started: {timestamp}
Parent goal: {parent_line}
Mode: {args.mode}
Ledger path: `{relative_ledger_path}`

## Objective

{args.objective}

## Goal Mode Coupling

When creating or updating the matching `/goal`, include this ledger pointer in the goal objective:

`Maintain the agent-owned ledger at {absolute_ledger_path}/ and keep implementation-notes.html current at checkpoints, before compaction, and before final handoff.`

## Finishing Criteria

- [todo] Define concrete validation before implementation.
- [todo] Keep `implementation-notes.html` current with status, decisions, tradeoffs, changes, validation, and next action.
- [todo] Link large proof artifacts from `evidence/` when they are too bulky for the HTML notes.

## Escape Hatch

Pause, ask the user, or mark a scoped item `[blocked]` / `[incomplete]` if:
- validation contradicts the goal
- the goal requires a scope change
- the agent is looping without measurable progress
- the next step risks deleting or rewriting durable memory
- the PRD and actual repo disagree
- the ledger itself contaminates validation

""",
    )

    write_new(
        run_dir / "implementation-notes.html",
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escaped_title} - Implementation Notes</title>
  <style>
    body {{
      color: #202124;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.55;
      margin: 0 auto;
      max-width: 920px;
      padding: 40px 24px;
    }}
    h1, h2 {{ line-height: 1.2; }}
    code {{
      background: #f1f3f4;
      border-radius: 4px;
      padding: 2px 5px;
    }}
    .meta {{
      background: #f8f9fa;
      border: 1px solid #dadce0;
      border-radius: 8px;
      padding: 16px;
    }}
    .timeline {{
      background: #f8f9fa;
      border: 1px solid #dadce0;
      border-radius: 8px;
      max-height: 360px;
      overflow: auto;
      padding: 8px;
    }}
    .timeline-note {{
      color: #5f6368;
      margin-bottom: 10px;
    }}
    .event {{
      background: #fff;
      border: 1px solid #e8eaed;
      border-radius: 8px;
      margin: 8px 0;
      padding: 12px 14px;
    }}
    .event-head {{
      align-items: center;
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 6px;
    }}
    .event-summary {{
      margin: 0;
    }}
    .event time {{
      color: #5f6368;
      font-size: 13px;
    }}
    .badge, .phase, .actor {{
      border-radius: 999px;
      display: inline-block;
      font-size: 12px;
      font-weight: 700;
      line-height: 1;
      padding: 5px 8px;
      text-transform: uppercase;
    }}
    .badge {{ background: #e8f0fe; color: #174ea6; }}
    .status-done, .status-validated {{ background: #e6f4ea; color: #137333; }}
    .status-blocked, .status-failed {{ background: #fce8e6; color: #c5221f; }}
    .status-decision {{ background: #fef7e0; color: #b06000; }}
    .phase, .actor {{
      background: #f1f3f4;
      color: #3c4043;
      font-weight: 600;
    }}
    li {{ margin: 6px 0; }}
  </style>
</head>
<body>
  <h1>{escaped_title}</h1>
  <div class="meta">
    <p><strong>Goal ID:</strong> <code>{escaped_goal_id}</code></p>
    <p><strong>Started:</strong> {timestamp}</p>
    <p><strong>Parent goal:</strong> {escaped_parent}</p>
    <p><strong>Mode:</strong> {escaped_mode}</p>
    <p><strong>Objective:</strong> {escaped_objective}</p>
  </div>

  <h2>Resume Here</h2>
  <ul>
    <li><strong>Status:</strong> Goal created. Implementation work starts after validation is defined.</li>
    <li><strong>Current phase:</strong> Define validation, then begin the first concrete task.</li>
    <li><strong>Blockers:</strong> None recorded.</li>
    <li><strong>Next action:</strong> Write the first working checkpoint here before or after implementation starts.</li>
    <li><strong>Protected paths:</strong> None recorded.</li>
  </ul>

  <h2>Progress Timeline</h2>
  <p class="timeline-note">Progress is rendered directly in this file from the inline <code>progressEvents</code> array below. Append a new event to that array whenever execution reality changes meaningfully.</p>
  <div id="progress-timeline" class="timeline"></div>

  <h2>Decisions Outside The Spec</h2>
  <ul>
    <li>Empty at start.</li>
  </ul>

  <h2>Changes And Tradeoffs</h2>
  <ul>
    <li>Empty at start.</li>
  </ul>

  <h2>Validation</h2>
  <ul>
    <li>Validation is pending.</li>
  </ul>

  <h2>Evidence</h2>
  <ul>
    <li>Evidence links are pending. Put large logs, screenshots, or command output in <code>evidence/</code> and link them here.</li>
  </ul>

  <h2>Next Goal Candidates</h2>
  <ul>
    <li>Empty at start.</li>
  </ul>
  <script>
    const progressEvents = [
      {{
        ts: "{timestamp}",
        status: "created",
        phase: "start",
        actor: "agent",
        summary: "Goal ledger created."
      }}
    ];

    function escapeHtml(value) {{
      return String(value || "")
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
    }}

    function renderEvent(event) {{
      const status = escapeHtml(event.status || "event");
      const phase = escapeHtml(event.phase || "general");
      const actor = escapeHtml(event.actor || "agent");
      const timestamp = escapeHtml(event.ts || "");
      const summary = escapeHtml(event.summary || "");
      return `
        <article class="event">
          <div class="event-head">
            <span class="badge status-${{status}}">${{status}}</span>
            <span class="phase">${{phase}}</span>
            <span class="actor">${{actor}}</span>
            <time datetime="${{timestamp}}">${{timestamp}}</time>
          </div>
          <p class="event-summary">${{summary}}</p>
        </article>
      `;
    }}

    function renderProgressTimeline() {{
      const target = document.getElementById("progress-timeline");
      const events = Array.isArray(progressEvents) ? progressEvents : [];
      if (events.length === 0) {{
        target.innerHTML = "<p>No progress events recorded yet.</p>";
        return;
      }}
      target.innerHTML = events.map(renderEvent).join("");
    }}
    renderProgressTimeline();
  </script>
</body>
</html>
""",
    )

    goals_path = root / ".agent" / "GOALS.md"
    if not goals_path.exists():
        write_new(
            goals_path,
            """# Agent Goals

This file is the project-level index of active and completed agent goals. It records goal chains, not full implementation detail.

| Goal | Status | Parent | Ledger | Updated |
|---|---|---|---|---|
""",
        )
    append_text(
        goals_path,
        f"| `{goal_id}` | active | {parent_line} | `.agent/runs/{goal_id}/` | {timestamp} |\n",
    )

    print(run_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
