# SQLAlchemy Alembic POC

## Commands

```shell
# Spin up postgres database container
docker compose up

# Spin up pgadmin UI, need to first override DATA_DIR in config.py to absolute path
uv run pgadmin4

# Autogenerate migration script
uv run alembic --config migrations/alembic.ini revision -m "create initial tables" --autogenerate

# Run migration
uv run alembic --config migrations/alembic.ini upgrade head

# Revert migration
uv run alembic --config migrations/alembic.ini downgrade -1
```