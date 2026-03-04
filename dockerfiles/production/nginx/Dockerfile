# =============================================================================
# Dockerfile for Nginx - Production
# =============================================================================

FROM nginx:1.27-alpine

# Remove default nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom config
COPY dockerfiles/production/nginx/default.conf /etc/nginx/conf.d/

CMD ["nginx", "-g", "daemon off;"]
