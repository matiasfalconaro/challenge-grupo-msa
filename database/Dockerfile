# PostgreSQL oficial image
FROM postgres:16-alpine

# Copy initialization script
COPY init-postgres.sql /docker-entrypoint-initdb.d/

# El entrypoint de postgres ejecuta automáticamente los scripts en /docker-entrypoint-initdb.d
