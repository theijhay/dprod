# Terminal 1: Backend services
./scripts/start-dev.sh
npm run dev:api

# Terminal 2: Link CLI (run once)
npm run dev:cli

# Terminal 3: Test deployment
cd ~/example-nodejs-app
dprod deploy

# Watch it work! 🎉
# CLI talks to your local API at localhost:8000
# API uses AI to detect project
# Deployment happens with Docker stats monitoring