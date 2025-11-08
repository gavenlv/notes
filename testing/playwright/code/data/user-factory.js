// data/user-factory.js
class UserFactory {
  static createValidUser() {
    return {
      username: `user_${Date.now()}`,
      email: `user_${Date.now()}@example.com`,
      password: 'Password123!'
    };
  }

  static createInvalidUser() {
    return {
      username: '',
      email: 'invalid-email',
      password: '123'
    };
  }
}

module.exports = { UserFactory };