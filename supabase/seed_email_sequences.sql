-- Seed file for email sequences
-- Run AFTER migration 026_email_system.sql
-- Can be run multiple times (uses ON CONFLICT)

-- =============================================================================
-- Email Templates
-- =============================================================================

INSERT INTO email_templates (id, name, subject, body_html, body_text, template_type, variables)
VALUES
  -- Day 0: Welcome + Checklist
  (
    'tpl_welcome_checklist',
    'Welcome Checklist',
    'Your Family Ski Trip Checklist',
    NULL, -- Load from file in agent
    'Welcome to Snowthere! Here''s your family ski trip checklist...',
    'welcome',
    '["name", "email"]'::jsonb
  ),
  -- Day 2: Alps vs Colorado
  (
    'tpl_welcome_day2',
    'Alps vs Colorado',
    'Wait... the Alps can be CHEAPER than Colorado?',
    NULL,
    'I know it sounds backwards. "Fly across the ocean to SAVE money?" But stick with me here...',
    'nurture',
    '["name", "email"]'::jsonb
  ),
  -- Day 4: Kids Ages
  (
    'tpl_welcome_day4',
    'Kids Ages Matter',
    'Your kids'' ages change EVERYTHING',
    NULL,
    'I see parents make this mistake all the time...',
    'nurture',
    '["name", "email"]'::jsonb
  ),
  -- Day 7: Epic vs Ikon
  (
    'tpl_welcome_day7',
    'Epic vs Ikon',
    'Epic vs Ikon: Let''s end the confusion',
    NULL,
    'Should we get the Epic Pass or Ikon Pass? Here''s the honest answer...',
    'nurture',
    '["name", "email"]'::jsonb
  ),
  -- Day 14: Ready to Pick
  (
    'tpl_welcome_day14',
    'Ready to Pick',
    'Ready to pick your resort?',
    NULL,
    'Two weeks ago, you signed up for the checklist. Now let''s put it all together...',
    'nurture',
    '["name", "email"]'::jsonb
  )
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  subject = EXCLUDED.subject,
  body_text = EXCLUDED.body_text,
  template_type = EXCLUDED.template_type,
  variables = EXCLUDED.variables,
  updated_at = NOW();

-- =============================================================================
-- Welcome Sequence
-- =============================================================================

INSERT INTO email_sequences (id, name, description, trigger_event, status)
VALUES (
  'seq_welcome',
  'Welcome Sequence',
  'Onboarding sequence for new subscribers: checklist, value education, resort selection framework',
  'signup',
  'active'
)
ON CONFLICT (id) DO UPDATE SET
  name = EXCLUDED.name,
  description = EXCLUDED.description,
  trigger_event = EXCLUDED.trigger_event,
  status = EXCLUDED.status,
  updated_at = NOW();

-- =============================================================================
-- Sequence Steps
-- =============================================================================

-- Clear existing steps for this sequence (to allow re-seeding)
DELETE FROM email_sequence_steps WHERE sequence_id = 'seq_welcome';

INSERT INTO email_sequence_steps (sequence_id, step_number, template_id, delay_days, subject_override)
VALUES
  -- Step 1: Day 0 - Welcome + Checklist (immediate)
  ('seq_welcome', 1, 'tpl_welcome_checklist', 0, NULL),
  -- Step 2: Day 2 - Alps vs Colorado
  ('seq_welcome', 2, 'tpl_welcome_day2', 2, NULL),
  -- Step 3: Day 4 - Kids Ages
  ('seq_welcome', 3, 'tpl_welcome_day4', 2, NULL),
  -- Step 4: Day 7 - Epic vs Ikon
  ('seq_welcome', 4, 'tpl_welcome_day7', 3, NULL),
  -- Step 5: Day 14 - Ready to Pick
  ('seq_welcome', 5, 'tpl_welcome_day14', 7, NULL);

-- =============================================================================
-- Verification
-- =============================================================================

-- Check what we created
SELECT
  s.name as sequence_name,
  s.status,
  COUNT(ss.id) as step_count
FROM email_sequences s
LEFT JOIN email_sequence_steps ss ON ss.sequence_id = s.id
WHERE s.id = 'seq_welcome'
GROUP BY s.id, s.name, s.status;

SELECT
  ss.step_number,
  t.name as template_name,
  t.subject,
  ss.delay_days
FROM email_sequence_steps ss
JOIN email_templates t ON t.id = ss.template_id
WHERE ss.sequence_id = 'seq_welcome'
ORDER BY ss.step_number;
