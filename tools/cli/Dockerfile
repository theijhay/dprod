FROM node:18

WORKDIR /app

# Copy package files
COPY tools/cli/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY tools/cli/ .

# Set executable permissions
RUN chmod +x bin/dprod

# Expose port (if needed)
EXPOSE 3000

# Run the CLI
CMD ["node", "src/index.js"]
