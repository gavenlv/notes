// reporters/slack-reporter.js
class SlackReporter {
  constructor(options) {
    this.options = options || {};
  }

  async onEnd(result) {
    // 在测试结束时调用
    if (result.status === 'failed' && this.options.webhookUrl) {
      await this.sendSlackNotification(result);
    }
  }

  async sendSlackNotification(result) {
    // 发送失败通知到Slack
    const failedTests = result.failures ? result.failures.length : 0;
    const passedTests = result.passes ? result.passes.length : 0;
    const totalTests = failedTests + passedTests;
    
    const message = `
:test_tube: Playwright测试报告
通过: ${passedTests} :white_check_mark:
失败: ${failedTests} :x:
总执行时间: ${result.duration || 0}ms
环境: ${process.env.TEST_ENV || 'development'}
    `;
    
    try {
      // 发送到Slack webhook
      await fetch(this.options.webhookUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: message })
      });
      console.log('Slack通知已发送');
    } catch (error) {
      console.error('发送Slack通知失败:', error);
    }
  }
}

module.exports = { SlackReporter };