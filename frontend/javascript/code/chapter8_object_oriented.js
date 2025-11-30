// 原型与原型链示例
function testPrototypes() {
    // 父类
    function Animal(name) {
        this.name = name;
    }
    
    Animal.prototype.eat = function() {
        return `${this.name} 正在吃东西`;
    };
    
    // 子类
    function Dog(name, breed) {
        Animal.call(this, name);
        this.breed = breed;
    }
    
    // 设置子类的原型
    Dog.prototype = Object.create(Animal.prototype);
    Dog.prototype.constructor = Dog;
    
    // 子类特有方法
    Dog.prototype.bark = function() {
        return `${this.name} 正在汪汪叫`;
    };
    
    const myDog = new Dog("旺财", "金毛寻回犬");
    
    // 显示结果
    showResult('prototypesResult', `我的狗: ${myDog.name} (${myDog.breed})\n${myDog.eat()}\n${myDog.bark()}\n\n原型链关系:\nmyDog instanceof Dog: ${myDog instanceof Dog}\nmyDog instanceof Animal: ${myDog instanceof Animal}`);
}

// ES6类与继承示例
function testClasses() {
    // 父类
    class Vehicle {
        constructor(brand, model) {
            this.brand = brand;
            this.model = model;
            this._mileage = 0;
        }
        
        drive() {
            this._mileage += 10;
            return `驾驶 ${this.brand} ${this.model} (已行驶: ${this._mileage}公里)`;
        }
        
        get mileage() {
            return this._mileage;
        }
    }
    
    // 子类
    class Car extends Vehicle {
        constructor(brand, model, doors) {
            super(brand, model);
            this.doors = doors;
        }
        
        honk() {
            return `${this.brand} ${this.model} 响喇叭`;
        }
        
        drive() {
            const result = super.drive();
            return `${result} - 轿车行驶平稳`;
        }
    }
    
    const myCar = new Car("特斯拉", "Model 3", 4);
    
    // 显示结果
    showResult('classResult', `我的车: ${myCar.brand} ${myCar.model}\n车门数: ${myCar.doors}\n${myCar.drive()}\n${myCar.honk()}\n\n里程: ${myCar.mileage}公里\n${myCar.drive()}\n总里程: ${myCar.mileage}公里`);
}

// 电子商务系统示例
class Product {
    constructor(id, name, price, description) {
        this.id = id;
        this.name = name;
        this.price = price;
        this.description = description;
    }
    
    getDisplayInfo() {
        return {
            name: this.name,
            price: `¥${this.price.toFixed(2)}`,
            description: this.description
        };
    }
}

class ShoppingCart {
    constructor() {
        this.items = [];
    }
    
    addProduct(product, quantity = 1) {
        const existingItem = this.items.find(item => item.product.id === product.id);
        
        if (existingItem) {
            existingItem.quantity += quantity;
        } else {
            this.items.push({ product, quantity });
        }
        this.updateCartDisplay();
    }
    
    removeProduct(productId) {
        this.items = this.items.filter(item => item.product.id !== productId);
        this.updateCartDisplay();
    }
    
    getTotalPrice() {
        return this.items.reduce((total, item) => {
            return total + (item.product.price * item.quantity);
        }, 0);
    }
    
    isEmpty() {
        return this.items.length === 0;
    }
    
    clear() {
        this.items = [];
        this.updateCartDisplay();
    }
    
    updateCartDisplay() {
        const cartDetails = document.getElementById('cartDetails');
        const cartTotal = document.getElementById('cartTotal');
        
        if (this.isEmpty()) {
            cartDetails.textContent = '购物车是空的';
        } else {
            let details = '购物车内容:\n';
            this.items.forEach(item => {
                details += `${item.product.name} x ${item.quantity} = ¥${(item.product.price * item.quantity).toFixed(2)}\n`;
            });
            cartDetails.textContent = details;
        }
        
        cartTotal.textContent = `总计: ¥${this.getTotalPrice().toFixed(2)}`;
    }
}

class User {
    constructor(id, name, email) {
        this.id = id;
        this.name = name;
        this.email = email;
        this.shoppingCart = new ShoppingCart();
        this.orders = [];
    }
}

class Order {
    constructor(user, items) {
        this.id = Date.now().toString(36) + Math.random().toString(36).substr(2);
        this.userId = user.id;
        this.items = items;
        this.status = "pending";
        this.createDate = new Date();
        this.totalAmount = this.calculateTotal();
    }
    
    calculateTotal() {
        return this.items.reduce((total, item) => {
            return total + (item.product.price * item.quantity);
        }, 0);
    }
    
    complete() {
        this.status = "completed";
        this.completeDate = new Date();
    }
}

// 初始化电商系统
let currentUser;
let products = [];

function initializeECommerceSystem() {
    // 创建用户
    currentUser = new User("1", "张三", "zhangsan@example.com");
    
    // 创建产品
    products = [
        new Product("1", "笔记本电脑", 5999, "高性能笔记本电脑"),
        new Product("2", "无线鼠标", 99, "舒适的无线鼠标"),
        new Product("3", "机械键盘", 299, "专业游戏机械键盘"),
        new Product("4", "显示器", 1299, "4K高清显示器"),
        new Product("5", "耳机", 399, "降噪蓝牙耳机")
    ];
    
    // 显示产品
    const productsContainer = document.getElementById('products');
    productsContainer.innerHTML = '';
    
    products.forEach(product => {
        const productCard = document.createElement('div');
        productCard.className = 'product-card';
        
        productCard.innerHTML = `
            <div class="product-title">${product.name}</div>
            <div>${product.description}</div>
            <div class="product-price">¥${product.price.toFixed(2)}</div>
            <div>
                <input type="number" id="qty-${product.id}" min="1" value="1" style="width: 50px;">
                <button onclick="addToCart('${product.id}')">加入购物车</button>
            </div>
        `;
        
        productsContainer.appendChild(productCard);
    });
}

function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    const quantity = parseInt(document.getElementById(`qty-${productId}`).value, 10);
    
    if (product) {
        currentUser.shoppingCart.addProduct(product, quantity);
    }
}

function checkout() {
    if (currentUser.shoppingCart.isEmpty()) {
        showResult('orderList', '购物车是空的，无法结算');
        return;
    }
    
    const order = new Order(currentUser, [...currentUser.shoppingCart.items]);
    currentUser.orders.push(order);
    order.complete();
    
    currentUser.shoppingCart.clear();
    updateOrderHistory();
}

function clearCart() {
    currentUser.shoppingCart.clear();
}

function updateOrderHistory() {
    const orderList = document.getElementById('orderList');
    
    if (currentUser.orders.length === 0) {
        orderList.textContent = '暂无订单';
        return;
    }
    
    let history = '<div>';
    currentUser.orders.forEach(order => {
        history += `
            <div style="margin-bottom: 15px; padding: 10px; border: 1px solid #ddd; border-radius: 5px;">
                <div><strong>订单号:</strong> ${order.id}</div>
                <div><strong>状态:</strong> ${order.status === 'completed' ? '已完成' : '处理中'}</div>
                <div><strong>日期:</strong> ${order.createDate.toLocaleString()}</div>
                <div><strong>商品:</strong></div>
                <ul>
        `;
        
        order.items.forEach(item => {
            history += `<li>${item.product.name} x ${item.quantity}</li>`;
        });
        
        history += `
                </ul>
                <div><strong>总金额:</strong> ¥${order.totalAmount.toFixed(2)}</div>
            </div>
        `;
    });
    
    history += '</div>';
    orderList.innerHTML = history;
}

// 观察者模式示例
class Subject {
    constructor() {
        this.observers = [];
        this.messageHistory = [];
    }
    
    subscribe(observer) {
        this.observers.push(observer);
        return this.observers.length;
    }
    
    unsubscribe(observerId) {
        this.observers = this.observers.filter((_, index) => index !== observerId - 1);
    }
    
    notify(data) {
        const timestamp = new Date().toLocaleTimeString();
        this.messageHistory.push({ timestamp, message: data });
        
        this.observers.forEach(observer => {
            observer.update(data);
        });
        
        this.updateObserverDisplay();
    }
    
    updateObserverDisplay() {
        const result = document.getElementById('observerResult');
        let display = `观察者数量: ${this.observers.length}\n\n消息历史:\n`;
        
        this.messageHistory.forEach(item => {
            display += `[${item.timestamp}] ${item.message}\n`;
        });
        
        result.textContent = display;
    }
}

class Observer {
    constructor(id) {
        this.id = id;
    }
    
    update(data) {
        console.log(`观察者 ${this.id} 收到通知: ${data}`);
    }
}

// 初始化观察者系统
const messageSubject = new Subject();
let observerCounter = 0;

function addObserver() {
    const observer = new Observer(++observerCounter);
    messageSubject.subscribe(observer);
    messageSubject.notify(`新观察者 ${observer.id} 已加入`);
}

function removeObserver() {
    if (messageSubject.observers.length > 0) {
        const removedId = messageSubject.observers.length;
        messageSubject.unsubscribe(removedId);
        messageSubject.notify(`观察者 ${removedId} 已离开`);
    }
}

function publishMessage() {
    const messageInput = document.getElementById('messageInput');
    if (messageInput.value.trim()) {
        messageSubject.notify(messageInput.value);
        messageInput.value = '';
    }
}

// 简单游戏示例
class GameObject {
    constructor(x, y, width, height, color) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
        this.color = color;
        this.isActive = true;
    }
    
    render(ctx) {
        if (this.isActive) {
            ctx.fillStyle = this.color;
            ctx.fillRect(this.x, this.y, this.width, this.height);
        }
    }
    
    checkCollision(other) {
        return this.isActive && other.isActive &&
            this.x < other.x + other.width &&
            this.x + this.width > other.x &&
            this.y < other.y + other.height &&
            this.y + this.height > other.y;
    }
}

class Paddle extends GameObject {
    constructor(canvas) {
        super(canvas.width / 2 - 50, canvas.height - 30, 100, 10, '#3498db');
        this.canvas = canvas;
        this.speed = 8;
    }
    
    moveLeft() {
        this.x = Math.max(0, this.x - this.speed);
    }
    
    moveRight() {
        this.x = Math.min(this.canvas.width - this.width, this.x + this.speed);
    }
}

class Ball extends GameObject {
    constructor(canvas) {
        super(canvas.width / 2 - 5, canvas.height / 2 - 5, 10, 10, '#e74c3c');
        this.canvas = canvas;
        this.speedX = 3;
        this.speedY = -3;
        this.initialX = this.x;
        this.initialY = this.y;
    }
    
    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        
        // 边界碰撞检测
        if (this.x <= 0 || this.x >= this.canvas.width - this.width) {
            this.speedX = -this.speedX;
        }
        
        if (this.y <= 0) {
            this.speedY = -this.speedY;
        }
        
        // 底部边界检测（丢失球）
        if (this.y > this.canvas.height) {
            this.reset();
            return false; // 球丢失
        }
        
        return true; // 球仍在游戏区域内
    }
    
    reset() {
        this.x = this.initialX;
        this.y = this.initialY;
        this.speedX = 3;
        this.speedY = -3;
    }
    
    bounceOffPaddle(paddle) {
        // 计算球击中挡板的位置（0-1，0表示最左边，1表示最右边）
        const hitPos = (this.x - paddle.x) / paddle.width;
        
        // 根据击中位置调整反弹角度
        this.speedX = 8 * (hitPos - 0.5);
        this.speedY = -this.speedY;
    }
}

class Brick extends GameObject {
    constructor(x, y, width = 75, height = 20) {
        super(x, y, width, height, `hsl(${Math.random() * 360}, 70%, 50%)`);
        this.points = 10;
    }
}

class Game {
    constructor(canvasId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.isRunning = false;
        this.isPaused = false;
        this.score = 0;
        this.lives = 3;
        
        this.initializeGameObjects();
        this.setupControls();
    }
    
    initializeGameObjects() {
        this.paddle = new Paddle(this.canvas);
        this.ball = new Ball(this.canvas);
        this.bricks = [];
        
        // 创建砖块阵列
        const rows = 4;
        const cols = Math.floor(this.canvas.width / 80);
        const brickWidth = 75;
        const brickHeight = 20;
        const brickPadding = 5;
        const offsetTop = 30;
        const offsetLeft = (this.canvas.width - (cols * (brickWidth + brickPadding))) / 2;
        
        for (let r = 0; r < rows; r++) {
            for (let c = 0; c < cols; c++) {
                const x = c * (brickWidth + brickPadding) + offsetLeft;
                const y = r * (brickHeight + brickPadding) + offsetTop;
                this.bricks.push(new Brick(x, y, brickWidth, brickHeight));
            }
        }
        
        this.keys = {
            ArrowLeft: false,
            ArrowRight: false
        };
    }
    
    setupControls() {
        document.addEventListener('keydown', (e) => {
            if (this.keys.hasOwnProperty(e.key)) {
                this.keys[e.key] = true;
            }
        });
        
        document.addEventListener('keyup', (e) => {
            if (this.keys.hasOwnProperty(e.key)) {
                this.keys[e.key] = false;
            }
        });
    }
    
    update() {
        if (!this.isRunning || this.isPaused) return;
        
        // 移动挡板
        if (this.keys.ArrowLeft) {
            this.paddle.moveLeft();
        }
        if (this.keys.ArrowRight) {
            this.paddle.moveRight();
        }
        
        // 更新球
        if (!this.ball.update()) {
            // 球丢失
            this.lives--;
            this.updateGameInfo();
            
            if (this.lives <= 0) {
                this.gameOver();
            }
        }
        
        // 检测球与挡板碰撞
        if (this.ball.checkCollision(this.paddle)) {
            this.ball.bounceOffPaddle(this.paddle);
        }
        
        // 检测球与砖块碰撞
        for (const brick of this.bricks) {
            if (brick.isActive && this.ball.checkCollision(brick)) {
                brick.isActive = false;
                this.ball.speedY = -this.ball.speedY;
                this.score += brick.points;
                this.updateGameInfo();
                
                // 检查是否所有砖块都被消除
                if (this.bricks.every(brick => !brick.isActive)) {
                    this.levelComplete();
                }
            }
        }
    }
    
    render() {
        // 清空画布
        this.ctx.fillStyle = '#000';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        // 渲染游戏对象
        this.paddle.render(this.ctx);
        this.ball.render(this.ctx);
        this.bricks.forEach(brick => brick.render(this.ctx));
    }
    
    gameLoop() {
        this.update();
        this.render();
        
        if (this.isRunning) {
            requestAnimationFrame(() => this.gameLoop());
        }
    }
    
    start() {
        this.isRunning = true;
        this.isPaused = false;
        this.gameLoop();
    }
    
    pause() {
        this.isPaused = !this.isPaused;
        this.updateGameInfo();
    }
    
    reset() {
        this.isRunning = false;
        this.score = 0;
        this.lives = 3;
        this.initializeGameObjects();
        this.updateGameInfo();
        this.render();
    }
    
    gameOver() {
        this.isRunning = false;
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = 'white';
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('游戏结束', this.canvas.width / 2, this.canvas.height / 2);
        
        this.ctx.font = '24px Arial';
        this.ctx.fillText(`最终得分: ${this.score}`, this.canvas.width / 2, this.canvas.height / 2 + 50);
    }
    
    levelComplete() {
        this.isRunning = false;
        this.ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = 'white';
        this.ctx.font = '48px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.fillText('关卡完成！', this.canvas.width / 2, this.canvas.height / 2);
        
        this.ctx.font = '24px Arial';
        this.ctx.fillText(`得分: ${this.score}`, this.canvas.width / 2, this.canvas.height / 2 + 50);
    }
    
    updateGameInfo() {
        const info = document.getElementById('gameInfo');
        info.textContent = `得分: ${this.score} | 生命: ${this.lives}${this.isPaused ? ' | 已暂停' : ''}`;
    }
}

// 初始化游戏
let game;

function startGame() {
    if (!game) {
        game = new Game('gameCanvas');
    }
    game.start();
}

function pauseGame() {
    if (game) {
        game.pause();
    }
}

function resetGame() {
    if (game) {
        game.reset();
    }
}

// 辅助函数：在指定元素中显示结果
function showResult(elementId, content) {
    document.getElementById(elementId).textContent = content;
}

// 页面加载完成后初始化
window.onload = function() {
    initializeECommerceSystem();
    
    // 添加一个初始观察者
    addObserver();
};