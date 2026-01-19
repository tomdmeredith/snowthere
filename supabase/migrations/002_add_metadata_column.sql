-- Add metadata column to agent_audit_log table
-- This was missing from the initial migration but is expected by the agent code

ALTER TABLE agent_audit_log
ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- Add a comment explaining the column
COMMENT ON COLUMN agent_audit_log.metadata IS 'Generic metadata field for storing additional audit context (run_id, etc.)';
