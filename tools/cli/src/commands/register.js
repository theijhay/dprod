const { Command } = require('commander');
const inquirer = require('inquirer');
const auth = require('../lib/auth');
const logger = require('../lib/logger');

async function registerAction() {
  try {
    logger.info('📝 Register for Dprod');
    
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
        message: 'Password (min 8 chars, uppercase, lowercase, digit):',
        mask: '*',
        validate: password => {
          if (password.length < 8) return 'Password must be at least 8 characters';
          if (!/[A-Z]/.test(password)) return 'Password must contain uppercase letter';
          if (!/[a-z]/.test(password)) return 'Password must contain lowercase letter';
          if (!/[0-9]/.test(password)) return 'Password must contain a digit';
          return true;
        }
      },
      {
        type: 'password',
        name: 'confirmPassword',
        message: 'Confirm password:',
        mask: '*',
        validate: (value, answers) => value === answers.password || 'Passwords do not match'
      }
    ]);

    logger.info('Creating your account...');
    const result = await auth.register(credentials.email, credentials.password);
    
    logger.success(`✅ Account created successfully!`);
    logger.success(`📧 Logged in as ${result.user.email}`);
    logger.info('');
    logger.info('🔑 Your API key (save this securely):');
    logger.info(`   ${result.token.api_key}`);
    logger.info('');
    logger.info('💡 Usage:');
    logger.info('   - Keep this API key secure');
    logger.info('   - Use it to login: dprod login --token <your-api-key>');
    logger.info('   - Or login with email/password: dprod login');
    logger.info('');

  } catch (error) {
    logger.error(`❌ Registration failed: ${error.message}`);
    if (error.response?.data?.detail) {
      logger.error(`   ${error.response.data.detail}`);
    }
    process.exit(1);
  }
}

const registerCommand = new Command('register')
  .description('Create a new Dprod account')
  .action(registerAction);

module.exports = registerCommand;
