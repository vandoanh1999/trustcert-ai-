# Use the official Redis image from Docker Hub
FROM redis:7-alpine

# Expose the default Redis port
EXPOSE 6379

# The command to start Redis server
CMD ["redis-server"]
