# 1. Navigate to CLI directory
cd /home/dev-soft/dprod/tools/cli

# 2. Install dependencies (if needed)
npm install

# 3. Test locally first
npm link  # Test the CLI locally

# 4. Login to npm (if not already)
npm login

# 5. Publish to npm
npm publish

# 3. Verify it's published
npm info dprod-cli

# Optional: If you want to test before publishing
npm pack  # Creates a tarball to test

# After Publishing
npm install -g dprod-cli@latest
# or
npm update -g dprod-cli