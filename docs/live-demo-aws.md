# QuantShield Live Demo AWS Runbook

## Target Architecture

```text
Internet
  |
  v
Public EC2 app host
  |-- Nginx
  |-- Docker Compose
  |-- FastAPI service on 8000
  |-- Streamlit dashboard on 8501
  |
  v
RDS PostgreSQL
```

Keep the v1 demo under control by avoiding NAT Gateway, ALB, autoscaling, and
Kubernetes. One small public app host plus RDS is enough for a portfolio demo.

## Host Setup

Install packages on the app host:

```bash
sudo dnf update -y
sudo dnf install -y git nginx docker
sudo systemctl enable --now docker nginx
sudo usermod -aG docker ec2-user
```

Install Docker Compose if it is not already available as `docker compose`.

Clone the repo:

```bash
sudo mkdir -p /opt/quantshield
sudo chown ec2-user:ec2-user /opt/quantshield
git clone https://github.com/RyanMFurman/quantshield.git /opt/quantshield
cd /opt/quantshield
```

Create the app environment:

```bash
cp .env.example .env
```

Set:

```text
DATABASE_URL=postgresql://...
QUANTSHIELD_API_URL=https://api.example.com
```

See `docs/live-rds-app-config.md` for RDS security group and app environment
details.

## Run App Stack

```bash
docker compose up -d --build
curl http://127.0.0.1:8000/health
```

Install the systemd unit:

```bash
sudo cp deploy/systemd/quantshield-demo.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now quantshield-demo
```

## Nginx

Copy the example config:

```bash
sudo cp deploy/nginx/quantshield.conf.example /etc/nginx/conf.d/quantshield.conf
sudo nginx -t
sudo systemctl reload nginx
```

Replace:

```text
demo.example.com
api.example.com
```

with the final public DNS names.

## HTTPS

Point DNS records at the app host public IP before requesting certificates:

```text
demo.example.com -> app host public IP
api.example.com  -> app host public IP
```

Install Certbot:

```bash
sudo dnf install -y certbot
```

Stop Nginx and request certificates with the standalone challenge:

```bash
sudo systemctl stop nginx
sudo certbot certonly --standalone -d demo.example.com
sudo certbot certonly --standalone -d api.example.com
sudo systemctl start nginx
```

After certificates exist, copy `deploy/nginx/quantshield.conf.example`, replace
the example domains, and reload Nginx:

```bash
sudo nginx -t
sudo systemctl reload nginx
```

Verify renewal:

```bash
sudo certbot renew --dry-run
```

## Seed Demo Data

After the schema exists and `DATABASE_URL` is set:

```bash
docker compose exec api python scripts/seed_live_demo_data.py
```

Verify:

```bash
curl http://127.0.0.1:8000/market/latest
curl http://127.0.0.1:8000/alerts/active
curl http://127.0.0.1:8000/api/v1/insider-risk
```

## Scheduled Refresh

Install the refresh service and timer:

```bash
sudo cp deploy/systemd/quantshield-demo-refresh.service /etc/systemd/system/
sudo cp deploy/systemd/quantshield-demo-refresh.timer /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now quantshield-demo-refresh.timer
```

Run the refresh manually:

```bash
sudo systemctl start quantshield-demo-refresh.service
```

Check status and logs:

```bash
systemctl status quantshield-demo-refresh.timer
journalctl -u quantshield-demo-refresh.service -n 100 --no-pager
```
