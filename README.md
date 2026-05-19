# Goal Ledger

<p align="center">
  <img src="plugins/goal-ledger/skills/goal/assets/hero.jpeg" alt="Vibe Bot crossing the finish line with arms raised, scoreboard of completed objectives behind him" width="720">
</p>

A single-file agent goal ledger that pairs with `/goal` mode in **Claude Code** and **OpenAI Codex CLI**.

`/goal` mode is great at keeping an agent pointed at one durable objective. It is not great at remembering what already happened. The Goal Ledger fills that gap: every checkpoint, decision, blocker, and validation gets written into one human-readable `implementation-notes.html` file that opens in any browser and survives compaction, hand-offs, and chained goals.

The same skill works in both agents. Same `SKILL.md`, same script, same on-disk layout. Drop it into `~/.claude/skills/goal/` and `~/.codex/skills/goal/` and both agents pick it up natively.

## What it does

When the agent says `$goal`, `/goal mode`, `start a goal`, or any equivalent goal-mode language, the skill:

1. Creates a fresh ledger under `.agent/runs/<goal-id>/` in the current project.
2. Writes a contract file (`GOAL.md`): objective, finishing criteria, escape hatch, parent goal.
3. Writes a single canonical state file (`implementation-notes.html`): a self-contained HTML page with a `Resume Here` block at the top and an embedded progress timeline.
4. Couples to the runtime goal: when the user is in Codex `/goal` mode, the absolute ledger path is dropped into the goal objective so the next agent on the thread knows exactly where to read and write.
5. Updates the HTML at every meaningful checkpoint: validation runs, implementation milestones, blockers, spec-vs-reality conflicts, compaction prep, final hand-off.

The progress timeline is rendered directly from an inline `progressEvents` array inside the HTML file. There is no separate `events.jsonl` to keep in sync — the page is its own history. Open the file locally and you get the whole story at a glance.

## Why one HTML file

Earlier versions of this skill used a sprawl of `PROGRESS.md`, `HANDOFF.md`, `events.jsonl`, and `CODEBASE_STATUS.md`. Agents got confused about which file was canonical. Humans got confused about which file to read. State drifted between them.

Goal Ledger collapses all of that into one self-contained HTML file:

- **Top** is a `Resume Here` block: status, current phase, blockers, next exact action, last validation, protected paths. Built so the next agent (or human) can resume in under a minute.
- **Middle** is `Decisions Outside The Spec`, `Changes And Tradeoffs`, `Validation`, `Evidence`. The execution record.
- **Bottom** is `Progress Timeline`. Rendered from an inline events array, no external file dependencies, no fetches against sibling files. Opens cleanly even when you double-click the HTML straight out of the file browser.

The HTML is the contract with the next agent. `GOAL.md` is the contract with the current agent. That's the whole system.

## What problem this actually solves

You ask Codex or Claude Code to do something multi-hour or multi-day. Halfway through it compacts, gets interrupted, or hands off to a new session. Without a ledger, the new agent picks up with vibes and a stale objective.

With this skill in `/goal` mode, the active goal text itself includes the ledger path. Compaction can drop the conversation history and the next agent still knows:

- where to read state
- what was already validated
- what's actively in progress
- what's blocked and why
- which paths are user-owned and out of bounds
- what the next exact action is

The skill is the difference between an agent that resumes work and an agent that re-explores the codebase.

## Install

### Claude Code

Add the marketplace, then install the plugin:

```text
/plugin marketplace add kingbootoshi/goal-ledger
/plugin install goal-ledger
```

Restart Claude Code if the skill does not appear immediately. After install, the skill triggers automatically on goal-mode language, or you can invoke it explicitly.

### OpenAI Codex CLI

Codex looks for skills at `~/.codex/skills/<name>/`. Drop the skill directory there:

```bash
git clone https://github.com/kingbootoshi/goal-ledger.git ~/.goal-ledger
mkdir -p ~/.codex/skills
ln -sfn ~/.goal-ledger/plugins/goal-ledger/skills/goal ~/.codex/skills/goal
```

Restart Codex if needed. Invoke explicitly with `$goal` or describe the work in goal-mode language and Codex will auto-select it.

Codex also ships a native `/goal` lifecycle (`/goal`, `/goal pause`, `/goal resume`, `/goal clear`). Enable it once in `~/.codex/config.toml`:

```toml
[features]
goals = true
```

When the native goal exists, the skill couples the ledger path directly into the runtime goal objective so compaction-safe continuation works end to end.

### One canonical location for both agents

If you prefer a single source of truth, keep the skill in one place and symlink it into both agents:

```bash
# clone once
git clone https://github.com/kingbootoshi/goal-ledger.git ~/.goal-ledger

# Claude Code
mkdir -p ~/.claude/skills
ln -sfn ~/.goal-ledger/plugins/goal-ledger/skills/goal ~/.claude/skills/goal

# Codex CLI
mkdir -p ~/.codex/skills
ln -sfn ~/.goal-ledger/plugins/goal-ledger/skills/goal ~/.codex/skills/goal
```

Both agents follow symlinks for skill discovery, so updates to the cloned repo flow to both automatically.

## Usage

Once installed, the skill activates on phrases like:

- `$goal`
- `/goal mode`
- `start a goal`
- `continue this goal`
- `chain goals`
- `agent progress ledger`
- `flight recorder`
- `implementation notes`

Typical session:

```text
$goal start migrating the auth service to the new schema. finishing criteria:
all integration tests green, old endpoints deleted, runbook updated.
```

The agent will:

1. Initialize the ledger under `.agent/runs/<goal-id>/`.
2. Write `GOAL.md` with the objective, finishing criteria, and escape hatch.
3. Write `implementation-notes.html` with a `Resume Here` block, decision sections, and an inline progress timeline.
4. Couple to `/goal` mode if available and drop the absolute ledger path into the runtime goal objective.
5. Update the HTML at every meaningful checkpoint while it works.

Open `.agent/runs/<goal-id>/implementation-notes.html` in a browser at any point to see live state.

## Layout

```text
.agent/
  GOALS.md                          # project-level index of all goals
  runs/
    <goal-id>/
      GOAL.md                       # contract: objective, finishing criteria, escape hatch
      implementation-notes.html     # canonical readable state + inline progress timeline
      evidence/                     # optional: bulky logs, screenshots, command output
```

## What lives in the HTML

- **Meta block**: goal id, started timestamp, parent goal, mode, objective.
- **Resume Here**: status, current phase, completed work, active work, blockers, next exact action, last validation, protected paths.
- **Progress Timeline**: scrollable list of compact event objects, rendered directly from an inline `progressEvents` array. No external file dependencies.
- **Decisions Outside The Spec**: where the spec was silent and the agent had to choose.
- **Changes And Tradeoffs**: where the spec and the repo disagreed, and how the agent reconciled.
- **Validation**: the commands that were run, what passed, what failed, what's still pending.
- **Evidence**: links to bulky proof files in `evidence/`.
- **Next Goal Candidates**: when this goal unlocks another, list it here.

## Status states

The skill uses six explicit states inside `implementation-notes.html`:

- `[todo]` known and not started
- `[doing]` currently active
- `[done]` completed and validated
- `[blocked]` waiting on external input or dependency
- `[incomplete]` attempted, not fully solvable inside current constraints
- `[abandoned]` intentionally stopped because the goal changed or no longer pays rent

`[incomplete]` is the honest fallback when a checkpoint is impossible inside current constraints. It carries a structured explanation: reason, proof, attempted, impact, next human/agent decision. This is the path that lets the agent tell the truth without quietly skipping work.

## Escape hatch

Every serious goal ships with an escape hatch in `GOAL.md`. The agent is told to pause, ask, or mark a scoped item `[blocked]` / `[incomplete]` if:

- validation contradicts the goal
- the goal requires a scope change
- the agent is looping without measurable progress
- the next step risks deleting or rewriting durable memory
- the PRD and actual repo disagree
- the ledger itself starts contaminating validation

This is the honesty path. It exists so the agent never has to lie or fake completion to satisfy the goal.

## Compatibility

Built against the open [Agent Skills](https://developers.openai.com/codex/skills) standard. Should work in any agent that scans a skills directory for `SKILL.md`:

| Agent | Personal path | Project path |
| --- | --- | --- |
| Claude Code | `~/.claude/skills/goal/` | `.claude/skills/goal/` |
| OpenAI Codex CLI | `~/.codex/skills/goal/` | `.agents/skills/goal/` or `.codex/skills/goal/` |
| Cursor | n/a | `.cursor/skills/goal/` |
| Google Antigravity | `~/.gemini/antigravity/skills/goal/` | `.agent/skills/goal/` |

The `agents/openai.yaml` sidecar is Codex-specific UI metadata. Other agents ignore it.

## License

MIT.
