// data/test-data-provider.js
const fs = require('fs');
const path = require('path');

class TestDataProvider {
  static loadFromJSON(filename) {
    const filePath = path.join(__dirname, filename);
    const data = JSON.parse(fs.readFileSync(filePath, 'utf8'));
    return data;
  }

  static loadFromCSV(filename) {
    // 实现CSV解析逻辑
    const filePath = path.join(__dirname, filename);
    // 返回解析后的数据
    return [];
  }
}

module.exports = { TestDataProvider };