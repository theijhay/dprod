const { Command } = require('commander');
const api = require('../lib/api');
const auth = require('../lib/auth');

async function logsAction(projectName, options) {
  try {
    const apiKey = await auth.getApiKey();
    if (!apiKey) {
      throw new Error('Not authenticated. Run "dprod login" first.');
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
  // Try to detect project name from current directory or from local config file
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
