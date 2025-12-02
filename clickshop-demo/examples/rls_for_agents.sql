-- =============================================================================
-- Row-Level Security for AI Agents with RDS Data API
-- =============================================================================
--
-- THE PATTERN: Shared DB User + Session Variables + RLS
--
-- Why not one DB user per agent?
--   • Managing dozens of database users/secrets adds complexity
--   • Connection pooling works better with fewer users
--
-- Solution: App sets session context → RLS filters on that context
--   1. App: SET LOCAL app.agent_type = 'order_agent';
--   2. RLS: USING (current_setting('app.agent_type') = ANY(agent_access))
--
-- =============================================================================


-- Track which agents can access each row
ALTER TABLE orders ADD COLUMN IF NOT EXISTS agent_access TEXT[] DEFAULT '{}';


-- RLS policy filters based on session context
CREATE POLICY agent_orders_policy ON orders
    FOR ALL
    USING (
        current_setting('app.agent_type', true) = ANY(agent_access)
    );

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;


-- =============================================================================
-- HOW IT WORKS
-- =============================================================================

-- MCP server (or your app) sets context per request:
SET LOCAL app.agent_type = 'order_agent';

-- Agent's query runs — RLS filters automatically:
SELECT order_id, customer_id, total_amount FROM orders;
-- ✓ Only sees rows where 'order_agent' is in agent_access


-- =============================================================================
-- WHY THIS IS SECURE
-- =============================================================================
--
--   [Agent] → [Trusted App Layer sets context] → [RLS enforces access]
--
--   • Your code (MCP server/app) determines agent identity
--   • Database enforces what that identity can see
--   • Even if agent writes malicious SQL, RLS still filters
--   • SQL injection can't bypass RLS policies
--
-- =============================================================================