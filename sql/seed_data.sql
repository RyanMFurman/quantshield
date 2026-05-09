-- Minimal seed data for local testing

INSERT INTO security_events (event_id, event_type, source_ip, username, user_agent, result, raw_payload, occurred_at)
VALUES
('11111111-1111-4111-8111-111111111111', 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 7}', NOW() - INTERVAL '3 minutes'),
('22222222-2222-4222-8222-222222222222', 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 8}', NOW() - INTERVAL '2 minutes'),
('33333333-3333-4333-8333-333333333333', 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 9}', NOW() - INTERVAL '1 minute')
ON CONFLICT (event_id) DO NOTHING;
