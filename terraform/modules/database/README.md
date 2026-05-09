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
- `psql` installed and available on `PATH`, or `psql_command` set to an absolute executable path.

The schema creates the foundational QuantShield tables, including `market_prices`, `security_events`, `alerts`, and `incidents`, plus supporting indexes.

For Windows workstations where PostgreSQL command line tools are installed but not on `PATH`, set:

```hcl
psql_command = "C:\\Program Files\\PostgreSQL\\18\\bin\\psql.exe"
```

Set `initialize_seed_data = true` in a dev tfvars file to load `sql/seed_data.sql` after the schema is initialized. The seed file is PostgreSQL SQL and should be applied through `psql` against the RDS PostgreSQL endpoint, not a SQL Server/T-SQL query editor.
