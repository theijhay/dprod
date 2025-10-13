const { Command } = require('commander');
const api = require('../lib/api');
const auth = require('../lib/auth');
const { Table } = require('../lib/ui');

async function statusAction(projectName) {
  try {
    const apiKey = await auth.getApiKey();
    if (!apiKey) {
      throw new Error('Not authenticated. Run "dprod login" first.');
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
    console.log('No projects found. Run "dprod deploy" to create one!');
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
