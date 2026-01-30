-- Fix non-ASCII characters in resort slugs for URL safety
-- Unicode characters in URL path segments cause encoding/normalization issues
-- across browsers, CDNs, and edge runtimes

UPDATE resorts
SET slug = 'kitzbuhel'
WHERE slug = 'kitzbühel';
