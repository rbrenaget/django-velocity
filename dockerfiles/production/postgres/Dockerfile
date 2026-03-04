# =============================================================================
# Dockerfile for Django Velocity - PostgreSQL Production
# =============================================================================

FROM postgres:16-alpine

# Set bash as shell
RUN apk add --no-cache bash

# Set default env variables (can be overridden by docker-compose)
ENV BACKUP_DIR=/backups
# Copy maintenance scripts to be available globally
COPY ./dockerfiles/production/postgres/scripts/ /usr/local/bin/

# Make scripts executable
RUN chmod +x /usr/local/bin/backup \
    /usr/local/bin/restore \
    /usr/local/bin/rmbackup \
    /usr/local/bin/list \
    /usr/local/bin/cleanup

ENV BACKUP_MAX_AGE_DAYS=30
ENV BACKUP_MAX_COUNT=50

# Create backup directory
RUN mkdir -p ${BACKUP_DIR} && \
    chown -R postgres:postgres ${BACKUP_DIR}

ENTRYPOINT ["docker-entrypoint.sh"]
CMD ["postgres"]
