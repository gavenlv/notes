// fixtures/database-fixture.js
class DatabaseFixture {
  constructor() {
    this.connection = null;
  }

  async connect() {
    if (!this.connection) {
      // 模拟建立数据库连接
      console.log('建立数据库连接...');
      this.connection = { connected: true };
    }
    return this.connection;
  }

  async disconnect() {
    if (this.connection) {
      // 模拟关闭数据库连接
      console.log('关闭数据库连接...');
      this.connection = null;
    }
  }
}

module.exports = { DatabaseFixture };