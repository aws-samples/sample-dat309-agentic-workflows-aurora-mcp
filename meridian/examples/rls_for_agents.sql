-- =============================================================================
-- Row-Level Security for Meridian agents
-- =============================================================================
--
-- ┌──────────────────────────┬───────────────────────────┬──────────────────────────────────┐
-- │ Table                    │ Policy                    │ Scoped by                        │
-- ├──────────────────────────┼───────────────────────────┼──────────────────────────────────┤
-- │ traveler_preferences     │ rls_prefs_traveler        │ app.current_traveler_id          │
-- │ trip_interactions        │ rls_interactions_traveler │ app.current_traveler_id          │
-- │ conversations            │ rls_conversations_traveler│ app.current_traveler_id          │
-- │ conversation_messages    │ rls_messages_traveler     │ via conversations FK → same GUC  │
-- │ bookings                 │ rls_bookings_agent_type   │ app.agent_type ∈ agent_access[]  │
-- └──────────────────────────┴───────────────────────────┴──────────────────────────────────┘
--
-- How GUC + RLS enforcement works (transaction-scoped):
--
--   1. BEGIN transaction
--   2. set_config('app.current_traveler_id', 'trv_xxx', true)
--                                                        ^^^^
--                                          third arg = true → SET LOCAL (transaction-scoped)
--   3. All queries in this TX see only rows matching that traveler_id
--   4. COMMIT → GUC vanishes automatically, zero leakage risk
--
--   Why transaction-scoped?
--   • If the agent crashes mid-turn, the GUC dies with the aborted TX
--   • Connections returned to a pool carry no residual identity
--   • No explicit cleanup needed — Postgres handles it
--
-- Relationship to AgentCore Identity (FAQ):
--
--   AgentCore Identity and Aurora RLS are complementary but independent:
--
--   ┌─────────────────────┬──────────────────────────────────────────────────┐
--   │ AgentCore Identity  │ Resolves WHO is calling (IAM + workload identity)│
--   │                     │ → lives in the application layer (client-side)   │
--   ├─────────────────────┼──────────────────────────────────────────────────┤
--   │ Aurora RLS + GUC    │ Enforces WHAT rows they can see                  │
--   │                     │ → lives in the PostgreSQL engine (server-side)   │
--   └─────────────────────┴──────────────────────────────────────────────────┘
--
--   Flow: Identity resolves principal → app maps it to traveler_id →
--         app calls set_config() → Aurora RLS filters rows.
--   If Identity were removed, RLS still works. You'd just lose the audit
--   trail of which IAM principal triggered the turn.
--
-- Two RLS patterns the demo enforces against Aurora:
--
--   A) Per-traveler memory isolation (Phase 4)
--      App: SELECT set_config('app.current_traveler_id', :tid, true)
--      RLS: USING (traveler_id = current_setting('app.current_traveler_id', true))
--
--      The Strands MemoryAgent sets this GUC inside the same transaction as the
--      memory SELECT.  Even if the agent forgets the WHERE clause, Aurora will
--      not return another traveler's preferences, messages, or interactions.
--
--   B) Agent-type scoping for booking writes (booking flow)
--      App: SELECT set_config('app.agent_type', 'booking_agent', true)
--      RLS: USING (current_setting('app.agent_type', true) = ANY(agent_access))
--
--      Search-only agents cannot read or mutate confirmed bookings even though
--      they share the same DB role.
--
-- Both are deployed by `python scripts/init_aurora_schema.py`.
--
-- AWS docs:
--   RDS Data API (app sets GUCs via ExecuteStatement inside a transaction):
--     https://docs.aws.amazon.com/rdsdataservice/latest/APIReference/API_BeginTransaction.html
--   Aurora PostgreSQL:
--     https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/Aurora.AuroraPostgreSQL.html
--   PostgreSQL RLS (Aurora PostgreSQL compatible):
--     https://www.postgresql.org/docs/current/ddl-rowsecurity.html
-- =============================================================================
-- ----------------------------------------------------------------------------
-- A. Per-traveler isolation on Phase 4 memory tables
-- ----------------------------------------------------------------------------
ALTER TABLE traveler_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversation_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE trip_interactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS rls_prefs_traveler ON traveler_preferences;
DROP POLICY IF EXISTS rls_messages_traveler ON conversation_messages;
DROP POLICY IF EXISTS rls_interactions_traveler ON trip_interactions;
DROP POLICY IF EXISTS rls_conversations_traveler ON conversations;
CREATE POLICY rls_prefs_traveler ON traveler_preferences FOR ALL USING (
    traveler_id = current_setting('app.current_traveler_id', true)
    OR current_setting('app.current_traveler_id', true) = ''
);
CREATE POLICY rls_interactions_traveler ON trip_interactions FOR ALL USING (
    traveler_id = current_setting('app.current_traveler_id', true)
    OR current_setting('app.current_traveler_id', true) = ''
);
CREATE POLICY rls_conversations_traveler ON conversations FOR ALL USING (
    traveler_id = current_setting('app.current_traveler_id', true)
    OR current_setting('app.current_traveler_id', true) = ''
);
-- conversation_messages joins to conversations to derive the traveler.
CREATE POLICY rls_messages_traveler ON conversation_messages FOR ALL USING (
    current_setting('app.current_traveler_id', true) = ''
    OR conversation_id IN (
        SELECT conversation_id
        FROM conversations
        WHERE traveler_id = current_setting('app.current_traveler_id', true)
    )
);
-- The empty-string fallback above lets seed scripts and admin tooling read
-- without a session variable set.  Production code paths always set it.
-- ----------------------------------------------------------------------------
-- B. Agent-type scoping on bookings
-- ----------------------------------------------------------------------------
ALTER TABLE bookings
ADD COLUMN IF NOT EXISTS agent_access TEXT [] DEFAULT ARRAY ['booking_agent', 'supervisor_agent', 'concierge_agent'];
UPDATE bookings
SET agent_access = ARRAY ['booking_agent', 'supervisor_agent', 'concierge_agent']
WHERE agent_access IS NULL;
DROP POLICY IF EXISTS rls_bookings_agent_type ON bookings;
CREATE POLICY rls_bookings_agent_type ON bookings FOR ALL USING (
    current_setting('app.agent_type', true) = ''
    OR current_setting('app.agent_type', true) = ANY(agent_access)
);
ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;
-- ----------------------------------------------------------------------------
-- C. Lightweight audit log written by the agent runtime
-- ----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS agent_audit_log (
    audit_id VARCHAR(50) PRIMARY KEY,
    traveler_id VARCHAR(50),
    agent_name VARCHAR(100) NOT NULL,
    operation VARCHAR(100) NOT NULL,
    rls_traveler TEXT,
    rls_agent_type TEXT,
    iam_identity TEXT,
    rows_returned INTEGER,
    ran_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_audit_traveler ON agent_audit_log(traveler_id, ran_at DESC);
CREATE INDEX IF NOT EXISTS idx_audit_agent ON agent_audit_log(agent_name, ran_at DESC);
CREATE OR REPLACE VIEW agent_iam_audit AS
SELECT audit_id,
    ran_at,
    agent_name,
    operation,
    traveler_id,
    rls_traveler,
    rls_agent_type,
    iam_identity,
    rows_returned
FROM agent_audit_log
ORDER BY ran_at DESC;
COMMENT ON VIEW agent_iam_audit IS 'Per-turn record of which agent ran which operation under which IAM identity ' 'and RLS session variables.  Operators query this to verify scoping.';