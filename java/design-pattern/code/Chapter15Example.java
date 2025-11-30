import java.util.*;

// 抽象表达式接口
interface Expression {
    boolean interpret(String context);
}

// 终结符表达式 - 终端符号
class TerminalExpression implements Expression {
    private String data;
    
    public TerminalExpression(String data) {
        this.data = data;
    }
    
    @Override
    public boolean interpret(String context) {
        return context.contains(data);
    }
}

// 非终结符表达式 - 或操作
class OrExpression implements Expression {
    private Expression expr1;
    private Expression expr2;
    
    public OrExpression(Expression expr1, Expression expr2) {
        this.expr1 = expr1;
        this.expr2 = expr2;
    }
    
    @Override
    public boolean interpret(String context) {
        return expr1.interpret(context) || expr2.interpret(context);
    }
}

// 非终结符表达式 - 与操作
class AndExpression implements Expression {
    private Expression expr1;
    private Expression expr2;
    
    public AndExpression(Expression expr1, Expression expr2) {
        this.expr1 = expr1;
        this.expr2 = expr2;
    }
    
    @Override
    public boolean interpret(String context) {
        return expr1.interpret(context) && expr2.interpret(context);
    }
}

// 表达式接口
interface MathematicalExpression {
    int interpret();
}

// 数字表达式（终结符）
class NumberExpression implements MathematicalExpression {
    private int number;
    
    public NumberExpression(int number) {
        this.number = number;
    }
    
    @Override
    public int interpret() {
        return number;
    }
}

// 加法表达式（非终结符）
class AddExpression implements MathematicalExpression {
    private MathematicalExpression leftExpression;
    private MathematicalExpression rightExpression;
    
    public AddExpression(MathematicalExpression left, MathematicalExpression right) {
        this.leftExpression = left;
        this.rightExpression = right;
    }
    
    @Override
    public int interpret() {
        return leftExpression.interpret() + rightExpression.interpret();
    }
}

// 减法表达式（非终结符）
class SubtractExpression implements MathematicalExpression {
    private MathematicalExpression leftExpression;
    private MathematicalExpression rightExpression;
    
    public SubtractExpression(MathematicalExpression left, MathematicalExpression right) {
        this.leftExpression = left;
        this.rightExpression = right;
    }
    
    @Override
    public int interpret() {
        return leftExpression.interpret() - rightExpression.interpret();
    }
}

// 乘法表达式（非终结符）
class MultiplyExpression implements MathematicalExpression {
    private MathematicalExpression leftExpression;
    private MathematicalExpression rightExpression;
    
    public MultiplyExpression(MathematicalExpression left, MathematicalExpression right) {
        this.leftExpression = left;
        this.rightExpression = right;
    }
    
    @Override
    public int interpret() {
        return leftExpression.interpret() * rightExpression.interpret();
    }
}

// 除法表达式（非终结符）
class DivideExpression implements MathematicalExpression {
    private MathematicalExpression leftExpression;
    private MathematicalExpression rightExpression;
    
    public DivideExpression(MathematicalExpression left, MathematicalExpression right) {
        this.leftExpression = left;
        this.rightExpression = right;
    }
    
    @Override
    public int interpret() {
        int divisor = rightExpression.interpret();
        if (divisor == 0) {
            throw new ArithmeticException("Division by zero");
        }
        return leftExpression.interpret() / divisor;
    }
}

// 表达式解析器
class ExpressionParser {
    private Stack<MathematicalExpression> stack = new Stack<>();
    
    public int parse(String expression) {
        String[] tokens = expression.split(" ");
        
        for (String token : tokens) {
            if (isOperator(token)) {
                MathematicalExpression right = stack.pop();
                MathematicalExpression left = stack.pop();
                
                switch (token) {
                    case "+":
                        stack.push(new AddExpression(left, right));
                        break;
                    case "-":
                        stack.push(new SubtractExpression(left, right));
                        break;
                    case "*":
                        stack.push(new MultiplyExpression(left, right));
                        break;
                    case "/":
                        stack.push(new DivideExpression(left, right));
                        break;
                }
            } else {
                stack.push(new NumberExpression(Integer.parseInt(token)));
            }
        }
        
        return stack.pop().interpret();
    }
    
    private boolean isOperator(String token) {
        return "+".equals(token) || "-".equals(token) || 
               "*".equals(token) || "/".equals(token);
    }
}

// 布尔表达式上下文
class BooleanContext {
    private Map<String, Boolean> variables = new HashMap<>();
    
    public void assign(String variable, Boolean value) {
        variables.put(variable, value);
    }
    
    public Boolean lookup(String variable) {
        return variables.get(variable);
    }
}

// 布尔表达式接口
interface BooleanExpression {
    boolean interpret(BooleanContext context);
}

// 变量表达式（终结符）
class VariableExpression implements BooleanExpression {
    private String name;
    
    public VariableExpression(String name) {
        this.name = name;
    }
    
    @Override
    public boolean interpret(BooleanContext context) {
        return context.lookup(name);
    }
}

// 常量表达式（终结符）
class ConstantExpression implements BooleanExpression {
    private boolean value;
    
    public ConstantExpression(boolean value) {
        this.value = value;
    }
    
    @Override
    public boolean interpret(BooleanContext context) {
        return value;
    }
}

// 与表达式（非终结符）
class AndBooleanExpression implements BooleanExpression {
    private BooleanExpression left;
    private BooleanExpression right;
    
    public AndBooleanExpression(BooleanExpression left, BooleanExpression right) {
        this.left = left;
        this.right = right;
    }
    
    @Override
    public boolean interpret(BooleanContext context) {
        return left.interpret(context) && right.interpret(context);
    }
}

// 或表达式（非终结符）
class OrBooleanExpression implements BooleanExpression {
    private BooleanExpression left;
    private BooleanExpression right;
    
    public OrBooleanExpression(BooleanExpression left, BooleanExpression right) {
        this.left = left;
        this.right = right;
    }
    
    @Override
    public boolean interpret(BooleanContext context) {
        return left.interpret(context) || right.interpret(context);
    }
}

// 非表达式（非终结符）
class NotBooleanExpression implements BooleanExpression {
    private BooleanExpression expression;
    
    public NotBooleanExpression(BooleanExpression expression) {
        this.expression = expression;
    }
    
    @Override
    public boolean interpret(BooleanContext context) {
        return !expression.interpret(context);
    }
}

// 规则上下文
class RuleContext {
    private Map<String, Object> attributes = new HashMap<>();
    
    public void setAttribute(String key, Object value) {
        attributes.put(key, value);
    }
    
    public Object getAttribute(String key) {
        return attributes.get(key);
    }
    
    public boolean hasAttribute(String key) {
        return attributes.containsKey(key);
    }
}

// 规则表达式接口
interface RuleExpression {
    boolean evaluate(RuleContext context);
}

// 属性存在规则（终结符）
class AttributeExistsRule implements RuleExpression {
    private String attributeName;
    
    public AttributeExistsRule(String attributeName) {
        this.attributeName = attributeName;
    }
    
    @Override
    public boolean evaluate(RuleContext context) {
        return context.hasAttribute(attributeName);
    }
}

// 属性值等于规则（终结符）
class AttributeEqualsRule implements RuleExpression {
    private String attributeName;
    private Object expectedValue;
    
    public AttributeEqualsRule(String attributeName, Object expectedValue) {
        this.attributeName = attributeName;
        this.expectedValue = expectedValue;
    }
    
    @Override
    public boolean evaluate(RuleContext context) {
        if (!context.hasAttribute(attributeName)) {
            return false;
        }
        Object actualValue = context.getAttribute(attributeName);
        return expectedValue.equals(actualValue);
    }
}

// 属性值大于规则（终结符）
class AttributeGreaterThanRule implements RuleExpression {
    private String attributeName;
    private Comparable expectedValue;
    
    public AttributeGreaterThanRule(String attributeName, Comparable expectedValue) {
        this.attributeName = attributeName;
        this.expectedValue = expectedValue;
    }
    
    @Override
    public boolean evaluate(RuleContext context) {
        if (!context.hasAttribute(attributeName)) {
            return false;
        }
        Object actualValue = context.getAttribute(attributeName);
        if (!(actualValue instanceof Comparable)) {
            return false;
        }
        return ((Comparable) actualValue).compareTo(expectedValue) > 0;
    }
}

// 与规则（非终结符）
class AndRule implements RuleExpression {
    private List<RuleExpression> rules;
    
    public AndRule() {
        this.rules = new ArrayList<>();
    }
    
    public AndRule addRule(RuleExpression rule) {
        rules.add(rule);
        return this;
    }
    
    @Override
    public boolean evaluate(RuleContext context) {
        for (RuleExpression rule : rules) {
            if (!rule.evaluate(context)) {
                return false;
            }
        }
        return true;
    }
}

// 或规则（非终结符）
class OrRule implements RuleExpression {
    private List<RuleExpression> rules;
    
    public OrRule() {
        this.rules = new ArrayList<>();
    }
    
    public OrRule addRule(RuleExpression rule) {
        rules.add(rule);
        return this;
    }
    
    @Override
    public boolean evaluate(RuleContext context) {
        for (RuleExpression rule : rules) {
            if (rule.evaluate(context)) {
                return true;
            }
        }
        return false;
    }
}

// 非规则（非终结符）
class NotRule implements RuleExpression {
    private RuleExpression rule;
    
    public NotRule(RuleExpression rule) {
        this.rule = rule;
    }
    
    @Override
    public boolean evaluate(RuleContext context) {
        return !rule.evaluate(context);
    }
}

public class Chapter15Example {
    public static void main(String[] args) {
        System.out.println("=== 解释器模式示例 ===\n");
        
        // 1. 基本表达式解释器示例
        System.out.println("1. 基本表达式解释器:");
        basicExpressionExample();
        
        // 2. 数学表达式解释器示例
        System.out.println("\n2. 数学表达式解释器:");
        mathematicalExpressionExample();
        
        // 3. 布尔表达式解释器示例
        System.out.println("\n3. 布尔表达式解释器:");
        booleanExpressionExample();
        
        // 4. 规则引擎解释器示例
        System.out.println("\n4. 规则引擎解释器:");
        ruleEngineExample();
    }
    
    // 基本表达式解释器示例
    public static void basicExpressionExample() {
        Expression robert = new TerminalExpression("Robert");
        Expression john = new TerminalExpression("John");
        Expression isMale = new OrExpression(robert, john);
        
        Expression julie = new TerminalExpression("Julie");
        Expression married = new TerminalExpression("Married");
        Expression isMarriedWoman = new AndExpression(julie, married);
        
        System.out.println("John is male? " + isMale.interpret("John"));
        System.out.println("Julie is a married women? " + isMarriedWoman.interpret("Married Julie"));
        System.out.println("Robert is male? " + isMale.interpret("Robert"));
    }
    
    // 数学表达式解释器示例
    public static void mathematicalExpressionExample() {
        ExpressionParser parser = new ExpressionParser();
        
        // 计算: (10 + 5) * 2 - 8 / 4
        // 后缀表达式: 10 5 + 2 * 8 4 / -
        String expression1 = "10 5 + 2 * 8 4 / -";
        int result1 = parser.parse(expression1);
        System.out.println("(10 + 5) * 2 - 8 / 4 = " + result1);
        
        // 计算: 20 / 4 + 3 * 2
        // 后缀表达式: 20 4 / 3 2 * +
        String expression2 = "20 4 / 3 2 * +";
        int result2 = parser.parse(expression2);
        System.out.println("20 / 4 + 3 * 2 = " + result2);
    }
    
    // 布尔表达式解释器示例
    public static void booleanExpressionExample() {
        // 创建变量表达式
        BooleanExpression x = new VariableExpression("x");
        BooleanExpression y = new VariableExpression("y");
        
        // 创建复合表达式: (x AND y) OR (NOT x)
        BooleanExpression notX = new NotBooleanExpression(x);
        BooleanExpression xAndY = new AndBooleanExpression(x, y);
        BooleanExpression complexExpression = new OrBooleanExpression(xAndY, notX);
        
        // 创建上下文并赋值
        BooleanContext context1 = new BooleanContext();
        context1.assign("x", true);
        context1.assign("y", false);
        
        BooleanContext context2 = new BooleanContext();
        context2.assign("x", false);
        context2.assign("y", true);
        
        System.out.println("Context1 (x=true, y=false): " + complexExpression.interpret(context1));
        System.out.println("Context2 (x=false, y=true): " + complexExpression.interpret(context2));
    }
    
    // 规则引擎解释器示例
    public static void ruleEngineExample() {
        // 创建规则: 年龄大于18并且有驾照
        RuleExpression ageRule = new AttributeGreaterThanRule("age", 18);
        RuleExpression licenseRule = new AttributeExistsRule("license");
        RuleExpression drivingRule = new AndRule()
            .addRule(ageRule)
            .addRule(licenseRule);
        
        // 测试数据1: 符合条件
        RuleContext context1 = new RuleContext();
        context1.setAttribute("age", 25);
        context1.setAttribute("license", "valid");
        
        // 测试数据2: 不符合条件
        RuleContext context2 = new RuleContext();
        context2.setAttribute("age", 16);
        context2.setAttribute("license", "valid");
        
        System.out.println("Person1 (age=25, license=valid) can drive: " + drivingRule.evaluate(context1));
        System.out.println("Person2 (age=16, license=valid) can drive: " + drivingRule.evaluate(context2));
    }
}