/**
 * 第七章：适配器模式代码示例
 */

// 1. 基本适配器模式示例 - 媒体播放器
// 目标接口
interface MediaPlayer {
    void play(String audioType, String fileName);
}

// 高级媒体播放器接口
interface AdvancedMediaPlayer {
    void playVlc(String fileName);
    void playMp4(String fileName);
}

// 适配者类 - VLC播放器
class VlcPlayer implements AdvancedMediaPlayer {
    @Override
    public void playVlc(String fileName) {
        System.out.println("Playing vlc file. Name: " + fileName);
    }
    
    @Override
    public void playMp4(String fileName) {
        // 不支持MP4格式
    }
}

// 适配者类 - MP4播放器
class Mp4Player implements AdvancedMediaPlayer {
    @Override
    public void playVlc(String fileName) {
        // 不支持VLC格式
    }
    
    @Override
    public void playMp4(String fileName) {
        System.out.println("Playing mp4 file. Name: " + fileName);
    }
}

// 类适配器 - 继承适配者类并实现目标接口
class MediaAdapter extends VlcPlayer implements MediaPlayer {
    AdvancedMediaPlayer advancedMusicPlayer;
    
    public MediaAdapter(String audioType) {
        if (audioType.equalsIgnoreCase("vlc")) {
            advancedMusicPlayer = new VlcPlayer();
        } else if (audioType.equalsIgnoreCase("mp4")) {
            advancedMusicPlayer = new Mp4Player();
        }
    }
    
    @Override
    public void play(String audioType, String fileName) {
        if (audioType.equalsIgnoreCase("vlc")) {
            advancedMusicPlayer.playVlc(fileName);
        } else if (audioType.equalsIgnoreCase("mp4")) {
            advancedMusicPlayer.playMp4(fileName);
        }
    }
}

// 客户端类
class AudioPlayer implements MediaPlayer {
    MediaAdapter mediaAdapter;
    
    @Override
    public void play(String audioType, String fileName) {
        // 播放mp3音乐文件的内置支持
        if (audioType.equalsIgnoreCase("mp3")) {
            System.out.println("Playing mp3 file. Name: " + fileName);
        }
        // mediaAdapter提供了播放其他文件格式的支持
        else if (audioType.equalsIgnoreCase("vlc") || audioType.equalsIgnoreCase("mp4")) {
            mediaAdapter = new MediaAdapter(audioType);
            mediaAdapter.play(audioType, fileName);
        } else {
            System.out.println("Invalid media. " + audioType + " format not supported");
        }
    }
}

// 2. 对象适配器模式
// 对象适配器 - 持有适配者类的实例
class MediaAdapterObject implements MediaPlayer {
    AdvancedMediaPlayer advancedMusicPlayer;
    
    public MediaAdapterObject(String audioType) {
        if (audioType.equalsIgnoreCase("vlc")) {
            advancedMusicPlayer = new VlcPlayer();
        } else if (audioType.equalsIgnoreCase("mp4")) {
            advancedMusicPlayer = new Mp4Player();
        }
    }
    
    @Override
    public void play(String audioType, String fileName) {
        if (audioType.equalsIgnoreCase("vlc")) {
            advancedMusicPlayer.playVlc(fileName);
        } else if (audioType.equalsIgnoreCase("mp4")) {
            advancedMusicPlayer.playMp4(fileName);
        }
    }
}

// 使用对象适配器的音频播放器
class AudioPlayerWithObjectAdapter implements MediaPlayer {
    MediaAdapterObject mediaAdapter;
    
    @Override
    public void play(String audioType, String fileName) {
        // 播放mp3音乐文件的内置支持
        if (audioType.equalsIgnoreCase("mp3")) {
            System.out.println("Playing mp3 file. Name: " + fileName);
        }
        // mediaAdapter提供了播放其他文件格式的支持
        else if (audioType.equalsIgnoreCase("vlc") || audioType.equalsIgnoreCase("mp4")) {
            mediaAdapter = new MediaAdapterObject(audioType);
            mediaAdapter.play(audioType, fileName);
        } else {
            System.out.println("Invalid media. " + audioType + " format not supported");
        }
    }
}

// 3. 接口适配器模式
// 定义一个多功能接口
interface RobotActions {
    void walk();
    void talk();
    void grab();
    void sense();
    void compute();
}

// 接口适配器 - 提供默认空实现
abstract class RobotAdapter implements RobotActions {
    @Override
    public void walk() {}
    
    @Override
    public void talk() {}
    
    @Override
    public void grab() {}
    
    @Override
    public void sense() {}
    
    @Override
    public void compute() {}
}

// 具体机器人 - 只需要行走和感知功能
class SimpleRobot extends RobotAdapter {
    @Override
    public void walk() {
        System.out.println("Simple robot is walking");
    }
    
    @Override
    public void sense() {
        System.out.println("Simple robot is sensing environment");
    }
}

// 复杂机器人 - 需要所有功能
class AdvancedRobot extends RobotAdapter {
    @Override
    public void walk() {
        System.out.println("Advanced robot is walking");
    }
    
    @Override
    public void talk() {
        System.out.println("Advanced robot is talking");
    }
    
    @Override
    public void grab() {
        System.out.println("Advanced robot is grabbing objects");
    }
    
    @Override
    public void sense() {
        System.out.println("Advanced robot is sensing environment");
    }
    
    @Override
    public void compute() {
        System.out.println("Advanced robot is computing");
    }
}

// 4. 电源适配器示例
// 目标接口 - 中国标准插座
interface ChinaSocket {
    void provideElectricity();
}

// 适配者类 - 美国插座
class USSocket {
    public void provideElectricity110V() {
        System.out.println("提供110V电压");
    }
}

// 适配器 - 电源适配器
class PowerAdapter implements ChinaSocket {
    private USSocket usSocket;
    
    public PowerAdapter(USSocket usSocket) {
        this.usSocket = usSocket;
    }
    
    @Override
    public void provideElectricity() {
        System.out.print("电源适配器转换: ");
        usSocket.provideElectricity110V();
        System.out.println("转换为220V电压");
    }
}

// 中国电器
class ChinaDevice {
    public void charge(ChinaSocket socket) {
        System.out.print("中国电器充电中... ");
        socket.provideElectricity();
    }
}

// 5. 数据库驱动适配器示例
// 目标接口 - 统一数据库操作接口
interface DatabaseDriver {
    void connect();
    void executeQuery(String sql);
    void close();
}

// 适配者类 - MySQL驱动
class MySQLDriver {
    public void mysqlConnect() {
        System.out.println("连接MySQL数据库");
    }
    
    public void mysqlExecute(String sql) {
        System.out.println("MySQL执行SQL: " + sql);
    }
    
    public void mysqlClose() {
        System.out.println("关闭MySQL连接");
    }
}

// 适配者类 - PostgreSQL驱动
class PostgreSQLDriver {
    public void pgConnect() {
        System.out.println("连接PostgreSQL数据库");
    }
    
    public void pgExecute(String sql) {
        System.out.println("PostgreSQL执行SQL: " + sql);
    }
    
    public void pgClose() {
        System.out.println("关闭PostgreSQL连接");
    }
}

// MySQL适配器
class MySQLAdapter implements DatabaseDriver {
    private MySQLDriver mySQLDriver;
    
    public MySQLAdapter() {
        this.mySQLDriver = new MySQLDriver();
    }
    
    @Override
    public void connect() {
        mySQLDriver.mysqlConnect();
    }
    
    @Override
    public void executeQuery(String sql) {
        mySQLDriver.mysqlExecute(sql);
    }
    
    @Override
    public void close() {
        mySQLDriver.mysqlClose();
    }
}

// PostgreSQL适配器
class PostgreSQLAdapter implements DatabaseDriver {
    private PostgreSQLDriver postgreSQLDriver;
    
    public PostgreSQLAdapter() {
        this.postgreSQLDriver = new PostgreSQLDriver();
    }
    
    @Override
    public void connect() {
        postgreSQLDriver.pgConnect();
    }
    
    @Override
    public void executeQuery(String sql) {
        postgreSQLDriver.pgExecute(sql);
    }
    
    @Override
    public void close() {
        postgreSQLDriver.pgClose();
    }
}

public class Chapter7Example {
    public static void main(String[] args) {
        System.out.println("=== 适配器模式示例 ===\n");
        
        // 1. 类适配器示例
        System.out.println("1. 类适配器示例 - 媒体播放器：");
        AudioPlayer audioPlayer = new AudioPlayer();
        
        audioPlayer.play("mp3", "beyond the horizon.mp3");
        audioPlayer.play("mp4", "alone.mp4");
        audioPlayer.play("vlc", "far far away.vlc");
        audioPlayer.play("avi", "mind me.avi");
        System.out.println();
        
        // 2. 对象适配器示例
        System.out.println("2. 对象适配器示例 - 媒体播放器：");
        AudioPlayerWithObjectAdapter audioPlayerObj = new AudioPlayerWithObjectAdapter();
        
        audioPlayerObj.play("mp3", "beyond the horizon.mp3");
        audioPlayerObj.play("mp4", "alone.mp4");
        audioPlayerObj.play("vlc", "far far away.vlc");
        audioPlayerObj.play("avi", "mind me.avi");
        System.out.println();
        
        // 3. 接口适配器示例
        System.out.println("3. 接口适配器示例 - 机器人：");
        SimpleRobot simpleRobot = new SimpleRobot();
        simpleRobot.walk();
        simpleRobot.sense();
        // simpleRobot.talk(); // 不需要实现
        
        AdvancedRobot advancedRobot = new AdvancedRobot();
        advancedRobot.walk();
        advancedRobot.talk();
        advancedRobot.grab();
        advancedRobot.sense();
        advancedRobot.compute();
        System.out.println();
        
        // 4. 电源适配器示例
        System.out.println("4. 电源适配器示例：");
        USSocket usSocket = new USSocket();
        PowerAdapter adapter = new PowerAdapter(usSocket);
        ChinaDevice device = new ChinaDevice();
        device.charge(adapter);
        System.out.println();
        
        // 5. 数据库驱动适配器示例
        System.out.println("5. 数据库驱动适配器示例：");
        DatabaseDriver mysqlAdapter = new MySQLAdapter();
        mysqlAdapter.connect();
        mysqlAdapter.executeQuery("SELECT * FROM users");
        mysqlAdapter.close();
        
        System.out.println();
        
        DatabaseDriver postgresqlAdapter = new PostgreSQLAdapter();
        postgresqlAdapter.connect();
        postgresqlAdapter.executeQuery("SELECT * FROM products");
        postgresqlAdapter.close();
    }
}