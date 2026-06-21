-- Minimal seed data for local testing and the live QuantShield demo.

INSERT INTO market_prices (symbol, price, volume, prev_close, captured_at)
VALUES
('SPY', 525.1200, 48000000, 524.8000, NOW() - INTERVAL '8 minutes'),
('QQQ', 449.3300, 36000000, 448.9000, NOW() - INTERVAL '7 minutes'),
('AAPL', 189.4500, 42000000, 188.9500, NOW() - INTERVAL '6 minutes'),
('MSFT', 414.9000, 24000000, 413.5000, NOW() - INTERVAL '5 minutes'),
('NVDA', 965.0000, 2500000, 900.0000, NOW() - INTERVAL '4 minutes');

INSERT INTO security_events (event_id, event_type, source_ip, username, user_agent, result, raw_payload, occurred_at)
VALUES
('11111111-1111-4111-8111-111111111111', 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 1, "symbol": "NVDA", "demo_batch": "live-demo"}', NOW() - INTERVAL '6 minutes'),
('22222222-2222-4222-8222-222222222222', 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 2, "symbol": "NVDA", "demo_batch": "live-demo"}', NOW() - INTERVAL '5 minutes'),
('33333333-3333-4333-8333-333333333333', 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 3, "symbol": "NVDA", "demo_batch": "live-demo"}', NOW() - INTERVAL '4 minutes'),
('44444444-4444-4444-8444-444444444444', 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 4, "symbol": "NVDA", "demo_batch": "live-demo"}', NOW() - INTERVAL '3 minutes'),
('55555555-5555-4555-8555-555555555555', 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 5, "symbol": "NVDA", "demo_batch": "live-demo"}', NOW() - INTERVAL '2 minutes'),
('66666666-6666-4666-8666-666666666666', 'ConsoleLogin', '198.51.100.10', 'trading-svc', 'Mozilla/5.0', 'Failure', '{"count": 6, "symbol": "NVDA", "demo_batch": "live-demo"}', NOW() - INTERVAL '1 minute'),
('77777777-7777-4777-8777-777777777777', 'GetObject', '198.51.100.10', 'trading-svc', 'aws-cli/2.15', 'Success', '{"bucket": "quant-research", "object": "nvda-model-inputs.csv", "symbol": "NVDA", "demo_batch": "live-demo"}', NOW() - INTERVAL '2 minutes'),
('88888888-8888-4888-8888-888888888888', 'ConsoleLogin', '203.0.113.40', 'analyst01', 'Mozilla/5.0', 'Success', '{"symbol": "MSFT", "demo_batch": "live-demo-noise"}', NOW() - INTERVAL '9 minutes')
ON CONFLICT (event_id) DO NOTHING;
