const { Command } = require('commander');
const api = require('../lib/api');
const auth = require('../lib/auth');
const { Table } = require('../lib/ui');

async function listAction() {
  try {
    const apiKey = await auth.getApiKey();
    if (!apiKey) {
      throw new Error('Not authenticated. Run "dprod login" first.');
    }

    const projects = await api.getProjects();

    if (projects.length === 0) {
      console.log('No projects found. Run "dprod deploy" to create one!');
      return;
    }

    console.log('\n📁 Your Projects:');
    
    const table = new Table({
      head: ['Name', 'Type', 'Status', 'URL', 'Last Deployed']
    });

    projects.forEach(project => {
      table.push([
        project.name,
        project.type || 'unknown',
        `${getStatusEmoji(project.status)} ${project.status}`,
        project.url || 'N/A',
        project.lastDeployed ? new Date(project.lastDeployed).toLocaleDateString() : 'Never'
      ]);
    });

    console.log(table.toString());

  } catch (error) {
    console.error(`❌ Failed to list projects: ${error.message}`);
    process.exit(1);
  }
}

function getStatusEmoji(status) {
  const emojis = {
    live: '✅',
    deploying: '🔄',
    error: '❌',
    stopped: '⏸️',
    building: '🔨',
    active: '✅'
  };
  return emojis[status] || '❓';
}

const listCommand = new Command('list')
  .description('List all your projects')
  .action(listAction);

module.exports = listCommand;
