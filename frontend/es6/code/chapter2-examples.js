// 第2章：变量声明与作用域示例

// 1. let与var的区别
function testVarVsLet() {
  console.log('=== let与var的区别 ===');
  
  // 使用var的循环
  console.log('使用var的循环:');
  for (var i = 0; i < 3; i++) {
    setTimeout(() => console.log(`var: ${i}`), 100);
  }
  
  // 使用let的循环
  console.log('使用let的循环:');
  for (let j = 0; j < 3; j++) {
    setTimeout(() => console.log(`let: ${j}`), 200);
  }
}

// 2. const与对象操作
function testConstWithObjects() {
  console.log('\n=== const与对象操作 ===');
  
  const person = {
    name: 'Alice',
    age: 30
  };
  
  console.log('原始对象:', person);
  
  // 修改对象属性 - 允许
  person.age = 31;
  console.log('修改年龄后:', person);
  
  // 添加新属性 - 允许
  person.email = 'alice@example.com';
  console.log('添加邮箱后:', person);
  
  // 尝试重新赋值整个对象 - 不允许
  try {
    person = { name: 'Bob', age: 25 };
  } catch (error) {
    console.log('重新赋值错误:', error.message);
  }
}

// 3. 块级作用域与TDZ
function testScopeAndTDZ() {
  console.log('\n=== 块级作用域与TDZ ===');
  
  let outer = 'outer';
  console.log('外层变量:', outer);
  
  {
    console.log('块内访问外层变量:', outer);
    
    let inner = 'inner';
    console.log('块内变量:', inner);
    
    {
      console.log('嵌套块内访问外层变量:', outer);
      console.log('嵌套块内访问块内变量:', inner);
      
      let deepest = 'deepest';
      console.log('最深层变量:', deepest);
    }
    
    // 尝试访问deepest - 不允许
    try {
      console.log(deepest);
    } catch (error) {
      console.log('访问deepest错误:', error.message);
    }
  }
  
  // 尝试访问inner - 不允许
  try {
    console.log(inner);
  } catch (error) {
    console.log('访问inner错误:', error.message);
  }
}

// 4. 暂时性死区
function testTDZ() {
  console.log('\n=== 暂时性死区 ===');
  
  // 1. 基本TDZ
  try {
    console.log(x);
    let x = 10;
  } catch (error) {
    console.log('基本TDZ错误:', error.message);
  }
  
  // 2. 函数参数中的TDZ
  try {
    // 以下代码会导致错误，所以我们用try-catch包装
    eval(`
      function testParams(x = y, y = 10) {
        return x + y;
      }
      testParams();
    `);
  } catch (error) {
    console.log('函数参数TDZ错误:', error.message);
  }
  
  // 3. 正确的参数默认值
  function correctParams(x = 10, y = x) {
    return x + y;
  }
  console.log('正确的参数默认值结果:', correctParams());
  
  // 4. typeof与TDZ
  try {
    console.log(typeof notDeclared); // "undefined"
    
    {
      // 以下代码会导致错误
      // console.log(typeof myLet); // ReferenceError
      // let myLet = 10;
      
      // 我们用try-catch来演示
      try {
        eval(`
          let myLet = 10;
        `);
      } catch (e) {
        console.log('typeof与TDZ错误:', e.message);
      }
    }
  } catch (error) {
    console.log('typeof测试错误:', error.message);
  }
}

// 5. 变量提升对比
function testHoisting() {
  console.log('\n=== 变量提升对比 ===');
  
  // var的变量提升
  console.log('var的变量提升:');
  function testVarHoisting() {
    console.log(x); // undefined
    var x = 10;
    console.log(x); // 10
  }
  testVarHoisting();
  
  // let/const的TDZ
  console.log('let/const的TDZ:');
  try {
    function testLetTDZ() {
      console.log(y); // ReferenceError
      let y = 10;
      console.log(y);
    }
    testLetTDZ();
  } catch (error) {
    console.log('let TDZ错误:', error.message);
  }
  
  // 函数声明提升
  console.log('函数声明提升:');
  testHoistedFunction(); // 可以正常调用
  
  function testHoistedFunction() {
    console.log('函数声明被提升了');
  }
  
  // 函数表达式不提升
  console.log('函数表达式不提升:');
  try {
    testExpression(); // TypeError
    var testExpression = function() {
      console.log('函数表达式');
    };
  } catch (error) {
    console.log('函数表达式错误:', error.message);
  }
}

// 6. 全局变量与全局对象
function testGlobalVariables() {
  console.log('\n=== 全局变量与全局对象 ===');
  
  // 使用var声明全局变量
  var globalVar = 'I am global with var';
  console.log('window.globalVar:', window.globalVar);
  
  // 使用let声明全局变量
  let globalLet = 'I am global with let';
  console.log('window.globalLet:', window.globalLet);
  
  // 使用const声明全局变量
  const globalConst = 'I am global with const';
  console.log('window.globalConst:', window.globalConst);
}

// 7. 重复声明测试
function testRedeclaration() {
  console.log('\n=== 重复声明测试 ===');
  
  // var允许重复声明
  var redeclaredVar = 'first';
  var redeclaredVar = 'second';
  console.log('var重复声明:', redeclaredVar);
  
  // let/const不允许重复声明
  try {
    let redeclaredLet = 'first';
    let redeclaredLet = 'second';
  } catch (error) {
    console.log('let重复声明错误:', error.message);
  }
  
  try {
    const redeclaredConst = 'first';
    const redeclaredConst = 'second';
  } catch (error) {
    console.log('const重复声明错误:', error.message);
  }
  
  // 不同作用域中的同名变量
  let sameName = 'outer';
  console.log('外层sameName:', sameName);
  
  {
    let sameName = 'inner';
    console.log('内层sameName:', sameName);
  }
  
  console.log('外层sameName:', sameName);
}

// 8. 对象冻结与不可变性
function testImmutability() {
  console.log('\n=== 对象冻结与不可变性 ===');
  
  // 普通const对象
  const normalObject = { name: 'Alice', age: 30 };
  normalObject.age = 31;
  console.log('修改const对象属性:', normalObject);
  
  // 冻结对象
  const frozenObject = Object.freeze({ name: 'Bob', age: 25 });
  
  // 尝试修改冻结对象
  try {
    frozenObject.age = 26;
    console.log('修改冻结对象属性:', frozenObject);
  } catch (error) {
    console.log('修改冻结对象错误:', error.message);
  }
  
  // 深度冻结
  function deepFreeze(obj) {
    Object.getOwnPropertyNames(obj).forEach(prop => {
      if (obj[prop] !== null && typeof obj[prop] === 'object') {
        deepFreeze(obj[prop]);
      }
    });
    return Object.freeze(obj);
  }
  
  const nestedObject = {
    user: { name: 'Charlie', age: 35 },
    settings: { theme: 'dark' }
  };
  
  const deeplyFrozenObject = deepFreeze(nestedObject);
  
  try {
    deeplyFrozenObject.user.age = 36;
    console.log('修改深度冻结对象:', deeplyFrozenObject);
  } catch (error) {
    console.log('修改深度冻结对象错误:', error.message);
  }
}

// 运行所有测试
function runAllTests() {
  testVarVsLet();
  
  setTimeout(() => {
    testConstWithObjects();
    testScopeAndTDZ();
    testTDZ();
    testHoisting();
    testGlobalVariables();
    testRedeclaration();
    testImmutability();
  }, 300);
}

// 导出函数以便在其他模块中使用
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    testVarVsLet,
    testConstWithObjects,
    testScopeAndTDZ,
    testTDZ,
    testHoisting,
    testGlobalVariables,
    testRedeclaration,
    testImmutability,
    runAllTests
  };
}

// 如果直接运行此文件，执行所有测试
if (typeof window === 'undefined') {
  runAllTests();
}