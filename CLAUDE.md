# Working on this repo

Chris Antosiewicz's portfolio project: a sourced MLS sponsorship dataset plus a
daily pipeline that publishes a Quarto page. This file routes; detail lives in
each folder's `CONTEXT.md`. Full project brief: the Claude project chat.

## Rules for every session

- **Chris writes the SQL and most of the code.** Explain, give small worked
  examples on toy data, review his work, and ask him to explain his choices.
  Write full code only for boilerplate (config, workflow YAML, plotting setup,
  the test runner) or when he asks and the learning value is low.
- On Oct 26, 2026 Chris asked Claude to build the whole foundation at once and
  teach it afterward. `docs/WALKTHROUGH.md` is that teaching plan; work through
  it with him before new features, and don't count Claude-built code as his
  evidence in `docs/SKILL_TRACKER.md` until he can explain it.
- Name the skill each task practices (see `docs/SKILL_TRACKER.md`).
- **Honesty:** pageviews are a proxy for public attention, never "sponsor
  value". Reported deal values are "reported", with a source. Never invent
  sponsors, data or results.
- **Data terms:** check a source's terms before designing around it, and credit
  it. YouTube is out. No scraping Instagram, TikTok or X.
- $0 budget; up to $50 only if essential, and ask first.
- Short, direct feedback. Lead with the answer.

## Route by what you're doing

| Situation | Read |
|-----------|------|
| Start of a session, or end of the week | `docs/CONTEXT.md` |
| Walkthrough with Chris | `docs/WALKTHROUGH.md`, the current section only |
| Researching or adding sponsorship rows | `data/CONTEXT.md` |
| Writing or reviewing a SQL model | `sql/CONTEXT.md` |
| Writing or reviewing a data test | `tests/CONTEXT.md` |
| Ingestion scripts or their unit tests | `python/CONTEXT.md` |
| The page or its charts | `site/CONTEXT.md` |
| A past decision ("why is it like this?") | `docs/DECISIONS.md` |
| Pipeline overview for a visitor | `README.md` |

Load only the row you need. Nothing ships without Chris reviewing it in a PR.
