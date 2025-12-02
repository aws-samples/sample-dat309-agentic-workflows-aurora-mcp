-- =============================================================================
-- Row-Level Security for AI Agents: The RDS Data API Challenge
-- =============================================================================
--
-- THE PROBLEM: RDS Data API = single IAM admin user for ALL connections
--   ❌ current_user is always "admin" - can't distinguish agents!
--
-- THE SOLUTION: App sets session variables → RLS filters on those variables
--   ✅ App: SET app.agent_type = 'order_agent'
--   ✅ RLS: USING (current_setting('app.agent_type') = ANY(agent_access))
--
-- =============================================================================


-- Step 1: Track which agents can access each order
ALTER TABLE orders ADD COLUMN IF NOT EXISTS agent_access TEXT[] DEFAULT '{}';


-- Step 2: RLS policy - agents only see orders they're authorized for
CREATE POLICY agent_orders_policy ON orders
    FOR ALL
    USING (
        current_setting('app.agent_type', true) = ANY(agent_access)
    );

ALTER TABLE orders ENABLE ROW LEVEL SECURITY;


-- Step 3: Tag orders with authorized agents
UPDATE orders SET agent_access = ARRAY['order_agent', 'supervisor_agent'];


-- =============================================================================
-- HOW IT WORKS IN PRACTICE
-- =============================================================================

-- MCP server (or your app) sets context at start of each request:
SET LOCAL app.agent_id = 'order_001';
SET LOCAL app.agent_type = 'order_agent';

-- Then agent's query runs - RLS filters automatically:
SELECT order_id, customer_id, total_amount FROM orders;
-- ✓ Only sees orders where 'order_agent' is in agent_access array

-- Different agent, different context, different results:
SET LOCAL app.agent_type = 'search_agent';
SELECT order_id, customer_id, total_amount FROM orders;
-- ✓ Returns nothing - search_agent not in agent_access


-- =============================================================================
-- KEY INSIGHT
-- =============================================================================
--
--   [AI Agent] → [MCP Server sets context] → [RLS enforces access]
--
--   • App determines WHO the agent is (flexible)
--   • Database enforces WHAT they can see (secure)
--   • Even malicious SQL can't bypass RLS
--
-- =============================================================================