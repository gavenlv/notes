// helpers/performance-monitor.js
class PerformanceMonitor {
  constructor() {
    this.metrics = {};
  }

  start(name) {
    this.metrics[name] = {
      startTime: Date.now(),
      endTime: null,
      duration: null
    };
  }

  end(name) {
    if (this.metrics[name]) {
      this.metrics[name].endTime = Date.now();
      this.metrics[name].duration = 
        this.metrics[name].endTime - this.metrics[name].startTime;
    }
  }

  getDuration(name) {
    return this.metrics[name]?.duration || 0;
  }

  report() {
    console.log('性能报告:');
    for (const [name, metric] of Object.entries(this.metrics)) {
      console.log(`${name}: ${metric.duration}ms`);
    }
  }
}

module.exports = { PerformanceMonitor };