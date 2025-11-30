import java.util.*;

// 备忘录类
class Memento {
    private String state;
    
    public Memento(String state) {
        this.state = state;
    }
    
    public String getState() {
        return state;
    }
}

// 发起人类
class Originator {
    private String state;
    
    public void setState(String state) {
        this.state = state;
    }
    
    public String getState() {
        return state;
    }
    
    // 创建备忘录
    public Memento createMemento() {
        return new Memento(state);
    }
    
    // 从备忘录恢复状态
    public void restoreMemento(Memento memento) {
        this.state = memento.getState();
    }
    
    public void showState() {
        System.out.println("当前状态: " + state);
    }
}

// 管理者类
class Caretaker {
    private Memento memento;
    
    public void setMemento(Memento memento) {
        this.memento = memento;
    }
    
    public Memento getMemento() {
        return memento;
    }
}

// 文本编辑器状态备忘录
class TextEditorMemento {
    private String content;
    private int cursorPosition;
    
    public TextEditorMemento(String content, int cursorPosition) {
        this.content = content;
        this.cursorPosition = cursorPosition;
    }
    
    public String getContent() {
        return content;
    }
    
    public int getCursorPosition() {
        return cursorPosition;
    }
}

// 文本编辑器
class TextEditor {
    private String content;
    private int cursorPosition;
    
    public TextEditor() {
        this.content = "";
        this.cursorPosition = 0;
    }
    
    public void setContent(String content) {
        this.content = content;
    }
    
    public String getContent() {
        return content;
    }
    
    public void setCursorPosition(int cursorPosition) {
        this.cursorPosition = cursorPosition;
    }
    
    public int getCursorPosition() {
        return cursorPosition;
    }
    
    // 输入文本
    public void inputText(String text) {
        content = content.substring(0, cursorPosition) + text + content.substring(cursorPosition);
        cursorPosition += text.length();
    }
    
    // 删除文本
    public void deleteText(int count) {
        if (cursorPosition >= count) {
            content = content.substring(0, cursorPosition - count) + content.substring(cursorPosition);
            cursorPosition -= count;
        } else {
            content = content.substring(cursorPosition);
            cursorPosition = 0;
        }
    }
    
    // 移动光标
    public void moveCursor(int position) {
        if (position >= 0 && position <= content.length()) {
            cursorPosition = position;
        }
    }
    
    // 创建备忘录
    public TextEditorMemento createMemento() {
        return new TextEditorMemento(content, cursorPosition);
    }
    
    // 从备忘录恢复状态
    public void restoreMemento(TextEditorMemento memento) {
        this.content = memento.getContent();
        this.cursorPosition = memento.getCursorPosition();
    }
    
    public void showContent() {
        System.out.println("内容: \"" + content + "\"");
        System.out.println("光标位置: " + cursorPosition);
    }
}

// 历史记录管理器
class HistoryManager {
    private Stack<TextEditorMemento> history;
    
    public HistoryManager() {
        this.history = new Stack<>();
    }
    
    public void saveState(TextEditorMemento memento) {
        history.push(memento);
    }
    
    public TextEditorMemento undo() {
        if (!history.isEmpty()) {
            return history.pop();
        }
        return null;
    }
    
    public boolean isEmpty() {
        return history.isEmpty();
    }
}

// 游戏角色状态备忘录
class GameRoleMemento {
    private int life;
    private int magic;
    private int attack;
    private int defense;
    
    public GameRoleMemento(int life, int magic, int attack, int defense) {
        this.life = life;
        this.magic = magic;
        this.attack = attack;
        this.defense = defense;
    }
    
    public int getLife() {
        return life;
    }
    
    public int getMagic() {
        return magic;
    }
    
    public int getAttack() {
        return attack;
    }
    
    public int getDefense() {
        return defense;
    }
}

// 游戏角色类
class GameRole {
    private int life;
    private int magic;
    private int attack;
    private int defense;
    
    public GameRole() {
        this.life = 100;
        this.magic = 100;
        this.attack = 50;
        this.defense = 30;
    }
    
    // 显示角色状态
    public void displayState() {
        System.out.println("角色状态:");
        System.out.println("生命值: " + life);
        System.out.println("魔法值: " + magic);
        System.out.println("攻击力: " + attack);
        System.out.println("防御力: " + defense);
    }
    
    // 战斗
    public void fight() {
        life -= 10;
        magic -= 5;
        System.out.println("战斗后状态:");
        displayState();
    }
    
    // 使用魔法
    public void useMagic() {
        magic -= 20;
        attack += 10;
        System.out.println("使用魔法后状态:");
        displayState();
    }
    
    // 休息恢复
    public void rest() {
        life += 20;
        magic += 30;
        if (life > 100) life = 100;
        if (magic > 100) magic = 100;
        System.out.println("休息后状态:");
        displayState();
    }
    
    // 创建备忘录
    public GameRoleMemento createMemento() {
        return new GameRoleMemento(life, magic, attack, defense);
    }
    
    // 从备忘录恢复状态
    public void restoreMemento(GameRoleMemento memento) {
        this.life = memento.getLife();
        this.magic = memento.getMagic();
        this.attack = memento.getAttack();
        this.defense = memento.getDefense();
    }
    
    // 获取生命值
    public int getLife() {
        return life;
    }
}

// 存档管理器
class SaveGameManager {
    private Stack<GameRoleMemento> saves;
    
    public SaveGameManager() {
        this.saves = new Stack<>();
    }
    
    public void saveGame(GameRoleMemento memento) {
        saves.push(memento);
        System.out.println("游戏已保存");
    }
    
    public GameRoleMemento loadGame() {
        if (!saves.isEmpty()) {
            GameRoleMemento memento = saves.pop();
            System.out.println("游戏已加载");
            return memento;
        }
        System.out.println("没有可加载的存档");
        return null;
    }
}

public class Chapter18Example {
    public static void main(String[] args) {
        System.out.println("=== 备忘录模式示例 ===\n");
        
        // 1. 基本备忘录模式示例
        System.out.println("1. 基本备忘录模式示例:");
        basicMementoExample();
        
        // 2. 文本编辑器示例
        System.out.println("\n2. 文本编辑器示例:");
        textEditorExample();
        
        // 3. 游戏角色存档系统示例
        System.out.println("\n3. 游戏角色存档系统示例:");
        gameRoleSaveExample();
    }
    
    // 基本备忘录模式示例
    public static void basicMementoExample() {
        Originator originator = new Originator();
        Caretaker caretaker = new Caretaker();
        
        // 设置状态
        originator.setState("状态1");
        originator.showState();
        
        // 保存状态
        caretaker.setMemento(originator.createMemento());
        System.out.println("状态已保存");
        
        // 修改状态
        originator.setState("状态2");
        originator.showState();
        
        // 恢复状态
        originator.restoreMemento(caretaker.getMemento());
        originator.showState();
    }
    
    // 文本编辑器示例
    public static void textEditorExample() {
        TextEditor editor = new TextEditor();
        HistoryManager history = new HistoryManager();
        
        // 输入文本
        System.out.println("--- 输入文本 ---");
        editor.inputText("Hello");
        editor.showContent();
        
        // 保存状态
        history.saveState(editor.createMemento());
        System.out.println("状态已保存");
        
        // 继续输入文本
        System.out.println("\n--- 继续输入文本 ---");
        editor.inputText(" World");
        editor.showContent();
        
        // 保存状态
        history.saveState(editor.createMemento());
        System.out.println("状态已保存");
        
        // 再次输入文本
        System.out.println("\n--- 再次输入文本 ---");
        editor.inputText("!");
        editor.showContent();
        
        // 撤销操作
        System.out.println("\n--- 撤销操作 ---");
        TextEditorMemento memento = history.undo();
        if (memento != null) {
            editor.restoreMemento(memento);
            editor.showContent();
        }
        
        // 再次撤销操作
        System.out.println("\n--- 再次撤销操作 ---");
        memento = history.undo();
        if (memento != null) {
            editor.restoreMemento(memento);
            editor.showContent();
        }
    }
    
    // 游戏角色存档系统示例
    public static void gameRoleSaveExample() {
        GameRole role = new GameRole();
        SaveGameManager saveManager = new SaveGameManager();
        
        // 显示初始状态
        System.out.println("--- 初始状态 ---");
        role.displayState();
        
        // 保存游戏
        saveManager.saveGame(role.createMemento());
        
        // 进行战斗
        System.out.println("\n--- 进行战斗 ---");
        role.fight();
        
        // 使用魔法
        System.out.println("\n--- 使用魔法 ---");
        role.useMagic();
        
        // 保存游戏
        saveManager.saveGame(role.createMemento());
        
        // 继续战斗
        System.out.println("\n--- 继续战斗 ---");
        role.fight();
        role.fight();
        
        // 生命值过低，加载存档
        if (role.getLife() < 30) {
            System.out.println("\n--- 生命值过低，加载存档 ---");
            GameRoleMemento memento = saveManager.loadGame();
            if (memento != null) {
                role.restoreMemento(memento);
                role.displayState();
            }
        }
    }
}