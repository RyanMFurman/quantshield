# Database Module

Creates a PostgreSQL RDS instance for QuantShield and initializes the application schema from the repo-level `sql/schema.sql`.

## Security

- RDS manages the master user password in AWS Secrets Manager through `manage_master_user_password`.
- The database is encrypted at rest with the default RDS KMS key.
- PostgreSQL ingress is limited to the configured CIDR blocks.
- Dev defaults make the database publicly reachable only from `admin_cidr` so connectivity can be tested.

## Schema Initialization

When `initialize_schema = true`, Terraform runs `sql/schema.sql` after the database is created. The local machine or CI runner applying Terraform must have:

- AWS CLI authenticated to read the RDS-managed secret.
- `psql` installed and available on `PATH`.

The schema creates the foundational QuantShield tables, including `market_prices`, `security_events`, `alerts`, and `incidents`, plus supporting indexes.
