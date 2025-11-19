// 基础项目入口文件
// 演示基本的JavaScript代码和依赖使用

// 引入第三方依赖
const _ = require('lodash');
const moment = require('moment');

// 定义一些示例数据
const users = [
  { id: 1, name: '张三', age: 25, joinDate: '2020-01-15' },
  { id: 2, name: '李四', age: 30, joinDate: '2019-05-20' },
  { id: 3, name: '王五', age: 28, joinDate: '2021-03-10' }
];

// 项目主函数
function main() {
  console.log('=== Yarn基础项目示例 ===');
  
  // 使用lodash处理数据
  const userNames = _.map(users, 'name');
  console.log('用户列表:', userNames.join(', '));
  
  // 计算平均年龄
  const totalAge = _.sumBy(users, 'age');
  const averageAge = (totalAge / users.length).toFixed(1);
  console.log(`平均年龄: ${averageAge}岁`);
  
  // 使用moment处理日期
  const now = moment();
  const formattedDate = now.format('YYYY-MM-DD HH:mm:ss');
  console.log(`当前时间: ${formattedDate}`);
  
  // 计算用户加入公司的时长
  users.forEach(user => {
    const joinDate = moment(user.joinDate);
    const duration = moment.duration(now.diff(joinDate));
    const years = Math.floor(duration.asYears());
    const months = Math.floor(duration.asMonths() % 12);
    
    console.log(`${user.name} 已加入公司 ${years}年${months}个月`);
  });
  
  console.log('\n=== 依赖版本信息 ===');
  console.log(`Lodash版本: ${_.VERSION}`);
  console.log(`Moment版本: ${moment.version}`);
}

// 如果直接运行此文件，则执行主函数
if (require.main === module) {
  main();
}

// 导出函数供其他模块使用
module.exports = {
  users,
  main
};