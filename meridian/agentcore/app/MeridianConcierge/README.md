# Meridian Concierge — Node.js reference runtime for AgentCore

Optional TypeScript runtime deployed via **AgentCore CLI** (Node.js CodeZip or Container).

```bash
# From meridian/agentcore after adding the runtime to agentcore.json:
agentcore add agent \
  --name MeridianConcierge \
  --language Node \
  --framework Strands \
  --protocol HTTP \
  --build CodeZip

agentcore deploy -y
agentcore invoke --runtime MeridianConcierge "Tokyo trip for two in October"
```

This folder is a **minimal HTTP health server** showing the Node deploy path. Wire your Strands concierge entrypoint to `src/index.ts` for production.

See: [AgentCore Runtime Node.js direct code deployment](https://aws.amazon.com/about-aws/whats-new/2026/04/amazon-bedrock-agentcore-runtime/)
