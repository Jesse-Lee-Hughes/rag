FROM postgres:16

# Install pgvector extension
RUN apt-get update && apt-get install -y postgresql-16-pgvector

# Copy the initialization script
COPY init-db.sh /docker-entrypoint-initdb.d/

# Make the initialization script executable
RUN chmod +x /docker-entrypoint-initdb.d/init-db.sh