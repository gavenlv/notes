// 第5章：DOM操作与事件处理 - 示例代码

// ====================== DOM基础 ======================

// 1.1 DOM节点类型
console.log(Node.ELEMENT_NODE);      // 1 - 元素节点
console.log(Node.TEXT_NODE);         // 3 - 文本节点
console.log(Node.COMMENT_NODE);      // 8 - 注释节点
console.log(Node.DOCUMENT_NODE);     // 9 - 文档节点
console.log(Node.DOCUMENT_TYPE_NODE); // 10 - 文档类型节点

// 1.2 DOM树遍历
function demonstrateDOMTraversal() {
    const container = document.getElementById('container');
    
    // 获取父节点
    console.log(container.parentNode);     // 父节点（包含文本节点）
    console.log(container.parentElement);    // 父元素节点
    
    // 获取子节点
    console.log(container.childNodes);     // 所有子节点（包含文本节点）
    console.log(container.children);        // 所有子元素节点
    
    // 获取第一个/最后一个子节点
    console.log(container.firstChild);      // 第一个子节点（可能是文本节点）
    console.log(container.firstElementChild); // 第一个元素子节点
    console.log(container.lastChild);       // 最后一个子节点（可能是文本节点）
    console.log(container.lastElementChild);  // 最后一个元素子节点
    
    // 获取兄弟节点
    const firstChild = container.firstElementChild;
    console.log(firstChild.nextSibling);        // 下一个兄弟节点（可能是文本节点）
    console.log(firstChild.nextElementSibling);  // 下一个兄弟元素节点
    console.log(firstChild.previousSibling);    // 上一个兄弟节点（可能是文本节点）
    console.log(firstChild.previousElementSibling); // 上一个兄弟元素节点
}

// ====================== 元素选择 ======================

// 2.1 传统选择方法
function traditionalSelectors() {
    // 通过ID选择元素（返回单个元素）
    const elementById = document.getElementById('myId');
    
    // 通过标签名选择元素（返回HTMLCollection）
    const elementsByTag = document.getElementsByTagName('div');
    
    // 通过类名选择元素（返回HTMLCollection）
    const elementsByClass = document.getElementsByClassName('myClass');
    
    // 通过name属性选择元素（返回NodeList）
    const elementsByName = document.getElementsByName('username');
}

// 2.2 现代选择方法
function modernSelectors() {
    // querySelector - 返回第一个匹配的元素
    const firstDiv = document.querySelector('div');
    const firstWithClass = document.querySelector('.myClass');
    const firstWithId = document.querySelector('#myId');
    const complexSelector = document.querySelector('div.container > p.highlight');
    
    // querySelectorAll - 返回所有匹配的元素（NodeList）
    const allDivs = document.querySelectorAll('div');
    const allWithClass = document.querySelectorAll('.myClass');
    const allNested = document.querySelectorAll('ul li');
}

// 2.3 选择器示例
function selectorExamples() {
    // 基本选择器
    document.querySelector('div');        // 标签选择器
    document.querySelector('#myId');     // ID选择器
    document.querySelector('.myClass');  // 类选择器
    
    // 组合选择器
    document.querySelector('div.container');  // 类为container的div元素
    document.querySelector('#header nav');    // ID为header内的nav元素
    
    // 属性选择器
    document.querySelector('[data-id]');                    // 有data-id属性的元素
    document.querySelector('[type="text"]');                 // type属性等于text的元素
    document.querySelector('[class^="btn"]');                // class属性以btn开头的元素
    document.querySelector('[class$="active"]');              // class属性以active结尾的元素
    document.querySelector('[class*="item"]');                // class属性包含item的元素
    
    // 伪类选择器
    document.querySelector(':first-child');      // 第一个子元素
    document.querySelector(':last-child');       // 最后一个子元素
    document.querySelector(':nth-child(2)');    // 第2个子元素
    document.querySelector(':nth-child(even)'); // 偶数位置的子元素
    document.querySelector(':not(.disabled)');  // 不包含disabled类的元素
}

// ====================== DOM操作 ======================

// 3.1 创建元素
function createElementExample() {
    // 创建元素
    const newDiv = document.createElement('div');
    const newP = document.createElement('p');
    const newImg = document.createElement('img');
    
    // 创建文本节点
    const textNode = document.createTextNode('这是文本内容');
    
    // 创建文档片段（用于批量添加元素）
    const fragment = document.createDocumentFragment();
    
    // 设置属性
    newDiv.id = 'newElement';
    newDiv.className = 'container highlight';
    newDiv.setAttribute('data-id', '12345');
    
    // 设置样式
    newDiv.style.color = 'red';
    newDiv.style.fontSize = '16px';
    newDiv.style.backgroundColor = '#f0f0f0';
    
    // 设置HTML内容和文本内容
    newDiv.innerHTML = '<strong>重要内容</strong>';
    newP.textContent = '这是纯文本内容';
    
    return newDiv;
}

// 3.2 添加元素
function addElementExample() {
    const parent = document.getElementById('parent');
    
    // 创建新元素
    const newElement = document.createElement('div');
    newElement.textContent = '新添加的元素';
    
    // 添加到父元素的末尾
    parent.appendChild(newElement);
    
    // 插入到指定元素之前
    const firstChild = parent.firstElementChild;
    parent.insertBefore(newElement, firstChild);
    
    // 使用insertAdjacentHTML插入HTML字符串
    parent.insertAdjacentHTML('beforeend', '<p>插入的段落</p>');
    parent.insertAdjacentHTML('afterbegin', '<p>开头的段落</p>');
    parent.insertAdjacentHTML('beforebegin', '<div>外部的div</div>');
    parent.insertAdjacentHTML('afterend', '<div>后面外部的div</div>');
    
    // 使用insertAdjacentElement插入元素
    const anotherElement = document.createElement('span');
    anotherElement.textContent = '另一个元素';
    parent.insertAdjacentElement('beforeend', anotherElement);
}

// 3.3 移除和替换元素
function removeReplaceElementExample() {
    // 移除元素
    const elementToRemove = document.getElementById('removeMe');
    elementToRemove.parentNode.removeChild(elementToRemove);
    // 或者在现代浏览器中
    elementToRemove.remove();
    
    // 替换元素
    const oldElement = document.getElementById('oldElement');
    const newElement = document.createElement('div');
    newElement.textContent = '新元素';
    oldElement.parentNode.replaceChild(newElement, oldElement);
    
    // 清空元素内容
    const container = document.getElementById('container');
    container.innerHTML = '';  // 清除所有内容
    // 或者
    while (container.firstChild) {
        container.removeChild(container.firstChild);
    }
}

// 3.4 批量添加元素（性能优化）
function batchAddElements() {
    // 不好的做法：多次操作DOM
    for (let i = 1; i <= 100; i++) {
        const li = document.createElement('li');
        li.textContent = `项目 ${i}`;
        document.getElementById('list').appendChild(li);
    }
    
    // 好的做法：使用文档片段
    const fragment = document.createDocumentFragment();
    for (let i = 1; i <= 100; i++) {
        const li = document.createElement('li');
        li.textContent = `项目 ${i}`;
        fragment.appendChild(li);
    }
    document.getElementById('list').appendChild(fragment);
}

// 3.5 克隆元素
function cloneElementExample() {
    const original = document.getElementById('original');
    
    // 浅克隆（不克隆事件监听器）
    const shallowClone = original.cloneNode(false);
    
    // 深克隆（克隆所有子节点）
    const deepClone = original.cloneNode(true);
    
    // 克隆后修改
    deepClone.id = 'clonedElement';
    deepClone.querySelector('h1').textContent = '克隆的标题';
}

// ====================== 属性与样式操作 ======================

// 4.1 属性操作
function attributeOperations() {
    const element = document.getElementById('myElement');
    
    // 获取属性
    const id = element.id;
    const className = element.className;
    const value = element.getAttribute('data-custom');
    const hasAttribute = element.hasAttribute('data-custom');
    
    // 设置属性
    element.id = 'newId';
    element.className = 'newClass anotherClass';
    element.setAttribute('data-custom', 'customValue');
    element.setAttribute('tabindex', '0');
    
    // 移除属性
    element.removeAttribute('data-custom');
    
    // 布尔属性
    const checkbox = document.getElementById('myCheckbox');
    checkbox.checked = true;        // 设置为选中
    checkbox.checked;               // 检查是否选中
    
    // 自定义数据属性（data-*）
    element.dataset.userId = '12345';
    element.dataset.info = '一些信息';
    console.log(element.dataset.userId); // '12345'
}

// 4.2 类名操作
function classOperations() {
    const element = document.getElementById('myElement');
    
    // 直接设置className
    element.className = 'new-class';
    element.className += ' another-class'; // 添加类名
    
    // classList API（推荐）
    element.classList.add('class1');           // 添加类
    element.classList.remove('class2');        // 移除类
    element.classList.toggle('class3');        // 切换类（有则删除，无则添加）
    element.classList.contains('class4');      // 检查是否包含类
    element.classList.replace('oldClass', 'newClass'); // 替换类
    
    // 一次性添加/移除多个类
    element.classList.add('class1', 'class2', 'class3');
    element.classList.remove('class1', 'class2', 'class3');
}

// 4.3 样式操作
function styleOperations() {
    const element = document.getElementById('myElement');
    
    // 直接设置单个样式
    element.style.color = 'red';
    element.style.fontSize = '16px';
    element.style.backgroundColor = '#f0f0f0';
    
    // 注意：CSS属性名中的连字符(-)需要转换为驼峰命名法
    // border-left-width -> borderLeftWidth
    // z-index -> zIndex
    
    // 获取计算样式（只读）
    const computedStyle = window.getComputedStyle(element);
    const bgColor = computedStyle.backgroundColor;
    const width = computedStyle.width;
    
    // 获取元素的位置和大小
    const rect = element.getBoundingClientRect();
    console.log(rect.left, rect.top, rect.width, rect.height);
    
    // 批量设置样式
    Object.assign(element.style, {
        color: 'blue',
        fontSize: '18px',
        fontWeight: 'bold',
        padding: '10px'
    });
    
    // 使用CSS变量
    document.documentElement.style.setProperty('--main-color', '#3498db');
    const mainColor = getComputedStyle(document.documentElement).getPropertyValue('--main-color');
}

// ====================== 表单操作 ======================

// 5.1 表单元素获取
function formElementAccess() {
    // 获取表单元素
    const form = document.getElementById('myForm');
    
    // 获取表单中的所有控件
    const elements = form.elements;  // HTMLCollection
    
    // 通过name或id获取控件
    const username = form.elements['username'];
    const password = form.elements.password;
    
    // 获取特定类型的控件
    const inputs = form.querySelectorAll('input');
    const checkboxes = form.querySelectorAll('input[type="checkbox"]');
    const radios = form.querySelectorAll('input[type="radio"]');
    const selects = form.querySelectorAll('select');
    const textareas = form.querySelectorAll('textarea');
}

// 5.2 表单值操作
function formValueOperations() {
    // 获取和设置文本输入框的值
    const textInput = document.getElementById('username');
    textInput.value = '新值';
    console.log(textInput.value);
    
    // 获取和设置复选框的值和状态
    const checkbox = document.getElementById('remember');
    checkbox.checked = true;  // 选中
    console.log(checkbox.checked);  // 是否选中
    
    // 处理单选按钮
    const radioButtons = document.querySelectorAll('input[name="gender"]');
    let selectedGender;
    radioButtons.forEach(radio => {
        if (radio.checked) {
            selectedGender = radio.value;
        }
    });
    
    // 设置单选按钮
    radioButtons.forEach(radio => {
        if (radio.value === 'male') {
            radio.checked = true;
        }
    });
    
    // 处理下拉选择框
    const select = document.getElementById('country');
    console.log(select.value);  // 选中项的值
    console.log(select.selectedIndex);  // 选中项的索引
    console.log(select.options[select.selectedIndex].text);  // 选中项的文本
    
    // 设置下拉选择框
    select.value = 'china';
    // 或者
    select.selectedIndex = 2;  // 选择第三项
    
    // 处理多选下拉框
    const multiSelect = document.getElementById('skills');
    const selectedSkills = Array.from(multiSelect.options)
        .filter(option => option.selected)
        .map(option => option.value);
    
    // 处理多选复选框
    const checkboxes = document.querySelectorAll('input[type="checkbox"][name="interests"]:checked');
    const selectedInterests = Array.from(checkboxes).map(cb => cb.value);
}

// 5.3 表单验证
function formValidation() {
    const form = document.getElementById('myForm');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    
    // 验证电子邮件
    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }
    
    // 验证密码
    function validatePassword(password) {
        return password.length >= 8 && /[A-Z]/.test(password) && /[0-9]/.test(password);
    }
    
    // 显示错误信息
    function showError(input, message) {
        const errorElement = document.getElementById(`${input.id}Error`);
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
        }
        input.classList.add('invalid');
    }
    
    // 清除错误信息
    function clearError(input) {
        const errorElement = document.getElementById(`${input.id}Error`);
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.style.display = 'none';
        }
        input.classList.remove('invalid');
    }
    
    // 实时验证
    emailInput.addEventListener('input', function() {
        if (this.value && !validateEmail(this.value)) {
            showError(this, '请输入有效的电子邮件地址');
        } else {
            clearError(this);
        }
    });
    
    passwordInput.addEventListener('input', function() {
        if (this.value && !validatePassword(this.value)) {
            showError(this, '密码必须至少8位，包含大写字母和数字');
        } else {
            clearError(this);
        }
    });
    
    // 表单提交验证
    form.addEventListener('submit', function(event) {
        let isValid = true;
        
        // 验证电子邮件
        if (!emailInput.value) {
            showError(emailInput, '请输入电子邮件');
            isValid = false;
        } else if (!validateEmail(emailInput.value)) {
            showError(emailInput, '请输入有效的电子邮件地址');
            isValid = false;
        } else {
            clearError(emailInput);
        }
        
        // 验证密码
        if (!passwordInput.value) {
            showError(passwordInput, '请输入密码');
            isValid = false;
        } else if (!validatePassword(passwordInput.value)) {
            showError(passwordInput, '密码必须至少8位，包含大写字母和数字');
            isValid = false;
        } else {
            clearError(passwordInput);
        }
        
        if (!isValid) {
            event.preventDefault();
        }
    });
}

// ====================== 事件处理 ======================

// 6.1 事件监听器
function eventListeners() {
    const button = document.getElementById('myButton');
    
    // 使用addEventListener（推荐）
    button.addEventListener('click', function() {
        console.log('按钮被点击了');
    });
    
    // 使用箭头函数
    button.addEventListener('click', () => {
        console.log('箭头函数处理点击事件');
    });
    
    // 使用命名函数
    function handleClick() {
        console.log('命名函数处理点击事件');
    }
    button.addEventListener('click', handleClick);
    
    // 添加多个事件监听器
    button.addEventListener('click', function() {
        console.log('第一个监听器');
    });
    button.addEventListener('click', function() {
        console.log('第二个监听器');
    });
    
    // 事件监听器参数
    button.addEventListener('click', function(event) {
        console.log('事件对象:', event);
        console.log('事件类型:', event.type);
        console.log('目标元素:', event.target);
        console.log('当前元素:', event.currentTarget);
    });
    
    // 移除事件监听器
    button.removeEventListener('click', handleClick);
    
    // 事件只触发一次
    button.addEventListener('click', function() {
        console.log('这只触发一次');
    }, { once: true });
    
    // 传统方式（不推荐，只能添加一个监听器）
    button.onclick = function() {
        console.log('传统方式处理点击事件');
    };
}

// 6.2 事件对象
function eventObject() {
    const button = document.getElementById('myButton');
    
    button.addEventListener('click', function(event) {
        // 事件基本信息
        console.log('事件类型:', event.type);        // 'click'
        console.log('目标元素:', event.target);      // 被点击的元素
        console.log('当前元素:', event.currentTarget); // 绑定事件的元素
        
        // 鼠标位置信息
        console.log('相对于视口的坐标:', event.clientX, event.clientY);
        console.log('相对于页面的坐标:', event.pageX, event.pageY);
        console.log('相对于屏幕的坐标:', event.screenX, event.screenY);
        
        // 按键信息（鼠标事件）
        console.log('是否按下了Ctrl:', event.ctrlKey);
        console.log('是否按下了Shift:', event.shiftKey);
        console.log('是否按下了Alt:', event.altKey);
        console.log('是否按下了Meta:', event.metaKey);
        console.log('鼠标按键:', event.button);      // 0:左键, 1:中键, 2:右键
        console.log('鼠标按键（详细）:', event.buttons);
        
        // 阻止默认行为
        event.preventDefault();   // 阻止元素的默认行为
        
        // 停止事件传播
        event.stopPropagation();  // 停止事件冒泡
        
        // 立即停止事件传播并阻止其他监听器
        event.stopImmediatePropagation();
    });
}

// 6.3 键盘事件
function keyboardEvents() {
    document.addEventListener('keydown', function(event) {
        console.log('按键代码:', event.code);        // 'KeyA', 'Enter'等
        console.log('按键值:', event.key);           // 'a', 'Enter'等
        console.log('按键是否重复:', event.repeat);  // 是否长按
        console.log('是否为输入键:', event.isComposing); // 是否为输入法组合键
    });
}

// 6.4 表单事件
function formEvents() {
    const form = document.getElementById('myForm');
    form.addEventListener('submit', function(event) {
        event.preventDefault();  // 阻止表单默认提交行为
        
        // 获取表单数据
        const formData = new FormData(form);
        console.log('表单数据:', formData);
        
        // 转换为普通对象
        const data = {};
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        console.log('表单数据对象:', data);
    });
}

// 6.5 事件冒泡与捕获
function eventBubblingCapturing() {
    const outer = document.getElementById('outer');
    const middle = document.getElementById('middle');
    const inner = document.getElementById('inner');
    
    // 事件捕获阶段（从外到内）
    outer.addEventListener('click', function() {
        console.log('外层 - 捕获阶段');
    }, true);  // 第三个参数为true表示在捕获阶段处理
    
    middle.addEventListener('click', function() {
        console.log('中层 - 捕获阶段');
    }, true);
    
    inner.addEventListener('click', function() {
        console.log('内层 - 捕获阶段');
    }, true);
    
    // 事件冒泡阶段（从内到外，默认）
    inner.addEventListener('click', function() {
        console.log('内层 - 冒泡阶段');
    });  // 第三个参数默认为false
    
    middle.addEventListener('click', function() {
        console.log('中层 - 冒泡阶段');
    });
    
    outer.addEventListener('click', function() {
        console.log('外层 - 冒泡阶段');
    });
    
    // 阻止事件冒泡
    inner.addEventListener('click', function(event) {
        console.log('内层 - 冒泡阶段（已阻止冒泡）');
        event.stopPropagation();  // 阻止事件继续冒泡
    });
}

// 6.6 事件委托
function eventDelegation() {
    const list = document.getElementById('list');
    
    list.addEventListener('click', function(event) {
        // 检查点击的是否是列表项
        if (event.target.tagName === 'LI') {
            console.log('点击了列表项:', event.target.textContent);
            
            // 可以在这里操作被点击的元素
            event.target.classList.toggle('selected');
        }
    });
    
    // 事件委托的优点：
    // 1. 减少事件监听器的数量，提高性能
    // 2. 动态添加的元素也能自动处理事件
    // 3. 简化代码管理
}

// ====================== 实用示例 ======================

// 7.1 选项卡切换
function initTabs() {
    const tabButtons = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // 为每个选项卡按钮添加点击事件
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            // 获取要显示的选项卡ID
            const tabId = this.getAttribute('data-tab');
            
            // 移除所有按钮和内容的active类
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // 为当前按钮和对应内容添加active类
            this.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
}

// 7.2 拖拽功能
function makeDraggable(element) {
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;
    
    // 鼠标按下
    element.addEventListener('mousedown', dragStart);
    
    // 鼠标移动
    document.addEventListener('mousemove', drag);
    
    // 鼠标释放
    document.addEventListener('mouseup', dragEnd);
    
    function dragStart(e) {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        
        if (e.target === element) {
            isDragging = true;
        }
    }
    
    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            
            xOffset = currentX;
            yOffset = currentY;
            
            setTranslate(currentX, currentY, element);
        }
    }
    
    function dragEnd(e) {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
    }
    
    function setTranslate(xPos, yPos, el) {
        el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
    }
}

// 7.3 无限滚动加载
function initInfiniteScroll() {
    const container = document.getElementById('content-container');
    let page = 1;
    let isLoading = false;
    
    // 模拟数据加载函数
    function loadData(page) {
        return new Promise((resolve) => {
            setTimeout(() => {
                const items = [];
                for (let i = 1; i <= 10; i++) {
                    const itemNum = (page - 1) * 10 + i;
                    items.push(`<div class="item">项目 ${itemNum}</div>`);
                }
                resolve(items);
            }, 1000);  // 模拟网络延迟
        });
    }
    
    // 渲染数据
    async function renderData(items) {
        const fragment = document.createDocumentFragment();
        items.forEach(itemHtml => {
            const div = document.createElement('div');
            div.innerHTML = itemHtml;
            fragment.appendChild(div.firstElementChild);
        });
        container.appendChild(fragment);
    }
    
    // 加载更多数据
    async function loadMore() {
        if (isLoading) return;
        
        isLoading = true;
        
        // 显示加载指示器
        const loader = document.getElementById('loader');
        if (loader) loader.style.display = 'block';
        
        try {
            const items = await loadData(page);
            await renderData(items);
            page++;
        } catch (error) {
            console.error('加载数据失败:', error);
        } finally {
            isLoading = false;
            if (loader) loader.style.display = 'none';
        }
    }
    
    // 检查是否需要加载更多
    function checkScroll() {
        const scrollTop = window.scrollY || document.documentElement.scrollTop;
        const windowHeight = window.innerHeight;
        const documentHeight = document.documentElement.scrollHeight;
        
        // 当滚动到距离底部100px时加载更多
        if (scrollTop + windowHeight >= documentHeight - 100) {
            loadMore();
        }
    }
    
    // 监听滚动事件（使用节流优化性能）
    let throttleTimer;
    function throttleCheckScroll() {
        if (throttleTimer) return;
        
        throttleTimer = setTimeout(() => {
            checkScroll();
            throttleTimer = null;
        }, 200);  // 200ms节流
    }
    
    window.addEventListener('scroll', throttleCheckScroll);
    
    // 初始加载
    loadMore();
}

// ====================== 性能优化 ======================

// 8.1 节流和防抖
function throttleAndDebounce() {
    // 节流：限制函数的执行频率
    function throttle(func, delay) {
        let lastCall = 0;
        return function(...args) {
            const now = new Date().getTime();
            if (now - lastCall < delay) return;
            lastCall = now;
            return func(...args);
        };
    }
    
    // 防抖：延迟执行，如果在延迟时间内再次调用则重新计时
    function debounce(func, delay) {
        let timerId;
        return function(...args) {
            clearTimeout(timerId);
            timerId = setTimeout(() => func(...args), delay);
        };
    }
    
    // 应用到滚动事件
    window.addEventListener('scroll', throttle(function() {
        console.log('滚动事件（节流处理）');
    }, 200));
    
    // 应用到输入事件
    searchInput.addEventListener('input', debounce(function() {
        console.log('搜索输入（防抖处理）');
        // 发送搜索请求
    }, 300));
}

// 8.2 批量DOM操作
function batchDOMOperations() {
    // 不好的做法：多次操作DOM
    for (let i = 0; i < 100; i++) {
        document.getElementById('list').innerHTML += `<li>项目 ${i}</li>`;
    }
    
    // 好的做法：使用文档片段
    const fragment = document.createDocumentFragment();
    for (let i = 0; i < 100; i++) {
        const li = document.createElement('li');
        li.textContent = `项目 ${i}`;
        fragment.appendChild(li);
    }
    document.getElementById('list').appendChild(fragment);
}

// ====================== 可访问性 ======================

// 9.1 键盘导航
function keyboardNavigation() {
    // 为可交互元素添加键盘支持
    const buttons = document.querySelectorAll('.custom-button');
    
    buttons.forEach(button => {
        // 确保元素可以获得焦点
        if (!button.hasAttribute('tabindex')) {
            button.setAttribute('tabindex', '0');
        }
        
        // 添加键盘事件支持
        button.addEventListener('keydown', function(event) {
            if (event.key === 'Enter' || event.key === ' ') {
                event.preventDefault();
                button.click();
            }
        });
        
        // 添加焦点样式
        button.addEventListener('focus', function() {
            this.classList.add('focused');
        });
        
        button.addEventListener('blur', function() {
            this.classList.remove('focused');
        });
    });
}

// 9.2 ARIA属性
function accessibilityAttributes() {
    // 为自定义组件添加ARIA属性
    const tabs = document.querySelectorAll('.tab');
    const panels = document.querySelectorAll('.tab-panel');
    
    tabs.forEach((tab, index) => {
        tab.setAttribute('role', 'tab');
        tab.setAttribute('aria-selected', 'false');
        tab.setAttribute('aria-controls', `panel-${index}`);
    });
    
    panels.forEach((panel, index) => {
        panel.setAttribute('role', 'tabpanel');
        panel.setAttribute('aria-labelledby', `tab-${index}`);
        panel.setAttribute('tabindex', '0');
        panel.setAttribute('hidden', 'true');
    });
    
    // 设置第一个选项卡为激活状态
    if (tabs.length > 0) {
        tabs[0].setAttribute('aria-selected', 'true');
        panels[0].removeAttribute('hidden');
    }
}

// ====================== 安全考虑 ======================

// 10.1 防止XSS攻击
function preventXSS() {
    // 不安全的做法：直接使用用户输入
    // element.innerHTML = userInput;
    
    // 安全的做法：转义HTML或使用textContent
    function escapeHTML(str) {
        return str.replace(/[&<>"']/g, function(match) {
            const escape = {
                '&': '&amp;',
                '<': '&lt;',
                '>': '&gt;',
                '"': '&quot;',
                "'": '&#039;'
            };
            return escape[match];
        });
    }
    
    const userInput = '<script>alert("XSS")</script>';
    element.textContent = userInput;  // 安全
    // 或者
    element.innerHTML = escapeHTML(userInput);  // 安全
}

// 10.2 内容安全策略(CSP)
// 在HTML头部添加CSP头
// <meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self' 'unsafe-inline'">