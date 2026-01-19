-- Agent Layer Memory Tables
-- Migration for agent memory, coordination, and hooks

-- ============================================
-- EPISODIC MEMORY: Past agent runs
-- ============================================

-- Agent episodes: Store completed runs for learning
CREATE TABLE agent_episodes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    run_id VARCHAR(100) NOT NULL,
    agent_name VARCHAR(50) NOT NULL,
    objective JSONB NOT NULL,
    plan JSONB NOT NULL,
    result JSONB,
    observation JSONB,
    success BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for episode queries
CREATE INDEX idx_agent_episodes_agent_name ON agent_episodes(agent_name);
CREATE INDEX idx_agent_episodes_run_id ON agent_episodes(run_id);
CREATE INDEX idx_agent_episodes_created_at ON agent_episodes(created_at DESC);
CREATE INDEX idx_agent_episodes_success ON agent_episodes(agent_name, success);

-- ============================================
-- SEMANTIC MEMORY: Learned patterns
-- ============================================

-- Agent patterns: Store learned patterns extracted from episodes
CREATE TABLE agent_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(50) NOT NULL,
    pattern_type VARCHAR(50) NOT NULL CHECK (pattern_type IN ('success', 'failure', 'optimization')),
    description TEXT NOT NULL,
    evidence JSONB DEFAULT '[]'::JSONB, -- Run IDs that support this pattern
    confidence FLOAT NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    applicable_contexts JSONB DEFAULT '[]'::JSONB,
    recommendation TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_validated TIMESTAMP WITH TIME ZONE
);

-- Indexes for pattern queries
CREATE INDEX idx_agent_patterns_agent_name ON agent_patterns(agent_name);
CREATE INDEX idx_agent_patterns_confidence ON agent_patterns(confidence DESC);
CREATE INDEX idx_agent_patterns_type ON agent_patterns(agent_name, pattern_type);

-- ============================================
-- COORDINATION: Agent-to-agent messages
-- ============================================

-- Agent messages: Message bus for agent coordination
CREATE TABLE agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    from_agent VARCHAR(50) NOT NULL,
    to_agent VARCHAR(50) NOT NULL,
    message_type VARCHAR(50) NOT NULL CHECK (message_type IN ('request', 'response', 'notification', 'handoff')),
    payload JSONB NOT NULL,
    priority INTEGER DEFAULT 5 CHECK (priority BETWEEN 1 AND 10),
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    correlation_id UUID, -- Links request/response pairs
    response JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for message queries
CREATE INDEX idx_agent_messages_to_agent ON agent_messages(to_agent);
CREATE INDEX idx_agent_messages_status ON agent_messages(to_agent, status);
CREATE INDEX idx_agent_messages_priority ON agent_messages(priority DESC);
CREATE INDEX idx_agent_messages_correlation ON agent_messages(correlation_id);
CREATE INDEX idx_agent_messages_created ON agent_messages(created_at DESC);

-- ============================================
-- HOOKS: Human intervention approvals
-- ============================================

-- Agent pending approvals: Human intervention points
CREATE TABLE agent_pending_approvals (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    hook_type VARCHAR(50) NOT NULL CHECK (hook_type IN (
        'pre_research', 'post_research', 'post_content', 'pre_publish',
        'on_low_confidence', 'on_error', 'on_quality_issue', 'on_high_cost'
    )),
    agent_name VARCHAR(50) NOT NULL,
    run_id VARCHAR(100) NOT NULL,
    context JSONB NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected', 'skip', 'expired')),
    modified_data JSONB, -- Optional modified data from human
    resolved_by VARCHAR(100),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    expires_at TIMESTAMP WITH TIME ZONE
);

-- Indexes for approval queries
CREATE INDEX idx_approvals_agent ON agent_pending_approvals(agent_name);
CREATE INDEX idx_approvals_status ON agent_pending_approvals(status);
CREATE INDEX idx_approvals_pending ON agent_pending_approvals(agent_name, status) WHERE status = 'pending';
CREATE INDEX idx_approvals_created ON agent_pending_approvals(created_at DESC);
CREATE INDEX idx_approvals_expires ON agent_pending_approvals(expires_at) WHERE status = 'pending';

-- ============================================
-- WORKING MEMORY: Current run context
-- (Optional - for distributed/persistent working memory)
-- ============================================

-- Agent working memory: Current run context (optional persistence)
CREATE TABLE agent_working_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(50) NOT NULL,
    run_id UUID NOT NULL,
    key VARCHAR(200) NOT NULL,
    value JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(agent_name, run_id, key)
);

-- Index for working memory queries
CREATE INDEX idx_working_memory_agent_run ON agent_working_memory(agent_name, run_id);

-- ============================================
-- CLEANUP: Automatic expiration
-- ============================================

-- Function to expire old pending approvals
CREATE OR REPLACE FUNCTION expire_pending_approvals()
RETURNS void AS $$
BEGIN
    UPDATE agent_pending_approvals
    SET status = 'expired', resolved_at = NOW()
    WHERE status = 'pending'
      AND expires_at IS NOT NULL
      AND expires_at < NOW();
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old working memory (call after runs complete)
CREATE OR REPLACE FUNCTION cleanup_working_memory(p_run_id UUID)
RETURNS void AS $$
BEGIN
    DELETE FROM agent_working_memory WHERE run_id = p_run_id;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- RLS POLICIES (Row Level Security)
-- ============================================

-- Enable RLS on all agent tables
ALTER TABLE agent_episodes ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_pending_approvals ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_working_memory ENABLE ROW LEVEL SECURITY;

-- Allow service role full access (agents run with service role)
CREATE POLICY "Service role has full access to agent_episodes"
    ON agent_episodes FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to agent_patterns"
    ON agent_patterns FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to agent_messages"
    ON agent_messages FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to agent_pending_approvals"
    ON agent_pending_approvals FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "Service role has full access to agent_working_memory"
    ON agent_working_memory FOR ALL
    USING (true)
    WITH CHECK (true);
