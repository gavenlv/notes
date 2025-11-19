// React与TypeScript集成示例

import { User } from './src/types/user.types';

/**
 * React示例类
 */
export class ReactExample {
    /**
     * 运行所有React示例
     */
    runExamples(): void {
        this.demonstrateComponentTypes();
        this.demonstrateHookTypes();
        this.demonstrateStateManagement();
        this.demonstrateEventHandling();
    }
    
    /**
     * 演示组件类型定义
     */
    private demonstrateComponentTypes(): void {
        console.log("\n1. React组件类型定义:");
        console.log(`
// 函数组件
interface UserCardProps {
    user: User;
    onEdit?: (userId: string) => void;
    onDelete?: (userId: string) => void;
}

const UserCard: React.FC<UserCardProps> = ({ user, onEdit, onDelete }) => {
    return (
        <div>
            <h3>{user.name}</h3>
            <p>{user.email}</p>
            <button onClick={() => onEdit?.(user.id)}>Edit</button>
            <button onClick={() => onDelete?.(user.id)}>Delete</button>
        </div>
    );
};

// 泛型组件
interface ListProps<T> {
    items: T[];
    renderItem: (item: T) => React.ReactNode;
    keyExtractor: (item: T) => string;
}

function List<T>({ items, renderItem, keyExtractor }: ListProps<T>) {
    return (
        <ul>
            {items.map(item => (
                <li key={keyExtractor(item)}>
                    {renderItem(item)}
                </li>
            ))}
        </ul>
    );
}
        `);
    }
    
    /**
     * 演示Hook类型定义
     */
    private demonstrateHookTypes(): void {
        console.log("\n2. React Hook类型定义:");
        console.log(`
// useState
const [user, setUser] = useState<User | null>(null);
const [loading, setLoading] = useState<boolean>(false);

// useEffect
useEffect(() => {
    const fetchUser = async () => {
        try {
            const userData = await api.getUser(userId);
            setUser(userData);
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };
    
    fetchUser();
}, [userId]);

// 自定义Hook
function useApi<T>(url: string) {
    const [data, setData] = useState<T | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(url);
                const result = await response.json() as T;
                setData(result);
            } catch (err) {
                setError(err instanceof Error ? err.message : 'Unknown error');
            } finally {
                setLoading(false);
            }
        };
        
        fetchData();
    }, [url]);
    
    return { data, loading, error };
}
        `);
    }
    
    /**
     * 演示状态管理
     */
    private demonstrateStateManagement(): void {
        console.log("\n3. 状态管理:");
        console.log(`
// Redux Toolkit
const userSlice = createSlice({
    name: 'users',
    initialState,
    reducers: {
        setCurrentUser: (state, action: PayloadAction<User | null>) => {
            state.currentUser = action.payload;
        }
    }
});

// Context API
interface UserContextType {
    currentUser: User | null;
    login: (email: string, password: string) => Promise<boolean>;
    logout: () => void;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

export const useUser = (): UserContextType => {
    const context = useContext(UserContext);
    if (!context) {
        throw new Error('useUser must be used within a UserProvider');
    }
    return context;
};
        `);
    }
    
    /**
     * 演示事件处理
     */
    private demonstrateEventHandling(): void {
        console.log("\n4. 事件处理:");
        console.log(`
// 表单事件处理
interface FormFieldProps {
    label: string;
    value: string;
    onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    error?: string;
}

const FormField: React.FC<FormFieldProps> = ({ label, value, onChange, error }) => {
    return (
        <div>
            <label>{label}</label>
            <input
                type="text"
                value={value}
                onChange={onChange}
            />
            {error && <span className="error">{error}</span>}
        </div>
    );
};

// 自定义事件
interface CustomButtonProps {
    onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
    children: React.ReactNode;
}

const CustomButton: React.FC<CustomButtonProps> = ({ onClick, children }) => {
    return (
        <button onClick={onClick}>
            {children}
        </button>
    );
};
        `);
    }
}