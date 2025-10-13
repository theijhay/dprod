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
  .description('Authenticate with Dprod')
  .option('-t, --token <token>', 'Authenticate with API token')
  .option('-e, --email <email>', 'Login with email')
  .action(loginAction);

module.exports = loginCommand;
