FROM node:18

WORKDIR /app

# Copy package files
COPY tools/frontend/package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY tools/frontend/ .

# Expose port
EXPOSE 3000

# Run the development server
CMD ["npm", "run", "dev"]
