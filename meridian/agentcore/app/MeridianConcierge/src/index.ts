/**
 * Meridian Concierge — minimal Node.js runtime entry for AgentCore CLI deploy.
 *
 * AgentCore Runtime expects HTTP on port 8080 (or MCP on 8000). Extend this
 * handler to host your Strands agent when deploying with:
 *
 *   agentcore add agent --name MeridianConcierge --language Node ...
 *   agentcore deploy -y
 */
import http from "node:http";

const PORT = Number(process.env.PORT ?? 8080);

const server = http.createServer(async (req, res) => {
  if (req.method === "GET" && req.url === "/health") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify({ status: "ok", service: "meridian-concierge-runtime" }));
    return;
  }

  if (req.method === "POST" && req.url === "/invocations") {
    const chunks: Buffer[] = [];
    for await (const chunk of req) chunks.push(chunk as Buffer);
    const body = Buffer.concat(chunks).toString("utf-8");
    let prompt = body;
    try {
      const parsed = JSON.parse(body) as { prompt?: string; message?: string };
      prompt = parsed.prompt ?? parsed.message ?? body;
    } catch {
      /* plain text payload */
    }

    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(
      JSON.stringify({
        message: `MeridianConcierge (AgentCore Runtime) received: ${prompt.slice(0, 200)}`,
        note: "Replace this stub with Strands Agent + @tool memory in production.",
      }),
    );
    return;
  }

  res.writeHead(404);
  res.end("Not found");
});

server.listen(PORT, "0.0.0.0", () => {
  console.log(`MeridianConcierge listening on :${PORT}`);
});
