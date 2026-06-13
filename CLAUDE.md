# CLAUDE.md — Autonome

## Project brief
Autonome is Ric Richardson's architecture for systems that accumulate judgment, not just knowledge. It extends the LLM-wiki pattern with a governed decision queue: structured files capture what is known; unresolved judgments surface as decisions, not tasks. Progressive autonomy — observe, recommend, draft, execute bounded work — with humans remaining sovereign over strategy, ethics, risk, money, law, credentials, and external commitments. Patent-backed concepts.

## Goals
- Build out the reference implementation: MCP server for agent access, knowledge graph (people, projects, companies, decisions, relationships), and decision queue interface.
- Keep architecture and documentation clear and aligned with the public positioning.
- Write code that demonstrates the authority ladder and governance boundary in practice.

## Constraints
- Subscription auth only. Never write, add, or log an Anthropic or LLM API key.
- No credentials or secrets in any committed file. All secrets (SUPABASE_ACCESS_TOKEN, ANTHROPIC_API_KEY, WARP_WRITE_KEY) are injected by the CI runner via GitHub secrets.
- High-risk or irreversible actions remain human-approved — implement governance boundaries as hard gates, not soft warnings.
- Do not add features or abstractions beyond what the task requires.

## Write-quarantine rules
Do NOT commit to this repository:
- Patent-sensitive claim detail or specification language unless explicitly cleared for public release.
- Private operating records, internal Warp canon, or personal decision-queue entries.
- Credentials, commercial negotiations, or investor/unitholder detail.
- Private data-room material from unrelated projects.

## Report-back requirements (Warp-dispatched tasks)

The triggering issue body contains the task ID in this format:
```
Warp task: `TSK-YYYYMMDD-XXXX`
```

### (a) Branch and pull request — mandatory

Never commit code changes directly to `main`. For every Warp task:
1. Create a branch: `git checkout -b warp/<task-id>` (e.g. `warp/TSK-20260613-CWT4`)
2. Make all changes on that branch, commit, and push.
3. Open a pull request targeting `main` before exiting.

### (b) Write a cloud-build event on completion

Use the `WARP_WRITE_KEY` secret injected by CI — **not** `SUPABASE_ACCESS_TOKEN`:

```bash
TASK_ID="TSK-..."            # extracted from issue body
SUPABASE_URL="https://uswnbpyiepoaceretjjj.supabase.co"
SUMMARY="one-sentence description of what you did"

curl -s -X POST "$SUPABASE_URL/rest/v1/events" \
  -H "Authorization: Bearer $WARP_WRITE_KEY" \
  -H "apikey: $WARP_WRITE_KEY" \
  -H "Content-Type: application/json" \
  --data "$(jq -n --arg kind cloud-build --arg task_id "$TASK_ID" --arg body "$SUMMARY" \
    '{kind:$kind,task_id:$task_id,body:$body}')"
```

### (c) Close the task row

```bash
curl -s -X PATCH "$SUPABASE_URL/rest/v1/tasks?id=eq.$TASK_ID" \
  -H "Authorization: Bearer $WARP_WRITE_KEY" \
  -H "apikey: $WARP_WRITE_KEY" \
  -H "Content-Type: application/json" \
  --data "$(jq -n --arg status done --arg result "$SUMMARY" \
    '{status:$status,result:$result}')"
```

Use `"status":"failed"` and include the error in `result` if the task could not be completed.

### In-progress logging

Use the `warp-supabase` MCP (SUPABASE_ACCESS_TOKEN) for step logging during the task:
```sql
SELECT cc_log_event('<task-id>', 'worker-step', '<what you did>');
```
Log at least one `worker-step` per meaningful action.
