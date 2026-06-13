# CLAUDE.md — Autonome

## Project brief
Autonome is Ric Richardson's architecture for systems that accumulate judgment, not just knowledge. It extends the LLM-wiki pattern with a governed decision queue: structured files capture what is known; unresolved judgments surface as decisions, not tasks. Progressive autonomy — observe, recommend, draft, execute bounded work — with humans remaining sovereign over strategy, ethics, risk, money, law, credentials, and external commitments. Patent-backed concepts.

## Goals
- Build out the reference implementation: MCP server for agent access, knowledge graph (people, projects, companies, decisions, relationships), and decision queue interface.
- Keep architecture and documentation clear and aligned with the public positioning.
- Write code that demonstrates the authority ladder and governance boundary in practice.

## Constraints
- Subscription auth only. Never write, add, or log an Anthropic or LLM API key.
- No credentials or secrets in any committed file. All secrets (SUPABASE_ACCESS_TOKEN, ANTHROPIC_API_KEY) are injected by the CI runner via GitHub secrets.
- High-risk or irreversible actions remain human-approved — implement governance boundaries as hard gates, not soft warnings.
- Do not add features or abstractions beyond what the task requires.

## Write-quarantine rules
Do NOT commit to this repository:
- Patent-sensitive claim detail or specification language unless explicitly cleared for public release.
- Private operating records, internal Warp canon, or personal decision-queue entries.
- Credentials, commercial negotiations, or investor/unitholder detail.
- Private data-room material from unrelated projects.

## Warp event logging
For tasks dispatched from Warp, use the `warp-supabase` MCP server (configured in `.claude/settings.json`) to log progress and close the task row:

```sql
-- Log a step
SELECT cc_log_event('<task-id>', 'worker-step', '<what you did>');

-- Close the task
UPDATE tasks SET status = 'done', result = '<summary>' WHERE id = '<task-id>';
```

Log at least one `worker-step` per meaningful action and always close the task row (`done` or `failed`) before exiting.
