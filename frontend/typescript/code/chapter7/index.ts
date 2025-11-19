// 第7章：TypeScript模块系统与命名空间 - 主入口文件

// 导入ES6模块示例
import { ES6Module } from './es6-modules';
import { ModuleA, ModuleB } from './module-imports';
import { Geometry } from './namespaces';

// 动态导入示例
async function demonstrateDynamicImports() {
    console.log("=== 动态导入示例 ===");
    
    // 动态导入模块
    const module = await import('./dynamic-imports');
    
    // 使用动态导入的函数
    console.log(module.default(10, 5)); // 输出: 15
    console.log(module.multiply(4, 7)); // 输出: 28
}

// 命名空间示例
function demonstrateNamespaces() {
    console.log("=== 命名空间示例 ===");
    
    // 使用嵌套命名空间
    const circle = new Geometry.Shapes.Circle(5);
    console.log(`Circle area: ${circle.area()}`); // 输出: Circle area: 78.53981633974483
    
    // 使用命名空间别名
    const rect = new Geometry.TwoD.Rect(10, 20);
    console.log(`Rectangle area: ${rect.area()}`); // 输出: Rectangle area: 200
}

// ES6模块示例
function demonstrateES6Modules() {
    console.log("=== ES6模块示例 ===");
    
    const module = new ES6Module();
    module.publicMethod(); // 访问公共方法
    console.log(module.publicProperty); // 访问公共属性
    
    // 尝试访问私有属性会导致编译错误
    // module.privateMethod(); // 错误: 属性'privateMethod'是私有的，只能在类'ES6Module'内部访问
}

// 模块导入示例
function demonstrateModuleImports() {
    console.log("=== 模块导入示例 ===");
    
    const moduleA = new ModuleA();
    moduleA.methodA();
    
    const moduleB = new ModuleB();
    moduleB.methodB();
}

// 运行所有示例
async function runExamples() {
    demonstrateES6Modules();
    console.log('---');
    demonstrateModuleImports();
    console.log('---');
    demonstrateNamespaces();
    console.log('---');
    await demonstrateDynamicImports();
    console.log('---');
}

runExamples().catch(console.error);