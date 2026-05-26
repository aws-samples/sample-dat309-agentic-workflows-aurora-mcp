# Meridian — AgentCore CLI project (Phase 4)

Install the **Node-based** AgentCore CLI (preferred over the legacy Python starter toolkit):

```bash
npm install -g @aws/agentcore
agentcore --version
```

If you previously installed `bedrock-agentcore-starter-toolkit`, remove it — both use the `agentcore` command name.

## Quick start (workshop)

From `meridian/`:

```bash
# 1. Bootstrap CLI project (interactive) — or use the starter files in this folder
cd agentcore
agentcore validate

# 2. Add platform resources
agentcore add memory --name meridian-session --strategies SEMANTIC --expiry 30
agentcore add gateway --name meridian-aurora --authorizer-type AWS_IAM

# Example: expose postgres MCP or a Lambda OpenAPI target as Gateway tools
# agentcore add gateway-target \
#   --name AuroraSearch \
#   --type mcp-server \
#   --endpoint https://your-mcp-endpoint/mcp \
#   --gateway meridian-aurora

# 3. Optional — Node.js Runtime for the concierge (direct code deploy)
# See app/MeridianConcierge/README.md

# 4. Deploy (CDK under the hood)
agentcore deploy -y

# 5. Sync ARNs/URLs into meridian/.env for the FastAPI demo
cd ..
python scripts/sync_agentcore_env.py --write

# 6. Verify
agentcore status
agentcore invoke --runtime MeridianConcierge "Hello from Runtime"
```

## What gets deployed

| CLI resource | Phase 4 role | Adapter |
| ------------ | ------------ | ------- |
| **Runtime** | Session-isolated Strands/host agent | `backend/agentcore/runtime.py` |
| **Gateway** | Managed MCP (`tools/list`, `tools/call`) | `backend/agentcore/gateway.py` |
| **Memory** | Session store mirror | `backend/agentcore/memory.py` |
| **Identity** | Workload + resource credentials | `backend/agentcore/identity.py` |

Deployed metadata is written to `.cli/deployed-state.json` (auto-managed — **do not edit**).

The FastAPI workshop reads that file via `backend/agentcore/cli_config.py`.

## Local dev

```bash
agentcore dev              # local Runtime inspector (http://localhost:8080)
agentcore dev "Tokyo trip" # one-shot local invoke
agentcore logs             # CloudWatch logs after deploy
agentcore traces list      # OTEL traces
```

## Node.js Runtime (optional)

`app/MeridianConcierge/` is a TypeScript reference runtime for **direct Node deploy** on AgentCore Runtime (see AWS what's-new: Node.js CodeZip support). The main demo still runs Strands in FastAPI; deploy this when you want to show Runtime isolation end-to-end.

## Docs

- [AgentCore CLI get started](https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-get-started-cli.html)
- [GitHub: aws/agentcore-cli](https://github.com/aws/agentcore-cli)
- Presenter walkthrough: `docs/PRESENTER_CODE_WALKTHROUGH.md`
