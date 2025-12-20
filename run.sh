# Terminal 1: Backend services
./scripts/start-dev.sh
npm run dev:api

# Terminal 2: Link CLI (run once)
npm run dev:cli

# Terminal 3: Test deployment
cd ~/example-nodejs-app
dprod deploy