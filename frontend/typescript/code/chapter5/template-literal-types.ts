// 模板字面量类型示例
function demonstrateTemplateLiteralTypes(): void {
    console.log("\n=== Template Literal Types Demo ===");
    
    // 基本模板字面量类型
    type EventName = `on${Capitalize<string>}`;
    
    // 使用模板字面量类型
    type ButtonEvent = `onClick` | `onDoubleClick`;
    type InputEvent = `onFocus` | `onBlur` | `onChange`;
    
    const buttonEvents: ButtonEvent[] = ["onClick", "onDoubleClick"];
    const inputEvents: InputEvent[] = ["onFocus", "onBlur", "onChange"];
    
    console.log("Button events:", buttonEvents);
    console.log("Input events:", inputEvents);
    
    // 内置字符串操作类型
    // Uppercase - 转换为大写
    type Upper = Uppercase<"hello">; // "HELLO"
    
    // Lowercase - 转换为小写
    type Lower = Lowercase<"HELLO">; // "hello"
    
    // Capitalize - 首字母大写
    type CapitalizeType = Capitalize<"hello">; // "Hello"
    
    // Uncapitalize - 首字母小写
    type UncapitalizeType = Uncapitalize<"Hello">; // "hello"
    
    // 组合使用
    type OnEventName<T extends string> = `on${Capitalize<T>}`;
    type OnClick = OnEventName<"click">; // "onClick"
    type OnFocus = OnEventName<"focus">; // "onFocus"
    
    // 使用模板字面量类型创建CSS属性
    type CSSProperties = {
        [K in keyof CSSStyleDeclaration as K extends string
            ? K extends `webkit${string}`
                ? `-${Uncapitalize<K>}`
                : K
            : never]: CSSStyleDeclaration[K];
    };
    
    // 使用模板字面量类型创建API端点
    type ApiEndpoint = `/api/${string}`;
    type UserEndpoint = ApiEndpoint & (`/users/${string}` | `/user/${number}`);
    
    const getUser: UserEndpoint = "/api/user/123";
    const getAllUsers: UserEndpoint = "/api/users";
    
    console.log("API endpoints:", { getUser, getAllUsers });
    
    // 使用模板字面量类型创建状态机类型
    type Event<T extends string> = `${T}_START` | `${T}_SUCCESS` | `${T}_ERROR`;
    type Events = Event<"FETCH_USER"> | Event<"CREATE_USER">;
    
    const fetchUserStart: Events = "FETCH_USER_START";
    const createUserSuccess: Events = "CREATE_USER_SUCCESS";
    
    console.log("Events:", { fetchUserStart, createUserSuccess });
    
    // 模板字面量类型与联合类型结合
    type Color = "red" | "green" | "blue";
    type Size = "small" | "medium" | "large";
    
    type ButtonVariant = `${Color}-${Size}`;
    
    const redSmallButton: ButtonVariant = "red-small";
    const greenLargeButton: ButtonVariant = "green-large";
    // const invalidButton: ButtonVariant = "yellow-medium"; // 错误
    
    console.log("Button variants:", { redSmallButton, greenLargeButton });
    
    // 模板字面量类型用于函数名
    interface ObjectMethods {
        [K in `get${string}`]: () => any;
        [K in `set${string}`]: (value: any) => void;
    }
    
    const obj: ObjectMethods = {
        getUser() {
            return { id: 1, name: "Alice" };
        },
        setUser(user) {
            console.log("Setting user:", user);
        },
        getSettings() {
            return { theme: "dark" };
        },
        setSettings(settings) {
            console.log("Setting settings:", settings);
        }
    };
    
    console.log("User:", obj.getUser());
    obj.setUser({ id: 2, name: "Bob" });
    
    // 高级模板字面量类型：创建类型安全的URL路由
    type RouteParams = {
        home: "";
        about: "";
        contact: "";
        user: "/user/:id";
        post: "/post/:id/comments/:commentId";
    };
    
    type ExtractRouteParams<T> = T extends `:${infer Param}/${infer Rest}`
        ? Param | ExtractRouteParams<`/${Rest}`>
        : T extends `:${infer Param}`
            ? Param
            : never;
    
    type UserRouteParams = ExtractRouteParams<RouteParams["user"]>; // "id"
    type PostRouteParams = ExtractRouteParams<RouteParams["post"]>; // "id" | "commentId"
    
    // 创建类型安全的路由函数
    type RouteFunction<T extends string> = 
        T extends `${string}:${infer Param}/${infer Rest}`
            ? (params: Record<Param, string> & Record<ExtractRouteParams<`/${Rest}`>, string>) => string
            : T extends `${string}:${infer Param}`
                ? (params: Record<Param, string>) => string
                : () => string;
    
    type Routes = {
        [K in keyof RouteParams]: RouteFunction<RouteParams[K]>;
    };
    
    const routes: Routes = {
        home: () => "/home",
        about: () => "/about",
        contact: () => "/contact",
        user: (params) => `/user/${params.id}`,
        post: (params) => `/post/${params.id}/comments/${params.commentId}`
    };
    
    console.log("Home route:", routes.home());
    console.log("User route:", routes.user({ id: "123" }));
    console.log("Post route:", routes.post({ 
        id: "456", 
        commentId: "789" 
    }));
    
    // 模板字面量类型用于类型安全的CSS类名生成
    type BEMBlock = string;
    type BEMElement = string;
    type BEMModifier = string;
    
    type BEM = 
        | `${BEMBlock}`
        | `${BEMBlock}__${BEMElement}`
        | `${BEMBlock}--${BEMModifier}`
        | `${BEMBlock}__${BEMElement}--${BEMModifier}`;
    
    function createBEM<T extends BEM>(block: T): T {
        return block;
    }
    
    const card = createBEM("card");
    const cardTitle = createBEM("card__title");
    const cardActive = createBEM("card--active");
    const cardTitleActive = createBEM("card__title--active");
    
    console.log("BEM classes:", { card, cardTitle, cardActive, cardTitleActive });
    
    // 模板字面量类型用于国际化键名
    type TranslationNamespace = "common" | "auth" | "profile";
    type TranslationKey<T extends TranslationNamespace> = 
        `${T}.${string}`;
    
    type Translations = {
        [K in TranslationKey<"common">]: string;
    } & {
        [K in TranslationKey<"auth">]: string;
    } & {
        [K in TranslationKey<"profile">]: string;
    };
    
    const translations: Translations = {
        "common.save": "Save",
        "common.cancel": "Cancel",
        "common.loading": "Loading...",
        "auth.login": "Login",
        "auth.register": "Register",
        "auth.forgotPassword": "Forgot Password",
        "profile.edit": "Edit Profile",
        "profile.save": "Save Changes",
        "profile.settings": "Settings"
    };
    
    function getTranslation<T extends TranslationNamespace>(key: TranslationKey<T>): string {
        return translations[key as TranslationKey<"common"> | TranslationKey<"auth"> | TranslationKey<"profile">];
    }
    
    console.log("Save button:", getTranslation("common.save"));
    console.log("Login button:", getTranslation("auth.login"));
    console.log("Edit profile:", getTranslation("profile.edit"));
}

demonstrateTemplateLiteralTypes();