-- Contact form submissions
-- Stores messages from the /contact page

CREATE TABLE IF NOT EXISTS contact_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- Contact info
    name TEXT NOT NULL,
    email TEXT NOT NULL,

    -- Message details
    subject TEXT NOT NULL,
    message TEXT NOT NULL,

    -- Metadata
    ip_address TEXT,
    user_agent TEXT,
    referrer TEXT,

    -- Status tracking
    status TEXT NOT NULL DEFAULT 'new',  -- new, read, replied, archived
    replied_at TIMESTAMPTZ,

    -- Timestamps
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Enable RLS
ALTER TABLE contact_submissions ENABLE ROW LEVEL SECURITY;

-- Service role can do everything
CREATE POLICY "Service role full access on contact_submissions"
    ON contact_submissions
    FOR ALL
    TO service_role
    USING (true)
    WITH CHECK (true);

-- Create index for status filtering
CREATE INDEX idx_contact_submissions_status ON contact_submissions(status);
CREATE INDEX idx_contact_submissions_created_at ON contact_submissions(created_at DESC);

-- Add comment
COMMENT ON TABLE contact_submissions IS 'Contact form submissions from website visitors';
