-- Minimal seed data for local testing

INSERT INTO security_events (event_id, event_type, source_ip, username, user_agent, result, raw_payload, occurred_at)
VALUES
(gen_random_uuid(), 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 7}', NOW() - INTERVAL '3 minutes'),
(gen_random_uuid(), 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 8}', NOW() - INTERVAL '2 minutes'),
(gen_random_uuid(), 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 9}', NOW() - INTERVAL '1 minute');
