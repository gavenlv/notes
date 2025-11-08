// helpers/metrics-collector.js
class MetricsCollector {
  constructor() {
    this.metrics = {
      totalTests: 0,
      passedTests: 0,
      failedTests: 0,
      skippedTests: 0,
      duration: 0
    };
  }

  recordTestResult(status) {
    this.metrics.totalTests++;
    switch (status) {
      case 'passed':
        this.metrics.passedTests++;
        break;
      case 'failed':
        this.metrics.failedTests++;
        break;
      case 'skipped':
        this.metrics.skippedTests++;
        break;
    }
  }

  recordDuration(duration) {
    this.metrics.duration += duration;
  }

  getMetrics() {
    return {
      ...this.metrics,
      passRate: this.metrics.totalTests > 0 ? 
        (this.metrics.passedTests / this.metrics.totalTests * 100).toFixed(2) + '%' : '0%'
    };
  }

  async sendToMonitoringSystem(metrics) {
    // 发送到Prometheus、Datadog等监控系统
    console.log('发送指标到监控系统:', JSON.stringify(metrics, null, 2));
    
    // 模拟发送到外部系统
    // 在实际应用中，这里会是真实的API调用
    return new Promise(resolve => {
      setTimeout(() => {
        console.log('指标已发送到监控系统');
        resolve();
      }, 100);
    });
  }
}

module.exports = { MetricsCollector };