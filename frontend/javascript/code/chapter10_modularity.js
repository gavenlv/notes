// 模块系统演示数据
const moduleSystemData = {
    commonjs: {
        modules: {
            'math.js': {
                type: 'commonjs',
                content: `const PI = 3.14159;

function add(a, b) {
    return a + b;
}

function subtract(a, b) {
    return a - b;
}

module.exports = {
    PI,
    add,
    subtract
};`
            },
            'main.js': {
                type: 'commonjs',
                content: `const { PI, add, subtract } = require('./math.js');

console.log('PI =', PI);
console.log('5 + 3 =', add(5, 3));
console.log('10 - 4 =', subtract(10, 4));`
            }
        }
    },
    esmodules: {
        modules: {
            'math.js': {
                type: 'esm',
                content: `export const PI = 3.14159;

export function add(a, b) {
    return a + b;
}

export function subtract(a, b) {
    return a - b;
}

export default function multiply(a, b) {
    return a * b;
};`
            },
            'main.js': {
                type: 'esm',
                content: `import multiply, { PI, add, subtract } from './math.js';

console.log('PI =', PI);
console.log('5 + 3 =', add(5, 3));
console.log('10 - 4 =', subtract(10, 4));
console.log('5 * 3 =', multiply(5, 3));`
            }
        }
    },
    modules: {}
};

// 代码分割演示
const codeModules = {
    'dashboard': {
        name: '仪表板',
        size: '45KB',
        dependencies: ['charts', 'utils'],
        loaded: false
    },
    'profile': {
        name: '个人资料',
        size: '28KB',
        dependencies: ['form-utils', 'validation'],
        loaded: false
    },
    'analytics': {
        name: '数据分析',
        size: '65KB',
        dependencies: ['charts', 'data-processing', 'api'],
        loaded: false
    }
};

// 模块联邦演示数据
const microFrontends = {
    'header': {
        name: 'Header组件',
        size: '15KB',
        url: 'http://header.example.com/remoteEntry.js',
        exposedModule: './Header'
    },
    'sidebar': {
        name: '侧边栏组件',
        size: '22KB',
        url: 'http://sidebar.example.com/remoteEntry.js',
        exposedModule: './Sidebar'
    },
    'footer': {
        name: 'Footer组件',
        size: '12KB',
        url: 'http://footer.example.com/remoteEntry.js',
        exposedModule: './Footer'
    }
};

// 切换标签页
function switchTab(tabName) {
    // 隐藏所有标签内容
    const tabs = document.querySelectorAll('.tab-content');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // 移除所有按钮的active类
    const buttons = document.querySelectorAll('.tab-button');
    buttons.forEach(button => button.classList.remove('active'));
    
    // 显示选中的标签内容
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // 设置选中按钮的active类
    event.target.classList.add('active');
}

// 模拟CommonJS加载
function simulateCommonJS() {
    const modules = moduleSystemData.commonjs.modules;
    const result = [];
    
    // 模拟同步加载
    result.push('开始加载模块 (同步)...\n');
    
    // 加载math.js模块
    result.push('加载模块: math.js');
    const mathModule = simulateModuleLoad(modules['math.js']);
    result.push('math.js 加载完成');
    
    // 加载main.js模块
    result.push('加载模块: main.js');
    const mainModule = simulateModuleLoad(modules['main.js']);
    result.push('main.js 加载完成');
    
    // 执行main.js
    result.push('\n执行main.js:');
    result.push('PI = 3.14159');
    result.push('5 + 3 = 8');
    result.push('10 - 4 = 6');
    
    showResult('moduleResult', result.join('\n'));
}

// 模拟ES Modules加载
function simulateESModules() {
    const modules = moduleSystemData.esmodules.modules;
    const result = [];
    
    // 模拟异步加载
    result.push('开始加载模块 (异步)...\n');
    
    // 加载main.js模块
    result.push('解析main.js依赖: ./math.js');
    result.push('加载模块: math.js');
    const mathModule = simulateModuleLoad(modules['math.js']);
    result.push('math.js 加载完成');
    
    result.push('加载模块: main.js');
    const mainModule = simulateModuleLoad(modules['main.js']);
    result.push('main.js 加载完成');
    
    // 执行main.js
    result.push('\n执行main.js:');
    result.push('PI = 3.14159');
    result.push('5 + 3 = 8');
    result.push('10 - 4 = 6');
    result.push('5 * 3 = 15');
    
    showResult('moduleResult', result.join('\n'));
}

// 模拟模块加载
function simulateModuleLoad(module) {
    // 模拟模块解析和执行
    return {
        type: module.type,
        exports: module.content
    };
}

// 代码分割演示 - 加载模块
async function loadModule(moduleName) {
    const spinner = document.getElementById(`spinner-${moduleName}`);
    const moduleInfo = codeModules[moduleName];
    
    if (!moduleInfo) {
        showResult('codeSplittingResult', `模块 ${moduleName} 不存在`);
        return;
    }
    
    if (moduleInfo.loaded) {
        showResult('codeSplittingResult', `模块 ${moduleInfo.name} 已经加载`);
        return;
    }
    
    // 显示加载动画
    spinner.style.display = 'inline-block';
    
    // 模拟异步加载
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // 标记为已加载
    moduleInfo.loaded = true;
    
    // 隐藏加载动画
    spinner.style.display = 'none';
    
    // 更新UI
    addModuleToDiagram(moduleName, moduleInfo);
    
    // 显示结果
    showResult('codeSplittingResult', `成功加载模块: ${moduleInfo.name} (${moduleInfo.size})`);
    updateBundleChart();
}

// 添加模块到图表
function addModuleToDiagram(moduleName, moduleInfo) {
    const container = document.getElementById('moduleContainer');
    
    // 检查是否已存在
    const existingModule = container.querySelector(`[data-module="${moduleName}"]`);
    if (existingModule) return;
    
    // 创建模块元素
    const moduleElement = document.createElement('div');
    moduleElement.className = 'module-box';
    moduleElement.setAttribute('data-module', moduleName);
    moduleElement.textContent = moduleInfo.name;
    
    container.appendChild(moduleElement);
}

// 更新打包图表
function updateBundleChart() {
    const chart = document.getElementById('bundleChart');
    const loadedModules = Object.entries(codeModules)
        .filter(([_, info]) => info.loaded)
        .map(([_, info]) => ({
            name: info.name,
            size: parseInt(info.size)
        }));
    
    // 清空图表
    chart.innerHTML = '';
    
    if (loadedModules.length === 0) {
        chart.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #888;">暂无已加载模块</div>';
        return;
    }
    
    // 计算总大小
    const totalSize = loadedModules.reduce((sum, module) => sum + module.size, 0);
    
    // 创建图表条
    const chartHTML = loadedModules.map((module, index) => {
        const percentage = (module.size / totalSize * 100).toFixed(1);
        const colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'];
        const color = colors[index % colors.length];
        
        return `
            <div style="
                height: 100%;
                width: ${percentage}%;
                background-color: ${color};
                display: inline-block;
                position: relative;
                color: white;
                text-align: center;
                line-height: 200px;
                font-weight: bold;
                border-right: 1px solid white;
            " title="${module.name}: ${module.size}KB">
                ${percentage > 10 ? `${module.name} (${percentage}%)` : ''}
            </div>
        `;
    }).join('');
    
    chart.innerHTML = chartHTML;
    
    // 添加图例
    const legend = document.createElement('div');
    legend.style.marginTop = '10px';
    legend.innerHTML = '<strong>图例:</strong> ' + loadedModules.map((module, index) => {
        const colors = ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6'];
        const color = colors[index % colors.length];
        return `<span style="display: inline-block; width: 15px; height: 15px; background-color: ${color}; margin-right: 5px; border-radius: 2px;"></span>${module.name} (${module.size}KB)`;
    }).join(' ');
    
    chart.appendChild(legend);
}

// 显示已加载模块
function showLoadedModules() {
    const loadedModules = Object.entries(codeModules)
        .filter(([_, info]) => info.loaded)
        .map(([name, info]) => `${name}: ${info.name} (${info.size})`);
    
    if (loadedModules.length === 0) {
        showResult('codeSplittingResult', '尚未加载任何模块');
        return;
    }
    
    showResult('codeSplittingResult', '已加载的模块:\n' + loadedModules.join('\n'));
}

// 模块联邦演示 - 加载远程组件
async function loadRemoteComponent(componentName, displayName) {
    const componentInfo = microFrontends[componentName];
    
    if (!componentInfo) {
        showResult('moduleFederationResult', `组件 ${componentName} 不存在`);
        return;
    }
    
    showResult('moduleFederationResult', `正在加载远程组件: ${displayName}`);
    
    // 模拟异步加载
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // 添加到架构图
    addRemoteComponentToDiagram(componentName, displayName);
    
    showResult('moduleFederationResult', `成功加载远程组件: ${displayName} (${componentInfo.size})\n来源: ${componentInfo.url}`);
}

// 添加远程组件到架构图
function addRemoteComponentToDiagram(componentName, displayName) {
    const container = document.getElementById('federationContainer');
    
    // 检查是否已存在
    const existingComponent = container.querySelector(`[data-component="${componentName}"]`);
    if (existingComponent) return;
    
    // 创建组件元素
    const componentElement = document.createElement('div');
    componentElement.className = 'module-box';
    componentElement.setAttribute('data-component', componentName);
    componentElement.innerHTML = `${displayName}<br><small>(${componentName})</small>`;
    
    container.appendChild(componentElement);
}

// 显示应用架构
function showAppArchitecture() {
    const diagram = document.getElementById('federationContainer');
    const components = Array.from(diagram.querySelectorAll('[data-component]'));
    
    if (components.length === 0) {
        showResult('moduleFederationResult', '尚未加载任何远程组件');
        return;
    }
    
    const architecture = {
        host: '宿主应用',
        remoteComponents: components.map(el => ({
            name: el.getAttribute('data-component'),
            displayName: el.textContent.trim()
        }))
    };
    
    let result = '微前端架构:\n\n';
    result += `宿主应用 (main)\n`;
    
    architecture.remoteComponents.forEach(comp => {
        const info = microFrontends[comp.name];
        result += `├── 远程组件: ${comp.displayName} (${info.size})\n`;
        result += `│   └── URL: ${info.url}\n`;
    });
    
    showResult('moduleFederationResult', result);
}

// 性能优化演示
function analyzeBundle() {
    // 模拟打包分析
    const bundleAnalysis = {
        'main.js': { size: '45KB', modules: 12 },
        'vendor.js': { size: '128KB', modules: 45 },
        'common.js': { size: '23KB', modules: 8 },
        'utils.js': { size: '15KB', modules: 6 },
        'dashboard.js': { size: '38KB', modules: 15 },
        'profile.js': { size: '22KB', modules: 10 },
    };
    
    let result = '打包分析结果:\n\n';
    
    const totalSize = Object.values(bundleAnalysis)
        .reduce((sum, bundle) => sum + parseInt(bundle.size), 0);
    
    result += `总计: ${totalSize}KB\n\n`;
    result += '各打包文件详情:\n';
    
    Object.entries(bundleAnalysis).forEach(([name, info]) => {
        const percentage = (parseInt(info.size) / totalSize * 100).toFixed(1);
        result += `${name}: ${info.size} (${percentage}%) - ${info.modules}个模块\n`;
    });
    
    result += '\n优化建议:\n';
    result += '1. 考虑进一步分割vendor.js，提取常用库\n';
    result += '2. Dashboard.js较大，可考虑拆分子模块\n';
    result += '3. 检查是否有未使用的依赖可以被移除\n';
    
    showResult('performanceResult', result);
}

function simulateOptimization() {
    let result = '模拟应用优化策略...\n\n';
    
    result += '1. Tree Shaking\n';
    result += '   移除未使用的代码: -12KB\n\n';
    
    result += '2. 代码压缩\n';
    result += '   使用TerserPlugin: -28KB\n\n';
    
    result += '3. 图片优化\n';
    result += '   WebP转换: -15KB\n\n';
    
    result += '4. 依赖优化\n';
    result += '   替换moment.js为dayjs: -25KB\n\n';
    
    result += '5. Gzip压缩\n';
    result += '   服务器端压缩: -45KB\n\n';
    
    result += '总计优化: -125KB (约25%减小)';
    
    showResult('performanceResult', result);
}

function showPerformanceMetrics() {
    const metrics = {
        '首屏加载时间': '1.8秒',
        '最大内容绘制': '2.4秒',
        '首次输入延迟': '120ms',
        '累积布局偏移': '0.08',
        '交互响应时间': '95ms',
        '资源加载数量': '18个',
        'JS主线程时间': '450ms',
        '内存使用': '12MB'
    };
    
    let result = '性能指标:\n\n';
    
    Object.entries(metrics).forEach(([name, value]) => {
        result += `${name}: ${value}\n`;
    });
    
    result += '\n建议:\n';
    result += '1. 减少初始JS包大小以提高加载速度\n';
    result += '2. 使用懒加载减少非关键资源的加载时间\n';
    result += '3. 优化图片以减少LCP时间\n';
    result += '4. 延迟加载非关键CSS';
    
    showResult('performanceResult', result);
}

// 构建工具对比
function compareBuildTools() {
    let result = '构建工具对比:\n\n';
    
    result += 'Webpack:\n';
    result += '✓ 功能最全面，插件生态系统丰富\n';
    result += '✓ 成熟稳定，广泛使用\n';
    result.push('✗ 配置复杂，学习曲线陡峭');
    result.push('✗ 开发环境下构建速度较慢\n\n');
    
    result += 'Vite:\n';
    result += '✓ 开发环境极快的热更新\n';
    result += '✓ 配置简单，开箱即用\n';
    result += '✗ 生态系统相对较新\n';
    result += '✗ 某些高级功能不如Webpack灵活\n\n';
    
    result += 'Rollup:\n';
    result += '✓ 生成的bundle小而高效\n';
    result += '✓ 专注于库的打包\n';
    result += '✗ 功能相对有限\n';
    result += '✗ 复杂应用支持不如Webpack\n\n';
    
    result += '选择建议:\n';
    result += '大型企业应用 → Webpack\n';
    result += '现代SPA项目 → Vite\n';
    result += '库/组件开发 → Rollup';
    
    showResult('buildToolsResult', result);
}

function simulateWebpack() {
    let result = '模拟Webpack打包过程...\n\n';
    
    result += '1. 解析配置文件 webpack.config.js\n';
    result += '2. 构建依赖图\n';
    result += '3. 应用loader (babel-loader, css-loader...)\n';
    result += '4. 应用插件 (HtmlWebpackPlugin...)\n';
    result += '5. 优化和压缩\n';
    result += '6. 输出打包文件\n\n';
    
    result += '打包结果:\n';
    result += '└── dist/\n';
    result += '    ├── main.js (45KB)\n';
    result += '    ├── vendor.js (128KB)\n';
    result += '    ├── main.css (15KB)\n';
    result += '    └── index.html (2KB)\n';
    
    result += '\n总构建时间: 3.2秒';
    
    showResult('buildToolsResult', result);
}

function simulateVite() {
    let result = '模拟Vite构建过程...\n\n';
    
    result += '开发模式:\n';
    result += '1. 启动开发服务器 (0.5秒)\n';
    result += '2. 浏览器请求模块\n';
    result += '3. 按需编译ES模块\n';
    result += '4. 热更新生效\n\n';
    
    result += '生产模式:\n';
    result += '1. 使用Rollup打包\n';
    result += '2. 应用插件和优化\n';
    result += '3. 代码分割和Tree Shaking\n';
    result += '4. 压缩和输出\n\n';
    
    result += '打包结果:\n';
    result += '└── dist/\n';
    result += '    ├── index.html (2KB)\n';
    result += '    ├── assets/\n';
    result += '    │   ├── index.js (38KB)\n';
    result += '    │   ├── vendor.js (95KB)\n';
    result += '    │   └── style.css (12KB)\n';
    
    result += '\n总构建时间: 1.8秒';
    
    showResult('buildToolsResult', result);
}

// 辅助函数：在指定元素中显示结果
function showResult(elementId, content) {
    document.getElementById(elementId).textContent = content;
}