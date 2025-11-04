#!/usr/bin/env node

const { Command } = require('commander');
const { version } = require('../package.json');

// Import commands
const deployCommand = require('./commands/deploy');
const registerCommand = require('./commands/register');
const loginCommand = require('./commands/login');
const logoutCommand = require('./commands/logout');
const statusCommand = require('./commands/status');
const logsCommand = require('./commands/logs');
const listCommand = require('./commands/list');

const program = new Command();

program
  .name('dprod')
  .description('Zero-configuration deployment platform - deploy any project with one command')
  .version(version, '-v, --version', 'Output the current version')
  .addCommand(deployCommand)
  .addCommand(registerCommand)
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
  .option('--api-url <url>', 'Custom API URL', process.env.DPROD_API_URL || 'http://localhost:8000')
  .option('--debug', 'Enable debug mode');

// Parse arguments
program.parse();

// Handle unknown commands
program.on('command:*', function () {
  console.error(`Invalid command: ${program.args.join(' ')}`);
  console.error('See --help for a list of available commands.');
  process.exit(1);
});
