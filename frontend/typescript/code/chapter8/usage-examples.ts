// 使用声明文件的示例

// 引入类型定义
import { User, UserRole, Status, Repository, ApiResponse } from './type-definitions';

// 使用全局声明
console.log(`App version: ${APP_VERSION}`);
console.log(`API URL: ${API_BASE_URL}`);

// 使用全局函数
logMessage('info', 'Application started', { version: APP_VERSION });
const now = new Date();
const formattedDate = formatDate(now);
console.log(`Current date: ${formattedDate}`);

// 使用全局接口
const user: User = {
    id: '123',
    name: 'John Doe',
    email: 'john@example.com',
    role: 'admin',
    status: 'active',
    profile: {
        bio: 'Software Developer',
        website: 'https://johndoe.com',
        location: 'San Francisco'
    },
    preferences: {
        theme: 'dark',
        language: 'en',
        notifications: true
    },
    createdAt: new Date(),
    updatedAt: new Date(),
    avatar: 'https://example.com/avatar.jpg'
};

// 使用全局类
const storage = new Storage('app-data');
storage.setItem('lastLogin', new Date().toISOString());
const lastLogin = storage.getItem('lastLogin');

// 使用模块声明
import * as MyLibrary from 'my-library';
MyLibrary.initialize();
const result = MyLibrary.process(user);
console.log(`Library version: ${MyLibrary.version}`);

// 使用通配符模块声明
import config from './config.json';
import styles from './styles.css';
const theme = styles.dark;

// 使用类型别名
type UserStatus = Status;
type AdminRole = Extract<UserRole, 'admin'>;

// 使用泛型接口
interface UserRepository extends Repository<User> {}

// 使用条件类型
type UserResponse = ApiResponse<User>;
type StringResponse = ApiResponse<string>;

// 创建使用类型定义的类
class UserService {
    private userRepository: UserRepository;
    
    constructor(userRepository: UserRepository) {
        this.userRepository = userRepository;
    }
    
    async createUser(userData: Omit<User, 'id' | 'createdAt' | 'updatedAt'>): Promise<User> {
        const user = {
            ...userData,
            id: this.generateId(),
            createdAt: new Date(),
            updatedAt: new Date()
        };
        
        return this.userRepository.create(user);
    }
    
    async getUserById(id: string): Promise<User | null> {
        return this.userRepository.findById(id);
    }
    
    async updateUser(id: string, updates: Partial<User>): Promise<User> {
        const existingUser = await this.getUserById(id);
        if (!existingUser) {
            throw new Error(`User with id ${id} not found`);
        }
        
        const updatedUser = {
            ...existingUser,
            ...updates,
            updatedAt: new Date()
        };
        
        return this.userRepository.update(id, updatedUser);
    }
    
    async deleteUser(id: string): Promise<boolean> {
        return this.userRepository.delete(id);
    }
    
    async findUsers(limit: number = 10, offset: number = 0): Promise<User[]> {
        return this.userRepository.findMany({ limit, offset });
    }
    
    private generateId(): string {
        return Math.random().toString(36).substring(2, 9);
    }
}

// 使用类型守卫
function isUser(obj: any): obj is User {
    return obj && 
           typeof obj.id === 'string' &&
           typeof obj.name === 'string' &&
           typeof obj.email === 'string' &&
           ['admin', 'editor', 'viewer'].includes(obj.role) &&
           ['active', 'inactive', 'pending', 'archived'].includes(obj.status);
}

// 处理未知类型的数据
function processUserData(data: unknown): User {
    if (isUser(data)) {
        return data;
    }
    
    throw new Error('Invalid user data');
}

// 使用声明合并
const calculation = new Calculation();
const result = calculation.add(5).multiply(3).subtract(2).getResult();
console.log(`Calculation result: ${result}`);

// 使用扩展的Express类型（示例）
function expressRequestHandler(req: any, res: any) {
    // 假设这里有Express的请求和响应对象
    // 我们可以使用扩展的类型
    
    if (req.user) {
        console.log(`User ${req.user.id} with role ${req.user.role} is making a request`);
    }
    
    if (req.pagination) {
        console.log(`Pagination: page ${req.pagination.page}, limit ${req.pagination.limit}`);
    }
    
    // 使用扩展的响应方法
    res.success({ message: 'Request processed successfully' });
}

// 使用扩展的全局对象
window.gtag('config', 'GA_MEASUREMENT_ID', { page_path: '/home' });
window.analytics.track('button_click', { button_id: 'submit' });

if (window.ENVIRONMENT === 'development') {
    console.log('Running in development mode');
}

// 使用NodeJS扩展
const dbConfig = {
    host: process.env.DB_HOST,
    port: parseInt(process.env.DB_PORT || '5432'),
    database: process.env.DB_NAME,
    username: process.env.DB_USER,
    password: process.env.DB_PASSWORD,
    ssl: process.env.NODE_ENV === 'production'
};

// 使用导入类型减少编译负载
type EventCallback = (event: string, data: any) => void;
type DeepPartialUser = DeepPartial<User>;

// 示例：创建一个部分用户对象
const partialUser: DeepPartialUser = {
    name: 'Jane Doe',
    email: 'jane@example.com',
    profile: {
        bio: 'Frontend Developer'
    }
};

// 导出所有示例函数和类供测试
export { UserService, isUser, processUserData, expressRequestHandler, partialUser };