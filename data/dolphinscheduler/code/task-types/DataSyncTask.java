import org.apache.dolphinscheduler.common.Constants;
import org.apache.dolphinscheduler.common.task.AbstractParameters;
import org.apache.dolphinscheduler.common.task.TaskTimeoutParameter;
import org.apache.dolphinscheduler.common.utils.JSONUtils;
import org.apache.dolphinscheduler.plugin.task.api.TaskChannel;
import org.apache.dolphinscheduler.plugin.task.api.TaskExecutionContext;
import org.apache.dolphinscheduler.plugin.task.api.TaskExecutor;
import org.apache.dolphinscheduler.plugin.task.api.model.Property;
import org.apache.dolphinscheduler.plugin.task.api.model.TaskInfo;
import org.apache.dolphinscheduler.plugin.task.api.model.ResourceInfo;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * 自定义数据同步任务类型
 */
public class DataSyncTask implements TaskExecutor {
    
    private static final Logger logger = LoggerFactory.getLogger(DataSyncTask.class);
    
    @Override
    public void init() {
        logger.info("DataSync task initialized");
    }
    
    @Override
    public void handle(TaskExecutionContext taskExecutionContext) throws Exception {
        // 1. 获取任务参数
        DataSyncTaskParams params = parseTaskParams(taskExecutionContext);
        
        // 2. 初始化同步引擎
        DataSyncEngine syncEngine = createDataSyncEngine(params, taskExecutionContext);
        
        // 3. 执行数据同步
        DataSyncResult result = syncEngine.sync();
        
        // 4. 设置输出参数
        setOutputParameters(taskExecutionContext, result);
        
        // 5. 记录执行日志
        logExecutionResult(result);
        
        // 6. 根据结果决定退出码
        if (result.isSuccess()) {
            taskExecutionContext.setExitStatusCode(Constants.EXIT_CODE_SUCCESS);
        } else {
            taskExecutionContext.setExitStatusCode(Constants.EXIT_CODE_FAILURE);
            throw new RuntimeException("Data sync failed: " + result.getErrorMessage());
        }
    }
    
    /**
     * 解析任务参数
     */
    private DataSyncTaskParams parseTaskParams(TaskExecutionContext context) {
        AbstractParameters parameters = context.getTaskParams();
        Map<String, Object> parameterMap = JSONUtils.toMap(parameters.getParamsJson());
        
        DataSyncTaskParams params = new DataSyncTaskParams();
        
        // 解析源数据源
        params.setSourceDataSourceId((Integer) parameterMap.getOrDefault("sourceDataSourceId", -1));
        params.setSourceType((String) parameterMap.getOrDefault("sourceType", "MYSQL"));
        params.setSourceTable((String) parameterMap.getOrDefault("sourceTable", ""));
        
        // 解析目标数据源
        params.setTargetDataSourceId((Integer) parameterMap.getOrDefault("targetDataSourceId", -1));
        params.setTargetType((String) parameterMap.getOrDefault("targetType", "MYSQL"));
        params.setTargetTable((String) parameterMap.getOrDefault("targetTable", ""));
        
        // 解析同步配置
        params.setSyncMode((String) parameterMap.getOrDefault("syncMode", "FULL")); // FULL, INCREMENTAL
        params.setBatchSize((Integer) parameterMap.getOrDefault("batchSize", 10000));
        params.setConcurrency((Integer) parameterMap.getOrDefault("concurrency", 4));
        
        // 解析增量配置
        params.setIncrementalColumn((String) parameterMap.getOrDefault("incrementalColumn", "id"));
        params.setLastSyncTime((Date) parameterMap.getOrDefault("lastSyncTime", null));
        
        return params;
    }
    
    /**
     * 创建数据同步引擎
     */
    private DataSyncEngine createDataSyncEngine(DataSyncTaskParams params, 
                                                 TaskExecutionContext context) {
        DataSyncEngine engine = new DataSyncEngine();
        
        // 设置源数据源
        DataSource sourceDataSource = getDataSource(params.getSourceDataSourceId());
        engine.setSourceDataSource(sourceDataSource);
        engine.setSourceType(params.getSourceType());
        engine.setSourceTable(params.getSourceTable());
        
        // 设置目标数据源
        DataSource targetDataSource = getDataSource(params.getTargetDataSourceId());
        engine.setTargetDataSource(targetDataSource);
        engine.setTargetType(params.getTargetType());
        engine.setTargetTable(params.getTargetTable());
        
        // 设置同步配置
        engine.setSyncMode(params.getSyncMode());
        engine.setBatchSize(params.getBatchSize());
        engine.setConcurrency(params.getConcurrency());
        
        // 设置增量配置
        engine.setIncrementalColumn(params.getIncrementalColumn());
        engine.setLastSyncTime(params.getLastSyncTime());
        
        // 设置执行上下文
        engine.setExecutionContext(context);
        
        return engine;
    }
    
    /**
     * 获取数据源信息（简化实现，实际应从DolphinScheduler API获取）
     */
    private DataSource getDataSource(int dataSourceId) {
        // 这里应该调用DolphinScheduler API获取数据源信息
        // 为了简化示例，使用硬编码
        
        DataSource dataSource = new DataSource();
        
        if (dataSourceId == 1) { // 源数据源
            dataSource.setHost("mysql.example.com");
            dataSource.setPort(3306);
            dataSource.setDatabase("source_db");
            dataSource.setUsername("source_user");
            dataSource.setPassword("source_password");
        } else if (dataSourceId == 2) { // 目标数据源
            dataSource.setHost("mysql.example.com");
            dataSource.setPort(3306);
            dataSource.setDatabase("target_db");
            dataSource.setUsername("target_user");
            dataSource.setPassword("target_password");
        }
        
        return dataSource;
    }
    
    /**
     * 设置输出参数
     */
    private void setOutputParameters(TaskExecutionContext context, DataSyncResult result) {
        // 设置同步记录数
        context.setOutputParam("sync_record_count", String.valueOf(result.getSyncCount()));
        
        // 设置同步耗时
        context.setOutputParam("sync_duration_ms", String.valueOf(result.getDurationMs()));
        
        // 设置下次同步时间
        if (result.getNextSyncTime() != null) {
            context.setOutputParam("next_sync_time", result.getNextSyncTime().toString());
        }
        
        // 设置最大ID（增量同步）
        if (result.getMaxIncrementalId() > 0) {
            context.setOutputParam("max_incremental_id", String.valueOf(result.getMaxIncrementalId()));
        }
    }
    
    /**
     * 记录执行日志
     */
    private void logExecutionResult(DataSyncResult result) {
        if (result.isSuccess()) {
            logger.info("Data sync completed successfully");
            logger.info("Synced records: " + result.getSyncCount());
            logger.info("Duration: " + result.getDurationMs() + "ms");
        } else {
            logger.error("Data sync failed: " + result.getErrorMessage());
            if (result.getException() != null) {
                logger.error("Exception details", result.getException());
            }
        }
    }
    
    @Override
    public void cancel() {
        logger.info("DataSync task cancelled");
    }
    
    /**
     * 数据同步任务参数
     */
    public static class DataSyncTaskParams {
        private int sourceDataSourceId;
        private String sourceType;
        private String sourceTable;
        
        private int targetDataSourceId;
        private String targetType;
        private String targetTable;
        
        private String syncMode; // FULL, INCREMENTAL
        private int batchSize;
        private int concurrency;
        
        private String incrementalColumn;
        private Date lastSyncTime;
        
        // Getters and Setters
        public int getSourceDataSourceId() {
            return sourceDataSourceId;
        }
        
        public void setSourceDataSourceId(int sourceDataSourceId) {
            this.sourceDataSourceId = sourceDataSourceId;
        }
        
        public String getSourceType() {
            return sourceType;
        }
        
        public void setSourceType(String sourceType) {
            this.sourceType = sourceType;
        }
        
        public String getSourceTable() {
            return sourceTable;
        }
        
        public void setSourceTable(String sourceTable) {
            this.sourceTable = sourceTable;
        }
        
        public int getTargetDataSourceId() {
            return targetDataSourceId;
        }
        
        public void setTargetDataSourceId(int targetDataSourceId) {
            this.targetDataSourceId = targetDataSourceId;
        }
        
        public String getTargetType() {
            return targetType;
        }
        
        public void setTargetType(String targetType) {
            this.targetType = targetType;
        }
        
        public String getTargetTable() {
            return targetTable;
        }
        
        public void setTargetTable(String targetTable) {
            this.targetTable = targetTable;
        }
        
        public String getSyncMode() {
            return syncMode;
        }
        
        public void setSyncMode(String syncMode) {
            this.syncMode = syncMode;
        }
        
        public int getBatchSize() {
            return batchSize;
        }
        
        public void setBatchSize(int batchSize) {
            this.batchSize = batchSize;
        }
        
        public int getConcurrency() {
            return concurrency;
        }
        
        public void setConcurrency(int concurrency) {
            this.concurrency = concurrency;
        }
        
        public String getIncrementalColumn() {
            return incrementalColumn;
        }
        
        public void setIncrementalColumn(String incrementalColumn) {
            this.incrementalColumn = incrementalColumn;
        }
        
        public Date getLastSyncTime() {
            return lastSyncTime;
        }
        
        public void setLastSyncTime(Date lastSyncTime) {
            this.lastSyncTime = lastSyncTime;
        }
    }
    
    /**
     * 数据同步引擎
     */
    public static class DataSyncEngine {
        private DataSource sourceDataSource;
        private String sourceType;
        private String sourceTable;
        
        private DataSource targetDataSource;
        private String targetType;
        private String targetTable;
        
        private String syncMode;
        private int batchSize;
        private int concurrency;
        
        private String incrementalColumn;
        private Date lastSyncTime;
        private TaskExecutionContext executionContext;
        
        // 执行数据同步
        public DataSyncResult sync() {
            long startTime = System.currentTimeMillis();
            
            try {
                if ("INCREMENTAL".equals(syncMode)) {
                    return performIncrementalSync(startTime);
                } else {
                    return performFullSync(startTime);
                }
            } catch (Exception e) {
                DataSyncResult result = new DataSyncResult();
                result.setSuccess(false);
                result.setErrorMessage(e.getMessage());
                result.setException(e);
                result.setDurationMs(System.currentTimeMillis() - startTime);
                return result;
            }
        }
        
        // 执行全量同步
        private DataSyncResult performFullSync(long startTime) throws SQLException {
            DataSyncResult result = new DataSyncResult();
            
            // 1. 清空目标表
            clearTargetTable();
            
            // 2. 获取总记录数
            long totalCount = getSourceTableCount();
            
            // 3. 分批同步数据
            int offset = 0;
            int syncCount = 0;
            
            try (Connection sourceConnection = sourceDataSource.getConnection();
                 Connection targetConnection = targetDataSource.getConnection()) {
                
                sourceConnection.setAutoCommit(false);
                targetConnection.setAutoCommit(false);
                
                while (offset < totalCount) {
                    // 查询源表数据
                    String selectSql = buildSelectSql(offset);
                    List<Map<String, Object>> records = queryRecords(sourceConnection, selectSql);
                    
                    if (records.isEmpty()) {
                        break;
                    }
                    
                    // 批量插入目标表
                    insertRecords(targetConnection, records);
                    
                    syncCount += records.size();
                    offset += records.size();
                    
                    if (executionContext != null) {
                        executionContext.getLogger().info("Synced {}/{} records", syncCount, totalCount);
                    }
                }
                
                // 提交事务
                targetConnection.commit();
            }
            
            result.setSuccess(true);
            result.setSyncCount(syncCount);
            result.setDurationMs(System.currentTimeMillis() - startTime);
            result.setNextSyncTime(new Date());
            
            return result;
        }
        
        // 执行增量同步
        private DataSyncResult performIncrementalSync(long startTime) throws SQLException {
            DataSyncResult result = new DataSyncResult();
            
            // 1. 获取上次同步位置
            long lastSyncId = getLastSyncId();
            
            try (Connection sourceConnection = sourceDataSource.getConnection();
                 Connection targetConnection = targetDataSource.getConnection()) {
                
                sourceConnection.setAutoCommit(false);
                targetConnection.setAutoCommit(false);
                
                // 2. 查询增量数据
                String selectSql = buildIncrementalSelectSql(lastSyncId);
                List<Map<String, Object>> records = queryRecords(sourceConnection, selectSql);
                
                if (!records.isEmpty()) {
                    // 3. 插入增量数据
                    insertRecords(targetConnection, records);
                    
                    // 4. 提交事务
                    targetConnection.commit();
                    
                    // 5. 更新同步位置
                    long maxId = getMaxIdFromRecords(records, incrementalColumn);
                    result.setMaxIncrementalId(maxId);
                    
                    if (executionContext != null) {
                        executionContext.getLogger().info("Incremental sync completed, records: {}", records.size());
                    }
                }
                
                result.setSuccess(true);
                result.setSyncCount(records.size());
                result.setDurationMs(System.currentTimeMillis() - startTime);
                result.setNextSyncTime(calculateNextSyncTime());
            }
            
            return result;
        }
        
        // 清空目标表
        private void clearTargetTable() throws SQLException {
            try (Connection connection = targetDataSource.getConnection();
                 Statement statement = connection.createStatement()) {
                
                String sql = "TRUNCATE TABLE " + targetTable;
                statement.execute(sql);
                
                if (executionContext != null) {
                    executionContext.getLogger().info("Cleared target table: {}", targetTable);
                }
            }
        }
        
        // 获取源表记录数
        private long getSourceTableCount() throws SQLException {
            try (Connection connection = sourceDataSource.getConnection();
                 Statement statement = connection.createStatement();
                 ResultSet resultSet = statement.executeQuery("SELECT COUNT(*) FROM " + sourceTable)) {
                
                if (resultSet.next()) {
                    return resultSet.getLong(1);
                }
                
                return 0;
            }
        }
        
        // 构建分页查询SQL
        private String buildSelectSql(int offset) {
            if ("MYSQL".equals(sourceType)) {
                return String.format("SELECT * FROM %s LIMIT %d, %d", 
                                     sourceTable, offset, batchSize);
            } else if ("POSTGRESQL".equals(sourceType)) {
                return String.format("SELECT * FROM %s LIMIT %d OFFSET %d", 
                                     sourceTable, batchSize, offset);
            } else if ("ORACLE".equals(sourceType)) {
                int endRow = offset + batchSize;
                return String.format("SELECT * FROM (SELECT a.*, ROWNUM rn FROM %s a WHERE ROWNUM <= %d) WHERE rn > %d", 
                                     sourceTable, endRow, offset);
            }
            
            // 默认MySQL语法
            return String.format("SELECT * FROM %s LIMIT %d, %d", 
                                 sourceTable, offset, batchSize);
        }
        
        // 构建增量查询SQL
        private String buildIncrementalSelectSql(long lastSyncId) {
            return String.format("SELECT * FROM %s WHERE %s > %d ORDER BY %s", 
                                 sourceTable, incrementalColumn, lastSyncId, incrementalColumn);
        }
        
        // 查询记录
        private List<Map<String, Object>> queryRecords(Connection connection, String sql) throws SQLException {
            List<Map<String, Object>> records = new ArrayList<>();
            
            try (Statement statement = connection.createStatement();
                 ResultSet resultSet = statement.executeQuery(sql)) {
                
                while (resultSet.next()) {
                    Map<String, Object> record = new HashMap<>();
                    
                    // 这里应该根据表的列名动态设置
                    // 简化实现，只处理几个通用字段
                    record.put("id", resultSet.getLong("id"));
                    record.put("name", resultSet.getString("name"));
                    // 其他字段...
                    
                    records.add(record);
                }
            }
            
            return records;
        }
        
        // 插入记录
        private void insertRecords(Connection connection, List<Map<String, Object>> records) throws SQLException {
            if (records.isEmpty()) {
                return;
            }
            
            // 构建批量插入SQL
            String sql = buildInsertSql(records.get(0));
            
            try (PreparedStatement statement = connection.prepareStatement(sql)) {
                for (Map<String, Object> record : records) {
                    setPreparedStatementParameters(statement, record);
                    statement.addBatch();
                }
                
                statement.executeBatch();
            }
        }
        
        // 构建插入SQL
        private String buildInsertSql(Map<String, Object> record) {
            StringBuilder columns = new StringBuilder();
            StringBuilder placeholders = new StringBuilder();
            
            boolean first = true;
            for (String column : record.keySet()) {
                if (!first) {
                    columns.append(", ");
                    placeholders.append(", ");
                }
                
                columns.append(column);
                placeholders.append("?");
                first = false;
            }
            
            return String.format("INSERT INTO %s (%s) VALUES (%s)", 
                                 targetTable, columns.toString(), placeholders.toString());
        }
        
        // 设置PreparedStatement参数
        private void setPreparedStatementParameters(PreparedStatement statement, 
                                                    Map<String, Object> record) throws SQLException {
            int index = 1;
            for (Object value : record.values()) {
                statement.setObject(index++, value);
            }
        }
        
        // 获取上次同步位置
        private long getLastSyncId() {
            // 这里应该从配置或数据库获取上次同步位置
            // 简化实现，返回0表示从头开始同步
            return 0;
        }
        
        // 从记录中获取最大ID
        private long getMaxIdFromRecords(List<Map<String, Object>> records, String column) {
            long maxId = 0;
            
            for (Map<String, Object> record : records) {
                Object idValue = record.get(column);
                if (idValue != null) {
                    long id = ((Number) idValue).longValue();
                    if (id > maxId) {
                        maxId = id;
                    }
                }
            }
            
            return maxId;
        }
        
        // 计算下次同步时间
        private Date calculateNextSyncTime() {
            // 这里可以根据业务需求计算下次同步时间
            // 简化实现，返回1小时后的时间
            return new Date(System.currentTimeMillis() + 60 * 60 * 1000);
        }
        
        // Getters and Setters
        public DataSource getSourceDataSource() {
            return sourceDataSource;
        }
        
        public void setSourceDataSource(DataSource sourceDataSource) {
            this.sourceDataSource = sourceDataSource;
        }
        
        public String getSourceType() {
            return sourceType;
        }
        
        public void setSourceType(String sourceType) {
            this.sourceType = sourceType;
        }
        
        public String getSourceTable() {
            return sourceTable;
        }
        
        public void setSourceTable(String sourceTable) {
            this.sourceTable = sourceTable;
        }
        
        public DataSource getTargetDataSource() {
            return targetDataSource;
        }
        
        public void setTargetDataSource(DataSource targetDataSource) {
            this.targetDataSource = targetDataSource;
        }
        
        public String getTargetType() {
            return targetType;
        }
        
        public void setTargetType(String targetType) {
            this.targetType = targetType;
        }
        
        public String getTargetTable() {
            return targetTable;
        }
        
        public void setTargetTable(String targetTable) {
            this.targetTable = targetTable;
        }
        
        public String getSyncMode() {
            return syncMode;
        }
        
        public void setSyncMode(String syncMode) {
            this.syncMode = syncMode;
        }
        
        public int getBatchSize() {
            return batchSize;
        }
        
        public void setBatchSize(int batchSize) {
            this.batchSize = batchSize;
        }
        
        public int getConcurrency() {
            return concurrency;
        }
        
        public void setConcurrency(int concurrency) {
            this.concurrency = concurrency;
        }
        
        public String getIncrementalColumn() {
            return incrementalColumn;
        }
        
        public void setIncrementalColumn(String incrementalColumn) {
            this.incrementalColumn = incrementalColumn;
        }
        
        public Date getLastSyncTime() {
            return lastSyncTime;
        }
        
        public void setLastSyncTime(Date lastSyncTime) {
            this.lastSyncTime = lastSyncTime;
        }
        
        public TaskExecutionContext getExecutionContext() {
            return executionContext;
        }
        
        public void setExecutionContext(TaskExecutionContext executionContext) {
            this.executionContext = executionContext;
        }
    }
    
    /**
     * 数据源配置
     */
    public static class DataSource {
        private String host;
        private int port;
        private String database;
        private String username;
        private String password;
        
        // 获取数据库连接
        public Connection getConnection() throws SQLException {
            String url = String.format("jdbc:mysql://%s:%d/%s", host, port, database);
            return DriverManager.getConnection(url, username, password);
        }
        
        // Getters and Setters
        public String getHost() {
            return host;
        }
        
        public void setHost(String host) {
            this.host = host;
        }
        
        public int getPort() {
            return port;
        }
        
        public void setPort(int port) {
            this.port = port;
        }
        
        public String getDatabase() {
            return database;
        }
        
        public void setDatabase(String database) {
            this.database = database;
        }
        
        public String getUsername() {
            return username;
        }
        
        public void setUsername(String username) {
            this.username = username;
        }
        
        public String getPassword() {
            return password;
        }
        
        public void setPassword(String password) {
            this.password = password;
        }
    }
    
    /**
     * 数据同步结果
     */
    public static class DataSyncResult {
        private boolean success;
        private int syncCount;
        private long durationMs;
        private Date nextSyncTime;
        private long maxIncrementalId;
        private String errorMessage;
        private Exception exception;
        
        // Getters and Setters
        public boolean isSuccess() {
            return success;
        }
        
        public void setSuccess(boolean success) {
            this.success = success;
        }
        
        public int getSyncCount() {
            return syncCount;
        }
        
        public void setSyncCount(int syncCount) {
            this.syncCount = syncCount;
        }
        
        public long getDurationMs() {
            return durationMs;
        }
        
        public void setDurationMs(long durationMs) {
            this.durationMs = durationMs;
        }
        
        public Date getNextSyncTime() {
            return nextSyncTime;
        }
        
        public void setNextSyncTime(Date nextSyncTime) {
            this.nextSyncTime = nextSyncTime;
        }
        
        public long getMaxIncrementalId() {
            return maxIncrementalId;
        }
        
        public void setMaxIncrementalId(long maxIncrementalId) {
            this.maxIncrementalId = maxIncrementalId;
        }
        
        public String getErrorMessage() {
            return errorMessage;
        }
        
        public void setErrorMessage(String errorMessage) {
            this.errorMessage = errorMessage;
        }
        
        public Exception getException() {
            return exception;
        }
        
        public void setException(Exception exception) {
            this.exception = exception;
        }
    }
}