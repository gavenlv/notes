import java.util.HashMap;
import java.util.Map;

/**
 * 第五章：建造者模式代码示例
 */

// 1. 基本建造者模式示例 - 计算机配置
class Computer {
    private String cpu;
    private String ram;
    private String storage;
    private String graphicsCard;
    private String motherboard;
    
    // 包级私有构造方法，允许同包的建造者访问
    Computer() {}
    
    // Getter方法
    public String getCpu() { return cpu; }
    public String getRam() { return ram; }
    public String getStorage() { return storage; }
    public String getGraphicsCard() { return graphicsCard; }
    public String getMotherboard() { return motherboard; }
    
    // Setter方法（包级私有，只允许同包的建造者访问）
    void setCpu(String cpu) { this.cpu = cpu; }
    void setRam(String ram) { this.ram = ram; }
    void setStorage(String storage) { this.storage = storage; }
    void setGraphicsCard(String graphicsCard) { this.graphicsCard = graphicsCard; }
    void setMotherboard(String motherboard) { this.motherboard = motherboard; }
    
    @Override
    public String toString() {
        return "Computer{" +
                "cpu='" + cpu + '\'' +
                ", ram='" + ram + '\'' +
                ", storage='" + storage + '\'' +
                ", graphicsCard='" + graphicsCard + '\'' +
                ", motherboard='" + motherboard + '\'' +
                '}';
    }
}

// 抽象建造者
abstract class ComputerBuilder {
    protected Computer computer;
    
    public ComputerBuilder() {
        this.computer = new Computer();
    }
    
    public abstract ComputerBuilder buildCpu(String cpu);
    public abstract ComputerBuilder buildRam(String ram);
    public abstract ComputerBuilder buildStorage(String storage);
    public abstract ComputerBuilder buildGraphicsCard(String graphicsCard);
    public abstract ComputerBuilder buildMotherboard(String motherboard);
    
    public Computer build() {
        return this.computer;
    }
}

// 具体建造者：游戏电脑建造者
class GamingComputerBuilder extends ComputerBuilder {
    @Override
    public ComputerBuilder buildCpu(String cpu) {
        computer.setCpu(cpu);
        return this;
    }
    
    @Override
    public ComputerBuilder buildRam(String ram) {
        computer.setRam(ram);
        return this;
    }
    
    @Override
    public ComputerBuilder buildStorage(String storage) {
        computer.setStorage(storage);
        return this;
    }
    
    @Override
    public ComputerBuilder buildGraphicsCard(String graphicsCard) {
        computer.setGraphicsCard(graphicsCard);
        return this;
    }
    
    @Override
    public ComputerBuilder buildMotherboard(String motherboard) {
        computer.setMotherboard(motherboard);
        return this;
    }
}

// 具体建造者：办公电脑建造者
class OfficeComputerBuilder extends ComputerBuilder {
    @Override
    public ComputerBuilder buildCpu(String cpu) {
        computer.setCpu(cpu);
        return this;
    }
    
    @Override
    public ComputerBuilder buildRam(String ram) {
        computer.setRam(ram);
        return this;
    }
    
    @Override
    public ComputerBuilder buildStorage(String storage) {
        computer.setStorage(storage);
        return this;
    }
    
    @Override
    public ComputerBuilder buildGraphicsCard(String graphicsCard) {
        // 办公电脑不需要独立显卡
        computer.setGraphicsCard("集成显卡");
        return this;
    }
    
    @Override
    public ComputerBuilder buildMotherboard(String motherboard) {
        computer.setMotherboard(motherboard);
        return this;
    }
}

// 指挥者
class ComputerDirector {
    public Computer constructGamingComputer(ComputerBuilder builder) {
        return builder.buildCpu("Intel i9-12900K")
                     .buildRam("32GB DDR4")
                     .buildStorage("1TB NVMe SSD")
                     .buildGraphicsCard("RTX 3080")
                     .buildMotherboard("Z690")
                     .build();
    }
    
    public Computer constructOfficeComputer(ComputerBuilder builder) {
        return builder.buildCpu("Intel i5-12400")
                     .buildRam("16GB DDR4")
                     .buildStorage("512GB SSD")
                     .buildMotherboard("B660")
                     .build();
    }
}

// 2. 链式调用的建造者模式示例
class Car {
    private String brand;
    private String model;
    private String color;
    private int doors;
    private String engine;
    private boolean gps;
    private boolean sunroof;
    
    private Car() {}
    
    // Getter方法
    public String getBrand() { return brand; }
    public String getModel() { return model; }
    public String getColor() { return color; }
    public int getDoors() { return doors; }
    public String getEngine() { return engine; }
    public boolean hasGps() { return gps; }
    public boolean hasSunroof() { return sunroof; }
    
    // 静态内部类作为建造者
    public static class Builder {
        private Car car;
        
        public Builder() {
            this.car = new Car();
        }
        
        public Builder brand(String brand) {
            car.brand = brand;
            return this;
        }
        
        public Builder model(String model) {
            car.model = model;
            return this;
        }
        
        public Builder color(String color) {
            car.color = color;
            return this;
        }
        
        public Builder doors(int doors) {
            car.doors = doors;
            return this;
        }
        
        public Builder engine(String engine) {
            car.engine = engine;
            return this;
        }
        
        public Builder gps(boolean gps) {
            car.gps = gps;
            return this;
        }
        
        public Builder sunroof(boolean sunroof) {
            car.sunroof = sunroof;
            return this;
        }
        
        public Car build() {
            // 可以在这里添加验证逻辑
            if (car.brand == null || car.model == null) {
                throw new IllegalStateException("品牌和型号是必需的");
            }
            return car;
        }
    }
    
    @Override
    public String toString() {
        return "Car{" +
                "brand='" + brand + '\'' +
                ", model='" + model + '\'' +
                ", color='" + color + '\'' +
                ", doors=" + doors +
                ", engine='" + engine + '\'' +
                ", gps=" + gps +
                ", sunroof=" + sunroof +
                '}';
    }
}

// 3. HTTP请求构建器示例
class HttpRequest {
    private String method;
    private String url;
    private Map<String, String> headers;
    private String body;
    
    private HttpRequest() {
        this.headers = new HashMap<>();
    }
    
    // Getter方法
    public String getMethod() { return method; }
    public String getUrl() { return url; }
    public Map<String, String> getHeaders() { return headers; }
    public String getBody() { return body; }
    
    public static class Builder {
        private HttpRequest request;
        
        public Builder() {
            this.request = new HttpRequest();
        }
        
        public Builder method(String method) {
            request.method = method;
            return this;
        }
        
        public Builder url(String url) {
            request.url = url;
            return this;
        }
        
        public Builder addHeader(String key, String value) {
            request.headers.put(key, value);
            return this;
        }
        
        public Builder body(String body) {
            request.body = body;
            return this;
        }
        
        public HttpRequest build() {
            if (request.method == null || request.url == null) {
                throw new IllegalStateException("HTTP方法和URL是必需的");
            }
            return request;
        }
    }
    
    @Override
    public String toString() {
        return "HttpRequest{" +
                "method='" + method + '\'' +
                ", url='" + url + '\'' +
                ", headers=" + headers +
                ", body='" + body + '\'' +
                '}';
    }
}

// 4. RequestConfig构建器示例
class RequestConfig {
    private int connectTimeout;
    private int socketTimeout;
    private boolean redirectsEnabled;
    
    private RequestConfig() {}
    
    public static class Builder {
        private RequestConfig config;
        
        public Builder() {
            this.config = new RequestConfig();
        }
        
        public Builder setConnectTimeout(int timeout) {
            config.connectTimeout = timeout;
            return this;
        }
        
        public Builder setSocketTimeout(int timeout) {
            config.socketTimeout = timeout;
            return this;
        }
        
        public Builder setRedirectsEnabled(boolean enabled) {
            config.redirectsEnabled = enabled;
            return this;
        }
        
        public RequestConfig build() {
            return config;
        }
    }
    
    // Getter方法
    public int getConnectTimeout() { return connectTimeout; }
    public int getSocketTimeout() { return socketTimeout; }
    public boolean isRedirectsEnabled() { return redirectsEnabled; }
    
    @Override
    public String toString() {
        return "RequestConfig{" +
                "connectTimeout=" + connectTimeout +
                ", socketTimeout=" + socketTimeout +
                ", redirectsEnabled=" + redirectsEnabled +
                '}';
    }
}

public class Chapter5Example {
    public static void main(String[] args) {
        System.out.println("=== 建造者模式示例 ===\n");
        
        // 1. 基本建造者模式示例
        System.out.println("1. 基本建造者模式示例：");
        ComputerDirector director = new ComputerDirector();
        
        // 构建游戏电脑
        Computer gamingComputer = director.constructGamingComputer(new GamingComputerBuilder());
        System.out.println("游戏电脑配置：" + gamingComputer);
        
        // 构建办公电脑
        Computer officeComputer = director.constructOfficeComputer(new OfficeComputerBuilder());
        System.out.println("办公电脑配置：" + officeComputer);
        System.out.println();
        
        // 2. 链式调用建造者模式示例
        System.out.println("2. 链式调用建造者模式示例：");
        Car sportsCar = new Car.Builder()
                .brand("Ferrari")
                .model("488 GTB")
                .color("Red")
                .doors(2)
                .engine("3.9L V8")
                .gps(true)
                .sunroof(true)
                .build();
        System.out.println("跑车配置：" + sportsCar);
        
        Car familyCar = new Car.Builder()
                .brand("Toyota")
                .model("Camry")
                .color("White")
                .doors(4)
                .engine("2.5L I4")
                .gps(true)
                .build();
        System.out.println("家用车配置：" + familyCar);
        System.out.println();
        
        // 3. HTTP请求构建器示例
        System.out.println("3. HTTP请求构建器示例：");
        HttpRequest request = new HttpRequest.Builder()
                .method("POST")
                .url("https://api.example.com/users")
                .addHeader("Content-Type", "application/json")
                .addHeader("Authorization", "Bearer token123")
                .body("{\"name\":\"John\",\"age\":30}")
                .build();
        System.out.println("HTTP请求：" + request);
        System.out.println();
        
        // 4. RequestConfig构建器示例
        System.out.println("4. RequestConfig构建器示例：");
        RequestConfig config = new RequestConfig.Builder()
                .setConnectTimeout(5000)
                .setSocketTimeout(10000)
                .setRedirectsEnabled(true)
                .build();
        System.out.println("请求配置：" + config);
    }
}