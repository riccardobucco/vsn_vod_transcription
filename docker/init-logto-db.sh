#!/bin/bash
set -e

# Create the logto database and user if they don't exist
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'logto') THEN
            CREATE ROLE logto WITH LOGIN PASSWORD 'logto' CREATEROLE;
        END IF;
    END
    \$\$;

    SELECT 'CREATE DATABASE logto OWNER logto'
    WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'logto')\gexec
EOSQL
