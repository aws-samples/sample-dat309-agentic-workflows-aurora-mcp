-- =============================================================================
-- Row-Level Security for AI Agents with RDS Data API (travel schema)
-- =============================================================================
--
-- Pattern: shared DB user + session variables + RLS
--   1. App: SET LOCAL app.agent_type = 'booking_agent';
--   2. RLS: USING (current_setting('app.agent_type') = ANY(agent_access))
--
-- Example table: bookings (see backend/db/schema.sql)

ALTER TABLE bookings ADD COLUMN IF NOT EXISTS agent_access TEXT[]
    DEFAULT ARRAY['booking_agent', 'supervisor_agent', 'concierge_agent'];

UPDATE bookings SET agent_access = ARRAY['booking_agent', 'supervisor_agent', 'concierge_agent']
WHERE agent_access IS NULL;

CREATE POLICY agent_bookings_policy ON bookings
    FOR ALL
    USING (
        current_setting('app.agent_type', true) = ANY(agent_access)
    );

ALTER TABLE bookings ENABLE ROW LEVEL SECURITY;

-- Application code (Python via RDS Data API):
-- execute("SET LOCAL app.agent_type = 'booking_agent'")
-- execute("SELECT booking_id, traveler_id, total_amount FROM bookings")
-- RLS filters rows automatically per agent type.
