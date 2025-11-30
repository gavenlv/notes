// Chapter14Example.java - 命令模式示例代码

// 抽象命令接口
interface Command {
    void execute();
}

// 支持撤销的命令接口
interface UndoableCommand extends Command {
    void undo();
}

// 接收者类
class Receiver {
    public void action() {
        System.out.println("执行具体操作");
    }
}

// 具体命令类
class ConcreteCommand implements Command {
    private Receiver receiver;
    
    public ConcreteCommand(Receiver receiver) {
        this.receiver = receiver;
    }
    
    @Override
    public void execute() {
        receiver.action();
    }
}

// 调用者类
class Invoker {
    private Command command;
    
    public void setCommand(Command command) {
        this.command = command;
    }
    
    public void call() {
        command.execute();
    }
}

// 文本编辑器接收者
class TextEditor {
    private StringBuilder text = new StringBuilder();
    
    public void append(String str) {
        text.append(str);
        System.out.println("文本已追加: " + str);
    }
    
    public void delete(int start, int end) {
        String deleted = text.substring(start, end);
        text.delete(start, end);
        System.out.println("文本已删除: " + deleted);
    }
    
    public String getText() {
        return text.toString();
    }
    
    public int length() {
        return text.length();
    }
}

// 追加文本命令
class AppendTextCommand implements UndoableCommand {
    private TextEditor editor;
    private String text;
    private int startPosition;
    
    public AppendTextCommand(TextEditor editor, String text) {
        this.editor = editor;
        this.text = text;
    }
    
    @Override
    public void execute() {
        startPosition = editor.length();
        editor.append(text);
    }
    
    @Override
    public void undo() {
        editor.delete(startPosition, startPosition + text.length());
    }
}

// 删除文本命令
class DeleteTextCommand implements UndoableCommand {
    private TextEditor editor;
    private String deletedText;
    private int startPosition;
    private int endPosition;
    
    public DeleteTextCommand(TextEditor editor, int start, int end) {
        this.editor = editor;
        this.startPosition = start;
        this.endPosition = end;
    }
    
    @Override
    public void execute() {
        deletedText = editor.getText().substring(startPosition, endPosition);
        editor.delete(startPosition, endPosition);
    }
    
    @Override
    public void undo() {
        editor.append(deletedText);
    }
}

// 电器接口
interface Appliance {
    void on();
    void off();
}

// 电视类
class Television implements Appliance {
    @Override
    public void on() {
        System.out.println("电视机已打开");
    }
    
    @Override
    public void off() {
        System.out.println("电视机已关闭");
    }
}

// 音响类
class Stereo implements Appliance {
    @Override
    public void on() {
        System.out.println("音响已打开");
    }
    
    @Override
    public void off() {
        System.out.println("音响已关闭");
    }
}

// 打开电器命令
class TurnOnCommand implements Command {
    private Appliance appliance;
    
    public TurnOnCommand(Appliance appliance) {
        this.appliance = appliance;
    }
    
    @Override
    public void execute() {
        appliance.on();
    }
}

// 关闭电器命令
class TurnOffCommand implements Command {
    private Appliance appliance;
    
    public TurnOffCommand(Appliance appliance) {
        this.appliance = appliance;
    }
    
    @Override
    public void execute() {
        appliance.off();
    }
}

// 遥控器类
class RemoteControl {
    private Command[] onCommands;
    private Command[] offCommands;
    
    public RemoteControl() {
        onCommands = new Command[5];
        offCommands = new Command[5];
        
        Command noCommand = new Command() {
            public void execute() {
                System.out.println("空命令");
            }
        };
        
        for (int i = 0; i < 5; i++) {
            onCommands[i] = noCommand;
            offCommands[i] = noCommand;
        }
    }
    
    public void setCommand(int slot, Command onCommand, Command offCommand) {
        onCommands[slot] = onCommand;
        offCommands[slot] = offCommand;
    }
    
    public void onButtonWasPushed(int slot) {
        onCommands[slot].execute();
    }
    
    public void offButtonWasPushed(int slot) {
        offCommands[slot].execute();
    }
    
    public void showCommands() {
        System.out.println("------- 遥控器 -------");
        for (int i = 0; i < onCommands.length; i++) {
            System.out.println("[slot " + i + "] " + 
                onCommands[i].getClass().getSimpleName() + "  " + 
                offCommands[i].getClass().getSimpleName());
        }
    }
}

// 计算器类（接收者）
class Calculator {
    private double currentValue = 0;
    
    public void add(double value) {
        currentValue += value;
        System.out.println("加上 " + value + "，结果为: " + currentValue);
    }
    
    public void subtract(double value) {
        currentValue -= value;
        System.out.println("减去 " + value + "，结果为: " + currentValue);
    }
    
    public void multiply(double value) {
        currentValue *= value;
        System.out.println("乘以 " + value + "，结果为: " + currentValue);
    }
    
    public void divide(double value) {
        if (value != 0) {
            currentValue /= value;
            System.out.println("除以 " + value + "，结果为: " + currentValue);
        } else {
            System.out.println("除数不能为零");
        }
    }
    
    public double getCurrentValue() {
        return currentValue;
    }
    
    public void setCurrentValue(double value) {
        this.currentValue = value;
    }
}

// 抽象计算器命令
abstract class CalculatorCommand implements UndoableCommand {
    protected Calculator calculator;
    protected double value;
    
    public CalculatorCommand(Calculator calculator, double value) {
        this.calculator = calculator;
        this.value = value;
    }
}

// 加法命令
class AddCommand extends CalculatorCommand {
    private double previousValue;
    
    public AddCommand(Calculator calculator, double value) {
        super(calculator, value);
    }
    
    @Override
    public void execute() {
        previousValue = calculator.getCurrentValue();
        calculator.add(value);
    }
    
    @Override
    public void undo() {
        calculator.setCurrentValue(previousValue);
    }
}

// 减法命令
class SubtractCommand extends CalculatorCommand {
    private double previousValue;
    
    public SubtractCommand(Calculator calculator, double value) {
        super(calculator, value);
    }
    
    @Override
    public void execute() {
        previousValue = calculator.getCurrentValue();
        calculator.subtract(value);
    }
    
    @Override
    public void undo() {
        calculator.setCurrentValue(previousValue);
    }
}

// 乘法命令
class MultiplyCommand extends CalculatorCommand {
    private double previousValue;
    
    public MultiplyCommand(Calculator calculator, double value) {
        super(calculator, value);
    }
    
    @Override
    public void execute() {
        previousValue = calculator.getCurrentValue();
        calculator.multiply(value);
    }
    
    @Override
    public void undo() {
        calculator.setCurrentValue(previousValue);
    }
}

// 除法命令
class DivideCommand extends CalculatorCommand {
    private double previousValue;
    
    public DivideCommand(Calculator calculator, double value) {
        super(calculator, value);
    }
    
    @Override
    public void execute() {
        previousValue = calculator.getCurrentValue();
        calculator.divide(value);
    }
    
    @Override
    public void undo() {
        calculator.setCurrentValue(previousValue);
    }
}

// 计算器调用者
class CalculatorInvoker {
    private java.util.Stack<UndoableCommand> commandHistory = new java.util.Stack<>();
    
    public void executeCommand(UndoableCommand command) {
        command.execute();
        commandHistory.push(command);
    }
    
    public void undo() {
        if (!commandHistory.isEmpty()) {
            UndoableCommand command = commandHistory.pop();
            command.undo();
            System.out.println("执行撤销操作");
        } else {
            System.out.println("没有可撤销的操作");
        }
    }
    
    public void redo() {
        // 简化实现，实际应用中需要保存redo历史
        System.out.println("执行重做操作");
    }
    
    public boolean hasCommands() {
        return !commandHistory.isEmpty();
    }
}

// 宏命令类
class MacroCommand implements Command {
    private java.util.List<Command> commands;
    
    public MacroCommand() {
        commands = new java.util.ArrayList<>();
    }
    
    public void addCommand(Command command) {
        commands.add(command);
    }
    
    public void removeCommand(Command command) {
        commands.remove(command);
    }
    
    @Override
    public void execute() {
        System.out.println("执行宏命令:");
        for (Command command : commands) {
            command.execute();
        }
    }
}

// 启动系统命令
class StartSystemCommand implements Command {
    @Override
    public void execute() {
        System.out.println("启动系统...");
    }
}

// 打开网络连接命令
class OpenNetworkCommand implements Command {
    @Override
    public void execute() {
        System.out.println("打开网络连接...");
    }
}

// 启动应用程序命令
class StartApplicationCommand implements Command {
    private String appName;
    
    public StartApplicationCommand(String appName) {
        this.appName = appName;
    }
    
    @Override
    public void execute() {
        System.out.println("启动应用程序: " + appName);
    }
}

// 主类 - 演示命令模式
public class Chapter14Example {
    public static void main(String[] args) {
        System.out.println("=== 第十四章 命令模式示例 ===\n");
        
        // 示例1: 基本命令模式
        System.out.println("1. 基本命令模式示例:");
        Receiver receiver = new Receiver();
        Command command = new ConcreteCommand(receiver);
        Invoker invoker = new Invoker();
        
        invoker.setCommand(command);
        invoker.call();
        System.out.println();
        
        // 示例2: 文本编辑器命令（支持撤销）
        System.out.println("2. 文本编辑器命令示例:");
        TextEditor editor = new TextEditor();
        UndoableCommand appendCmd1 = new AppendTextCommand(editor, "Hello ");
        UndoableCommand appendCmd2 = new AppendTextCommand(editor, "World!");
        
        appendCmd1.execute();
        appendCmd2.execute();
        System.out.println("当前文本: " + editor.getText());
        
        // 撤销操作
        ((AppendTextCommand)appendCmd2).undo();
        System.out.println("撤销后文本: " + editor.getText());
        System.out.println();
        
        // 示例3: 遥控器系统
        System.out.println("3. 遥控器系统示例:");
        RemoteControl remote = new RemoteControl();
        
        Television tv = new Television();
        Stereo stereo = new Stereo();
        
        Command tvOn = new TurnOnCommand(tv);
        Command tvOff = new TurnOffCommand(tv);
        Command stereoOn = new TurnOnCommand(stereo);
        Command stereoOff = new TurnOffCommand(stereo);
        
        remote.setCommand(0, tvOn, tvOff);
        remote.setCommand(1, stereoOn, stereoOff);
        
        remote.showCommands();
        System.out.println("--- 测试遥控器 ---");
        remote.onButtonWasPushed(0);
        remote.offButtonWasPushed(0);
        remote.onButtonWasPushed(1);
        remote.offButtonWasPushed(1);
        remote.onButtonWasPushed(2); // 空命令测试
        System.out.println();
        
        // 示例4: 计算器命令系统（支持撤销）
        System.out.println("4. 计算器命令系统示例:");
        Calculator calc = new Calculator();
        CalculatorInvoker calcInvoker = new CalculatorInvoker();
        
        // 执行一系列计算操作
        calcInvoker.executeCommand(new AddCommand(calc, 10));
        calcInvoker.executeCommand(new SubtractCommand(calc, 5));
        calcInvoker.executeCommand(new MultiplyCommand(calc, 3));
        calcInvoker.executeCommand(new DivideCommand(calc, 2));
        
        System.out.println("最终结果: " + calc.getCurrentValue());
        
        // 撤销操作
        while (calcInvoker.hasCommands()) {
            calcInvoker.undo();
            System.out.println("撤销后结果: " + calc.getCurrentValue());
        }
        System.out.println();
        
        // 示例5: 宏命令系统
        System.out.println("5. 宏命令系统示例:");
        MacroCommand macro = new MacroCommand();
        macro.addCommand(new StartSystemCommand());
        macro.addCommand(new OpenNetworkCommand());
        macro.addCommand(new StartApplicationCommand("文本编辑器"));
        macro.addCommand(new StartApplicationCommand("浏览器"));
        
        macro.execute();
    }
}