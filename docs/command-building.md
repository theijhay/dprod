# Dprod CLI Command Documentation
## Complete Specification for the `dprod` CLI Tool

---

# CLI Architecture Overview

## 🎯 Design Principles

1. **Zero Configuration**: No config files needed
2. **Instant Feedback**: Real-time progress and logs
3. **Intelligent Defaults**: Smart auto-detection everywhere
4. **Beautiful UX**: Clean, informative terminal output
5. **Cross-Platform**: Works on Windows, macOS, Linux

## 📦 Package Structure

```
dprod-cli/
├── src/
│   ├── index.js              # Main entry point
│   ├── commands/             # All command implementations
│   │   ├── deploy.js         # Core deploy command
│   │   ├── login.js          # Authentication
│   │   ├── logout.js         # Logout
│   │   ├── status.js         # Project status
│   │   ├── logs.js           # View logs
│   │   └── list.js           # List projects
│   ├── lib/
│   │   ├── auth.js           # Authentication manager
│   │   ├── api.js            # API client
│   │   ├── config.js         # Configuration management
│   │   ├── detector.js       # Project detection
│   │   ├── packager.js       # Code packaging
│   │   ├── logger.js         # Logging utilities
│   │   └── ui.js             # Terminal UI components
│   └── utils/
│       ├── files.js          # File system utilities
│       ├── validation.js     # Input validation
│       └── errors.js         # Error handling
├── bin/
│   └── dprod            # CLI binary
├── package.jsondprod
└── README.md
```

---

# Command Specifications

## 🚀 Core Command: `deployzero deploy`

### Command Structure
```bash
dprod deploy [options] [project-name]
```

### Options
```bash
--name, -n <name>      # Project name (default: directory name)
--env, -e <file>       # Environment file to include
--detach, -d           # Don't stream logs, return immediately
--force, -f            # Force deployment even if errors detected
--verbose, -v          # Show detailed build information
```

### Usage Examples
```bash
# Basic deployment (auto-detects everything)
dprod deploy

# Custom project name
dprod deploy --name my-awesome-app
dprod deploy -n my-awesome-app

# With environment variables
ddprod deploy --env .env.production

# Detached mode (no log streaming)
dprod deploy --detach

# Force deployment despite warnings
dprod deploy --force
```

### Implementation Details

#### File: `src/commands/deploy.js`
```javascript
const { Command } = require('commander');
const { deployHandler } = require('../lib/deploy-handler');
const { validateProject } = require('../lib/validator');

async function deployAction(projectName, options) {
  try {
    // 1. Validate current directory is a project
    await validateProject(process.cwd());
    
    // 2. Execute deployment
    const result = await deployHandler({
      projectPath: process.cwd(),
      projectName: projectName || options.name,
      envFile: options.env,
      detach: options.detach,
      force: options.force,
      verbose: options.verbose
    });
    
    // 3. Output results
    if (result.success) {
      console.log(`✅ ${result.message}`);
      console.log(`🔗 ${result.url}`);
      console.log(`📊 ${result.dashboardUrl}`);
    } else {
      console.error(`❌ ${result.message}`);
      process.exit(1);
    }
    
  } catch (error) {
    console.error(`💥 Deployment failed: ${error.message}`);
    process.exit(1);
  }
}

const deployCommand = new Command('deploy')
  .description('Deploy current directory to DeployZero')
  .argument('[project-name]', 'Name for your project')
  .option('-n, --name <name>', 'Project name')
  .option('-e, --env <file>', 'Environment file to include')
  .option('-d, --detach', 'Don\'t stream logs, return immediately')
  .option('-f, --force', 'Force deployment despite warnings')
  .option('-v, --verbose', 'Show detailed build information')
  .action(deployAction);

module.exports = deployCommand;
```

#### File: `src/lib/deploy-handler.js`
```javascript
const fs = require('fs').promises;
const path = require('path');
const auth = require('./auth');
const api = require('./api');
const detector = require('./detector');
const packager = require('./packager');
const logger = require('./logger');
const { Spinner } = require('./ui');

class DeployHandler {
  async deploy(options) {
    const {
      projectPath,
      projectName = path.basename(projectPath),
      envFile,
      detach = false,
      force = false,
      verbose = false
    } = options;

    const spinner = new Spinner('Preparing deployment...');
    
    try {
      // 1. Authentication check
      spinner.setText('Checking authentication...');
      const apiKey = await auth.getApiKey();
      if (!apiKey) {
        throw new Error('Not authenticated. Run "deployzero login" first.');
      }

      // 2. Project detection
      spinner.setText('Analyzing project...');
      const projectConfig = await detector.detectProject(projectPath);
      
      if (projectConfig.warnings.length > 0 && !force) {
        spinner.stop();
        console.log('⚠️  Project analysis warnings:');
        projectConfig.warnings.forEach(warning => console.log(`   - ${warning}`));
        console.log('\nUse --force to deploy anyway.');
        return { success: false, message: 'Project validation failed' };
      }

      // 3. Package project
      spinner.setText('Packaging project...');
      const packageStream = await packager.createPackage(projectPath, {
        includeNodeModules: false,
        excludePatterns: ['.git', 'node_modules', '.env']
      });

      // 4. Find or create project
      spinner.setText('Setting up project...');
      let project = await api.findProject(projectName);
      if (!project) {
        project = await api.createProject({
          name: projectName,
          type: projectConfig.type
        });
      }

      // 5. Start deployment
      spinner.setText('Starting deployment...');
      const deployment = await api.createDeployment(project.id, packageStream, {
        config: projectConfig,
        envFile: envFile ? await fs.readFile(envFile, 'utf8') : undefined
      });

      spinner.succeed('Deployment started!');

      // 6. Stream logs if not detached
      if (!detach) {
        console.log('\n📦 Build logs:');
        await this.streamDeploymentLogs(deployment.id, verbose);
      }

      return {
        success: true,
        message: 'Deployment completed successfully',
        url: deployment.url,
        dashboardUrl: deployment.dashboardUrl
      };

    } catch (error) {
      spinner.fail('Deployment failed');
      throw error;
    }
  }

  async streamDeploymentLogs(deploymentId, verbose = false) {
    return new Promise((resolve, reject) => {
      const logStream = api.streamDeploymentLogs(deploymentId);
      
      logStream.on('data', (data) => {
        const logEntry = JSON.parse(data);
        
        // Filter verbose logs unless verbose flag is set
        if (!verbose && logEntry.level === 'debug') {
          return;
        }

        const prefix = this.getLogPrefix(logEntry.level);
        const message = this.formatLogMessage(logEntry);
        
        console.log(`${prefix} ${message}`);
      });

      logStream.on('end', () => {
        console.log(''); // Empty line after logs
        resolve();
      });

      logStream.on('error', (error) => {
        reject(error);
      });
    });
  }

  getLogPrefix(level) {
    const prefixes = {
      info: 'ℹ️ ',
      warning: '⚠️ ',
      error: '❌',
      success: '✅',
      debug: '🔍'
    };
    return prefixes[level] || '📝';
  }

  formatLogMessage(logEntry) {
    const timestamp = new Date(logEntry.timestamp).toLocaleTimeString();
    return `[${timestamp}] ${logEntry.message}`;
  }
}

module.exports = new DeployHandler();
```

## 🔐 Authentication Command: `deployzero login`

### Command Structure
```bash
deployzero login [options]
```

### Options
```bash
--token <token>    # Directly provide API token
--email <email>    # Email for login
```

### Implementation

#### File: `src/commands/login.js`
```javascript
const { Command } = require('commander');
const auth = require('../lib/auth');
const { openBrowser } = require('../lib/utils/browser');

async function loginAction(options) {
  try {
    if (options.token) {
      // Direct token authentication
      await auth.loginWithToken(options.token);
      console.log('✅ Logged in successfully with token!');
      return;
    }

    if (options.email) {
      // Email-based authentication flow
      console.log('📧 Starting email authentication...');
      const result = await auth.loginWithEmail(options.email);
      
      if (result.verificationRequired) {
        console.log('📨 Check your email for verification link');
      } else {
        console.log('✅ Logged in successfully!');
      }
      return;
    }

    // Interactive browser-based login (default)
    console.log('🔗 Opening browser for authentication...');
    const loginUrl = await auth.getLoginUrl();
    
    await openBrowser(loginUrl);
    console.log('💻 Please complete authentication in your browser...');
    
    // Poll for authentication completion
    const user = await auth.waitForAuthentication();
    console.log(`✅ Logged in as ${user.email}!`);

  } catch (error) {
    console.error(`❌ Login failed: ${error.message}`);
    process.exit(1);
  }
}

const loginCommand = new Command('login')
  .description('Authenticate with DeployZero')
  .option('-t, --token <token>', 'Authenticate with API token')
  .option('-e, --email <email>', 'Login with email')
  .action(loginAction);

module.exports = loginCommand;
```

## 📊 Status Command: `deployzero status`

### Command Structure
```bash
deployzero status [project-name]
```

### Implementation

#### File: `src/commands/status.js`
```javascript
const { Command } = require('commander');
const api = require('../lib/api');
const auth = require('../lib/auth');
const { Table } = require('../lib/ui');

async function statusAction(projectName) {
  try {
    const apiKey = await auth.getApiKey();
    if (!apiKey) {
      throw new Error('Not authenticated. Run "deployzero login" first.');
    }

    if (projectName) {
      // Single project status
      await showProjectStatus(projectName);
    } else {
      // List all projects
      await listProjects();
    }

  } catch (error) {
    console.error(`❌ Failed to get status: ${error.message}`);
    process.exit(1);
  }
}

async function showProjectStatus(projectName) {
  const project = await api.getProject(projectName);
  const deployments = await api.getProjectDeployments(project.id, { limit: 5 });

  console.log(`\n📊 Project: ${project.name}`);
  console.log(`🔗 URL: ${project.url}`);
  console.log(`📅 Created: ${new Date(project.createdAt).toLocaleDateString()}`);
  console.log(`🔄 Status: ${getStatusEmoji(project.status)} ${project.status}`);

  if (deployments.length > 0) {
    console.log('\n📦 Recent Deployments:');
    
    const table = new Table({
      head: ['Date', 'Status', 'URL', 'Duration']
    });

    deployments.forEach(deployment => {
      table.push([
        new Date(deployment.createdAt).toLocaleDateString(),
        `${getStatusEmoji(deployment.status)} ${deployment.status}`,
        deployment.url || 'N/A',
        deployment.duration ? `${deployment.duration}s` : 'N/A'
      ]);
    });

    console.log(table.toString());
  }
}

async function listProjects() {
  const projects = await api.getProjects();

  if (projects.length === 0) {
    console.log('No projects found. Run "deployzero deploy" to create one!');
    return;
  }

  console.log('\n📁 Your Projects:');
  
  const table = new Table({
    head: ['Name', 'Status', 'URL', 'Last Deployed']
  });

  projects.forEach(project => {
    table.push([
      project.name,
      `${getStatusEmoji(project.status)} ${project.status}`,
      project.url,
      project.lastDeployed ? new Date(project.lastDeployed).toLocaleDateString() : 'Never'
    ]);
  });

  console.log(table.toString());
}

function getStatusEmoji(status) {
  const emojis = {
    live: '✅',
    deploying: '🔄',
    error: '❌',
    stopped: '⏸️',
    building: '🔨'
  };
  return emojis[status] || '❓';
}

const statusCommand = new Command('status')
  .description('Check project status and deployments')
  .argument('[project-name]', 'Project name to check')
  .action(statusAction);

module.exports = statusCommand;
```

## 📝 Logs Command: `deployzero logs`

### Command Structure
```bash
deployzero logs [project-name] [options]
```

### Options
```bash
--deployment <id>    # Specific deployment ID
--follow, -f         # Follow logs in real-time
--tail <number>      # Show last N lines (default: 100)
```

### Implementation

#### File: `src/commands/logs.js`
```javascript
const { Command } = require('commander');
const api = require('../lib/api');
const auth = require('../lib/auth');

async function logsAction(projectName, options) {
  try {
    const apiKey = await auth.getApiKey();
    if (!apiKey) {
      throw new Error('Not authenticated. Run "deployzero login" first.');
    }

    if (!projectName) {
      // Get project name from current directory or error
      projectName = await getCurrentProjectName();
    }

    const logs = await api.getDeploymentLogs(projectName, {
      deploymentId: options.deployment,
      tail: options.tail,
      follow: options.follow
    });

    if (options.follow) {
      console.log(`📝 Streaming logs for ${projectName}...\n`);
      await streamLogs(logs);
    } else {
      console.log(`📝 Logs for ${projectName}:\n`);
      displayLogs(logs);
    }

  } catch (error) {
    console.error(`❌ Failed to get logs: ${error.message}`);
    process.exit(1);
  }
}

async function streamLogs(logStream) {
  return new Promise((resolve, reject) => {
    logStream.on('data', (data) => {
      const logEntry = JSON.parse(data);
      const prefix = getLogPrefix(logEntry.level);
      console.log(`${prefix} ${logEntry.message}`);
    });

    logStream.on('end', resolve);
    logStream.on('error', reject);
  });
}

function displayLogs(logs) {
  logs.forEach(logEntry => {
    const prefix = getLogPrefix(logEntry.level);
    const timestamp = new Date(logEntry.timestamp).toLocaleTimeString();
    console.log(`[${timestamp}] ${prefix} ${logEntry.message}`);
  });
}

function getLogPrefix(level) {
  const prefixes = {
    info: 'ℹ️',
    warning: '⚠️',
    error: '❌',
    success: '✅'
  };
  return prefixes[level] || '📝';
}

async function getCurrentProjectName() {
  // Try to detect project name from current directory
  // or from local config file
  throw new Error('Project name required or run from project directory');
}

const logsCommand = new Command('logs')
  .description('View deployment logs')
  .argument('[project-name]', 'Project name')
  .option('-d, --deployment <id>', 'Specific deployment ID')
  .option('-f, --follow', 'Follow logs in real-time')
  .option('-t, --tail <number>', 'Number of lines to show', '100')
  .action(logsAction);

module.exports = logsCommand;
```

## 🏃‍♂️ Main CLI Entry Point

#### File: `src/index.js`
```javascript
#!/usr/bin/env node

const { Command } = require('commander');
const { version } = require('../package.json');

// Import commands
const deployCommand = require('./commands/deploy');
const loginCommand = require('./commands/login');
const logoutCommand = require('./commands/logout');
const statusCommand = require('./commands/status');
const logsCommand = require('./commands/logs');
const listCommand = require('./commands/list');

const program = new Command();

program
  .name('deployzero')
  .description('Zero-config deployment platform - deploy any project with one command')
  .version(version, '-v, --version', 'Output the current version')
  .addCommand(deployCommand)
  .addCommand(loginCommand)
  .addCommand(logoutCommand)
  .addCommand(statusCommand)
  .addCommand(logsCommand)
  .addCommand(listCommand);

// Global error handler
program.configureOutput({
  outputError: (str, write) => {
    write(`❌ ${str}`);
  }
});

// Global options
program
  .option('--api-url <url>', 'Custom API URL', process.env.DEPLOYZERO_API_URL || 'https://api.deployzero.com')
  .option('--debug', 'Enable debug mode');

// Parse arguments
program.parse();

// Handle unknown commands
program.on('command:*', function () {
  console.error(`Invalid command: ${program.args.join(' ')}`);
  console.error('See --help for a list of available commands.');
  process.exit(1);
});
```

#### File: `bin/deployzero`
```bash
#!/usr/bin/env node

require('../src/index.js');
```

---

# Supporting Libraries

## 🔐 Authentication Manager

#### File: `src/lib/auth.js`
```javascript
const fs = require('fs').promises;
const path = require('path');
const os = require('os');
const api = require('./api');

class AuthManager {
  constructor() {
    this.configDir = path.join(os.homedir(), '.deployzero');
    this.configFile = path.join(this.configDir, 'config.json');
  }

  async getApiKey() {
    try {
      const config = await this.loadConfig();
      return config.apiKey;
    } catch (error) {
      return null;
    }
  }

  async loginWithToken(token) {
    // Validate token with API
    const user = await api.validateToken(token);
    
    // Save to config
    await this.saveConfig({ apiKey: token, user });
    return user;
  }

  async getLoginUrl() {
    const { url, token } = await api.initiateLogin();
    
    // Store temporary token for polling
    await this.saveTempToken(token);
    return url;
  }

  async waitForAuthentication(timeout = 300000) { // 5 minutes
    const startTime = Date.now();
    const tempToken = await this.getTempToken();

    while (Date.now() - startTime < timeout) {
      try {
        const result = await api.checkLoginStatus(tempToken);
        
        if (result.authenticated) {
          await this.saveConfig({ 
            apiKey: result.apiKey, 
            user: result.user 
          });
          await this.clearTempToken();
          return result.user;
        }
      } catch (error) {
        // Continue polling on error
      }

      await new Promise(resolve => setTimeout(resolve, 2000)); // Wait 2 seconds
    }

    throw new Error('Authentication timeout');
  }

  async loadConfig() {
    const data = await fs.readFile(this.configFile, 'utf8');
    return JSON.parse(data);
  }

  async saveConfig(config) {
    await fs.mkdir(this.configDir, { recursive: true });
    await fs.writeFile(this.configFile, JSON.stringify(config, null, 2));
  }

  async getTempToken() {
    const tempFile = path.join(this.configDir, 'temp_token');
    const data = await fs.readFile(tempFile, 'utf8');
    return data.trim();
  }

  async saveTempToken(token) {
    const tempFile = path.join(this.configDir, 'temp_token');
    await fs.mkdir(this.configDir, { recursive: true });
    await fs.writeFile(tempFile, token);
  }

  async clearTempToken() {
    const tempFile = path.join(this.configDir, 'temp_token');
    try {
      await fs.unlink(tempFile);
    } catch (error) {
      // Ignore if file doesn't exist
    }
  }
}

module.exports = new AuthManager();
```

## 🌐 API Client

#### File: `src/lib/api.js`
```javascript
const axios = require('axios');
const FormData = require('form-data');
const auth = require('./auth');
const config = require('./config');

class APIClient {
  constructor() {
    this.baseURL = config.get('apiUrl');
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000
    });

    // Add auth interceptor
    this.client.interceptors.request.use(async (config) => {
      const apiKey = await auth.getApiKey();
      if (apiKey) {
        config.headers['Authorization'] = `Bearer ${apiKey}`;
      }
      return config;
    });
  }

  async createDeployment(projectId, fileStream, options = {}) {
    const formData = new FormData();
    
    formData.append('file', fileStream, {
      filename: 'source.tar.gz',
      contentType: 'application/gzip'
    });
    
    formData.append('config', JSON.stringify(options.config));
    
    if (options.envFile) {
      formData.append('env', options.envFile);
    }

    const response = await this.client.post(
      `/projects/${projectId}/deployments`,
      formData,
      {
        headers: formData.getHeaders(),
        timeout: 120000 // 2 minutes for upload
      }
    );

    return response.data;
  }

  async streamDeploymentLogs(deploymentId) {
    const apiKey = await auth.getApiKey();
    const url = `${this.baseURL}/deployments/${deploymentId}/logs/stream`;
    
    // Use WebSocket or Server-Sent Events based on API support
    return this.createEventSource(url, apiKey);
  }

  async findProject(name) {
    try {
      const response = await this.client.get(`/projects?name=${encodeURIComponent(name)}`);
      return response.data.projects.find(p => p.name === name);
    } catch (error) {
      if (error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async createProject(projectData) {
    const response = await this.client.post('/projects', projectData);
    return response.data;
  }

  async getProjects() {
    const response = await this.client.get('/projects');
    return response.data.projects;
  }

  async getProjectDeployments(projectId, options = {}) {
    const params = new URLSearchParams();
    if (options.limit) params.append('limit', options.limit);
    
    const response = await this.client.get(
      `/projects/${projectId}/deployments?${params}`
    );
    return response.data.deployments;
  }

  // Event Source implementation for log streaming
  createEventSource(url, apiKey) {
    // Implementation depends on whether API uses WebSocket or SSE
    // This is a simplified version
    const { EventSource } = require('eventsource');
    
    return new EventSource(url, {
      headers: {
        'Authorization': `Bearer ${apiKey}`
      }
    });
  }
}

module.exports = new APIClient();
```

---

# Package Configuration

#### File: `package.json`
```json
{
  "name": "deployzero",
  "version": "0.1.0",
  "description": "Zero-config deployment platform",
  "main": "src/index.js",
  "bin": {
    "deployzero": "./bin/deployzero"
  },
  "scripts": {
    "start": "node src/index.js",
    "dev": "node --inspect src/index.js",
    "test": "jest",
    "build": "pkg . --out-path dist/",
    "lint": "eslint src/",
    "prepublishOnly": "npm test && npm run lint"
  },
  "keywords": ["deployment", "paas", "zero-config", "docker", "cloud"],
  "author": "DeployZero Team",
  "license": "MIT",
  "dependencies": {
    "commander": "^9.4.1",
    "axios": "^1.4.0",
    "form-data": "^4.0.0",
    "tar": "^6.1.13",
    "chalk": "^4.1.2",
    "ora": "^5.4.1",
    "cli-table3": "^0.6.3",
    "open": "^8.4.0",
    "ws": "^8.13.0",
    "eventsource": "^2.0.2"
  },
  "devDependencies": {
    "jest": "^29.5.0",
    "eslint": "^8.42.0",
    "pkg": "^5.8.1"
  },
  "engines": {
    "node": ">=14.0.0"
  },
  "files": [
    "bin/",
    "src/",
    "LICENSE",
    "README.md"
  ]
}
```

---

# Installation & Distribution

## Local Development Installation
```bash
# From source
git clone https://github.com/deployzero/cli.git
cd cli
npm install -g .

# Test installation
deployzero --version
```

## Global NPM Installation
```bash
npm install -g deployzero
```

## Usage Examples
```bash
# First time setup
deployzero login
deployzero deploy

# Advanced usage
deployzero deploy --name my-app --env .env.production
deployzero status my-app
deployzero logs my-app --follow
deployzero list
```

This CLI specification provides a complete, professional-grade command-line interface that delivers on the promise of zero-configuration deployment while providing powerful features for advanced users.