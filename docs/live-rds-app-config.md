# Live RDS and App Configuration

## Required Environment Variables

The app host needs these values at runtime:

```text
DATABASE_URL=postgresql://<user>:<password>@<rds-endpoint>:5432/<database>
QUANTSHIELD_API_URL=https://api.example.com
```

Use `.env.example` as the template, but do not commit the real `.env` file.

## Where Values Live

For the v1 demo host, place the real values in:

```text
/opt/quantshield/.env
```

Docker Compose reads those values when the stack starts:

```bash
cd /opt/quantshield
docker compose up -d --build
```

## RDS Access

The app host must be allowed to connect to RDS on PostgreSQL port `5432`.

Recommended v1 setup:

- RDS is not publicly open to the internet.
- RDS security group allows inbound PostgreSQL only from the app host security group.
- App host security group allows public inbound `80` and `443`.
- SSH should be restricted to the admin IP.

## Validation

From the app host:

```bash
docker compose exec api python -c "from src.api.database import fetch_all; print(fetch_all('SELECT 1 AS ok'))"
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/market/latest
curl http://127.0.0.1:8000/api/v1/insider-risk
```

From a public browser:

```text
https://api.example.com/health
https://demo.example.com
```

## Rotation

If the RDS password changes:

1. Update `/opt/quantshield/.env`.
2. Restart the stack:

```bash
sudo systemctl restart quantshield-demo
```

3. Rerun validation commands.
