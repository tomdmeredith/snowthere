-- Seed file for email sequences
-- Run AFTER migration 026_email_system.sql
-- Can be run multiple times (uses ON CONFLICT)

-- =============================================================================
-- Email Templates
-- Note: body_html will be populated by the agent from template files
-- =============================================================================

INSERT INTO email_templates (name, subject, preview_text, body_html, body_text, category, variables)
VALUES
  -- Day 0: Welcome + Checklist
  (
    'welcome_checklist',
    'Your Family Ski Trip Checklist',
    'Everything you need for your first family ski trip',
    '<p>Welcome! Here is your checklist.</p>',
    'Welcome to Snowthere! Here is your family ski trip checklist...',
    'sequence',
    '["name", "email"]'::jsonb
  ),
  -- Day 2: Alps vs Colorado
  (
    'welcome_day2',
    'Wait... the Alps can be CHEAPER than Colorado?',
    'I know it sounds backwards',
    '<p>Alps vs Colorado comparison</p>',
    'I know it sounds backwards. Fly across the ocean to SAVE money? But stick with me here...',
    'sequence',
    '["name", "email"]'::jsonb
  ),
  -- Day 4: Kids Ages
  (
    'welcome_day4',
    'Your kids'' ages change EVERYTHING',
    'I see parents make this mistake all the time',
    '<p>Kids ages guide</p>',
    'I see parents make this mistake all the time...',
    'sequence',
    '["name", "email"]'::jsonb
  ),
  -- Day 7: Epic vs Ikon
  (
    'welcome_day7',
    'Epic vs Ikon: Let''s end the confusion',
    'Should we get the Epic Pass or Ikon Pass?',
    '<p>Epic vs Ikon guide</p>',
    'Should we get the Epic Pass or Ikon Pass? Here is the honest answer...',
    'sequence',
    '["name", "email"]'::jsonb
  ),
  -- Day 14: Ready to Pick
  (
    'welcome_day14',
    'Ready to pick your resort?',
    'Two weeks ago, you signed up for the checklist',
    '<p>Ready to pick</p>',
    'Two weeks ago, you signed up for the checklist. Now let us put it all together...',
    'sequence',
    '["name", "email"]'::jsonb
  )
ON CONFLICT (name) DO UPDATE SET
  subject = EXCLUDED.subject,
  preview_text = EXCLUDED.preview_text,
  body_text = EXCLUDED.body_text,
  category = EXCLUDED.category,
  variables = EXCLUDED.variables,
  updated_at = NOW();

-- =============================================================================
-- Welcome Sequence
-- =============================================================================

INSERT INTO email_sequences (name, trigger_event, trigger_conditions, status)
VALUES (
  'welcome',
  'on_subscribe',
  '{}'::jsonb,
  'active'
)
ON CONFLICT (name) DO UPDATE SET
  trigger_event = EXCLUDED.trigger_event,
  trigger_conditions = EXCLUDED.trigger_conditions,
  status = EXCLUDED.status,
  updated_at = NOW();

-- =============================================================================
-- Sequence Steps
-- Uses CTEs to properly reference template and sequence UUIDs
-- =============================================================================

-- Get the sequence and template IDs, then insert steps
WITH seq AS (SELECT id FROM email_sequences WHERE name = 'welcome'),
     tpl AS (
       SELECT name, id FROM email_templates
       WHERE name IN ('welcome_checklist', 'welcome_day2', 'welcome_day4', 'welcome_day7', 'welcome_day14')
     )
INSERT INTO email_sequence_steps (sequence_id, step_number, template_id, delay_days)
SELECT
  seq.id,
  step_number,
  tpl.id,
  delay_days
FROM seq, (
  VALUES
    (1, 'welcome_checklist', 0),  -- Day 0: Immediate
    (2, 'welcome_day2', 2),       -- Day 2: +2 days
    (3, 'welcome_day4', 2),       -- Day 4: +2 days
    (4, 'welcome_day7', 3),       -- Day 7: +3 days
    (5, 'welcome_day14', 7)       -- Day 14: +7 days
) AS steps(step_number, template_name, delay_days)
JOIN tpl ON tpl.name = steps.template_name
ON CONFLICT (sequence_id, step_number) DO UPDATE SET
  template_id = EXCLUDED.template_id,
  delay_days = EXCLUDED.delay_days;

-- =============================================================================
-- Verification
-- =============================================================================

SELECT
  'Templates: ' || COUNT(*)::text as info
FROM email_templates
WHERE name LIKE 'welcome%';

SELECT
  s.name as sequence_name,
  s.status,
  COUNT(ss.id) as step_count
FROM email_sequences s
LEFT JOIN email_sequence_steps ss ON ss.sequence_id = s.id
WHERE s.name = 'welcome'
GROUP BY s.id, s.name, s.status;

SELECT
  ss.step_number,
  t.name as template_name,
  t.subject,
  ss.delay_days
FROM email_sequence_steps ss
JOIN email_templates t ON t.id = ss.template_id
JOIN email_sequences s ON s.id = ss.sequence_id
WHERE s.name = 'welcome'
ORDER BY ss.step_number;
