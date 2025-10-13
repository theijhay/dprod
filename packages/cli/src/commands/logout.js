const { Command } = require('commander');
const auth = require('../lib/auth');

async function logoutAction() {
  try {
    await auth.logout();
    console.log('✅ Logged out successfully!');
  } catch (error) {
    console.error(`❌ Logout failed: ${error.message}`);
    process.exit(1);
  }
}

const logoutCommand = new Command('logout')
  .description('Logout from Dprod')
  .action(logoutAction);

module.exports = logoutCommand;
