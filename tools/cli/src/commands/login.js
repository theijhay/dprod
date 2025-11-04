const { Command } = require('commander');
const inquirer = require('inquirer');
const auth = require('../lib/auth');
const logger = require('../lib/logger');

async function loginAction(options) {
  try {
    if (options.token) {
      // Direct token authentication (API key)
      logger.info('Authenticating with token...');
      await auth.loginWithToken(options.token);
      logger.success('✅ Logged in successfully with token!');
      return;
    }

    // Interactive email/password login
    logger.info('📧 Login to Dprod');
    
    const credentials = await inquirer.prompt([
      {
        type: 'input',
        name: 'email',
        message: 'Email address:',
        validate: email => /.+@.+\..+/.test(email) || 'Please enter a valid email'
      },
      {
        type: 'password',
        name: 'password',
        message: 'Password:',
        mask: '*',
        validate: password => password.length >= 8 || 'Password must be at least 8 characters'
      }
    ]);

    logger.info('Logging in...');
    const result = await auth.loginWithPassword(credentials.email, credentials.password);
    
    logger.success(`✅ Logged in as ${result.user.email}!`);
    logger.info(`🔑 Your API key: ${result.token.api_key}`);
    logger.info('💡 You can also login with: dprod login --token <your-api-key>');

  } catch (error) {
    logger.error(`❌ Login failed: ${error.message}`);
    process.exit(1);
  }
}

const loginCommand = new Command('login')
  .description('Authenticate with Dprod')
  .option('-t, --token <token>', 'Authenticate with API token/key')
  .action(loginAction);

module.exports = loginCommand;
