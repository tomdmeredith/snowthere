-- GDPR/CCPA data requests (access, deletion)
CREATE TABLE IF NOT EXISTS data_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL,
  request_type TEXT NOT NULL CHECK (request_type IN ('deletion', 'access')),
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed')),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  completed_at TIMESTAMPTZ
);

-- Rate limit index: one request per email per type per day
CREATE UNIQUE INDEX IF NOT EXISTS idx_data_requests_rate_limit
  ON data_requests (email, request_type, (created_at::date));

-- Enable RLS
ALTER TABLE data_requests ENABLE ROW LEVEL SECURITY;

-- No public read access — admin only
CREATE POLICY "Service role only" ON data_requests
  FOR ALL
  USING (false);
