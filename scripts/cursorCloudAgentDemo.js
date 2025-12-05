/**
 * Cursor Cloud Agent API demo.
 *
 * Covers every documented endpoint:
 * - GET /v0/me
 * - GET /v0/models
 * - GET /v0/repositories
 * - POST /v0/agents
 * - GET /v0/agents
 * - GET /v0/agents/{id}
 * - POST /v0/agents/{id}/followup
 * - GET /v0/agents/{id}/conversation
 * - POST /v0/agents/{id}/stop
 * - DELETE /v0/agents/{id}
 *
 * Usage (Node 18+ with built-in fetch):
 * RUN_CURSOR_DEMO=1 CURSOR_API_KEY=xxx CURSOR_REPO_URL=https://github.com/your/repo \
 * CURSOR_REPO_REF=main CURSOR_MODEL=claude-4-sonnet-thinking \
 * node scripts/cursorCloudAgentDemo.js
 */

const API_KEY = process.env.CURSOR_API_KEY;
const API_URL = process.env.CURSOR_API_URL || "https://api.cursor.com";
const DEMO_ENABLED = process.env.RUN_CURSOR_DEMO === "1";

const DEFAULTS = {
  model: process.env.CURSOR_MODEL || "claude-4-sonnet-thinking",
  repo: process.env.CURSOR_REPO_URL,
  ref: process.env.CURSOR_REPO_REF || "main",
  prompt:
    process.env.CURSOR_DEMO_PROMPT ||
    "Add a README with install, run, and troubleshooting sections.",
};

function requireEnv(value, name) {
  if (!value) {
    throw new Error(`Missing required env: ${name}`);
  }
  return value;
}

async function request(path, { method = "GET", body, query } = {}) {
  requireEnv(API_KEY, "CURSOR_API_KEY");
  const qs = query
    ? "?" +
      Object.entries(query)
        .filter(([, v]) => v !== undefined && v !== null)
        .map(
          ([k, v]) =>
            `${encodeURIComponent(k)}=${encodeURIComponent(String(v))}`
        )
        .join("&")
    : "";

  const res = await fetch(`${API_URL}${path}${qs}`, {
    method,
    headers: {
      Authorization: `Bearer ${API_KEY}`,
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  const raw = await res.text();
  const data = raw ? safeJson(raw) : null;
  if (!res.ok) {
    throw new Error(
      `HTTP ${res.status} ${res.statusText} for ${path}: ${JSON.stringify(
        data || raw
      )}`
    );
  }
  return data;
}

function safeJson(raw) {
  try {
    return JSON.parse(raw);
  } catch (err) {
    return raw;
  }
}

function logStep(title, payload) {
  console.log(`\n=== ${title} ===`);
  if (payload !== undefined) {
    console.dir(payload, { depth: 6, colors: true });
  }
}

// --- Endpoint wrappers ---

const api = {
  getMe: () => request("/v0/me"),
  listModels: () => request("/v0/models"),
  listRepositories: () => request("/v0/repositories"),
  createAgent: ({
    promptText,
    model = DEFAULTS.model,
    repository = DEFAULTS.repo,
    ref = DEFAULTS.ref,
    target = {},
    webhook,
    images,
  }) =>
    request("/v0/agents", {
      method: "POST",
      body: {
        prompt: { text: promptText, images },
        model,
        source: { repository, ref },
        target,
        webhook,
      },
    }),
  listAgents: ({ limit, cursor } = {}) =>
    request("/v0/agents", { query: { limit, cursor } }),
  getAgent: (id) => request(`/v0/agents/${id}`),
  addFollowup: (id, promptText, images) =>
    request(`/v0/agents/${id}/followup`, {
      method: "POST",
      body: { prompt: { text: promptText, images } },
    }),
  getConversation: (id) => request(`/v0/agents/${id}/conversation`),
  stopAgent: (id) =>
    request(`/v0/agents/${id}/stop`, { method: "POST" }),
  deleteAgent: (id) =>
    request(`/v0/agents/${id}`, { method: "DELETE" }),
};

// --- Demo flow that exercises every endpoint once ---

async function demo() {
  requireEnv(DEFAULTS.repo, "CURSOR_REPO_URL");
  requireEnv(API_KEY, "CURSOR_API_KEY");

  logStep("GET /v0/me", await api.getMe());
  logStep("GET /v0/models", await api.listModels());
  logStep("GET /v0/repositories", await api.listRepositories());

  logStep("POST /v0/agents (create)");
  const created = await api.createAgent({
    promptText: DEFAULTS.prompt,
    target: { autoCreatePr: false },
  });
  logStep("Created agent", created);

  const agentId = created.id;
  logStep("GET /v0/agents", await api.listAgents({ limit: 5 }));
  logStep("GET /v0/agents/{id}", await api.getAgent(agentId));

  logStep("POST /v0/agents/{id}/followup");
  await api.addFollowup(
    agentId,
    "Also include a short troubleshooting section."
  );

  logStep(
    "GET /v0/agents/{id}/conversation",
    await api.getConversation(agentId)
  );

  logStep("POST /v0/agents/{id}/stop", await api.stopAgent(agentId));
  logStep("DELETE /v0/agents/{id}", await api.deleteAgent(agentId));

  console.log("\nDemo complete. Agent was created, followed up, stopped, and deleted.");
}

if (require.main === module) {
  if (!DEMO_ENABLED) {
    console.log(
      "Demo is disabled. Set RUN_CURSOR_DEMO=1 to run the full flow. Export CURSOR_API_KEY and CURSOR_REPO_URL."
    );
    process.exit(0);
  }
  demo().catch((err) => {
    console.error("Demo failed:", err);
    process.exit(1);
  });
}

module.exports = { api, demo };

