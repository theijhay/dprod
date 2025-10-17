const { Command } = require('commander');
const path = require('path');
const fs = require('fs-extra');
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
  .description('Deploy current directory to Dprod')
  .argument('[project-name]', 'Name for your project')
  .option('-n, --name <name>', 'Project name')
  .option('-e, --env <file>', 'Environment file to include')
  .option('-d, --detach', 'Don\'t stream logs, return immediately')
  .option('-f, --force', 'Force deployment despite warnings')
  .option('-v, --verbose', 'Show detailed build information')
  .action(deployAction);

module.exports = deployCommand;
