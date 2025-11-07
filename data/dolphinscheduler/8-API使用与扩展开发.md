# 第8章 API使用与扩展开发

## 8.1 REST API使用

### 8.1.1 API概述

DolphinScheduler提供完整的REST API，支持通过编程方式管理项目、工作流、任务等所有资源。

#### 8.1.1.1 API认证

API访问需要使用Token认证，可以通过用户名和密码获取Token。

```java
// API认证客户端
public class DolphinSchedulerApiClient {
    
    private String baseUrl;
    private String token;
    private CloseableHttpClient httpClient;
    
    public DolphinSchedulerApiClient(String baseUrl, String username, String password) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.httpClient = HttpClients.createDefault();
        
        // 登录获取Token
        this.token = login(username, password);
    }
    
    // 登录获取Token
    private String login(String username, String password) {
        try {
            String loginUrl = baseUrl + "/login";
            
            Map<String, String> formData = new HashMap<>();
            formData.put("userName", username);
            formData.put("userPassword", password);
            
            HttpPost httpPost = new HttpPost(loginUrl);
            httpPost.setEntity(new UrlEncodedFormEntity(
                formData.entrySet().stream()
                    .map(e -> new BasicNameValuePair(e.getKey(), e.getValue()))
                    .collect(Collectors.toList()),
                StandardCharsets.UTF_8));
            
            try (CloseableHttpResponse response = httpClient.execute(httpPost)) {
                String responseBody = EntityUtils.toString(response.getEntity());
                LoginResult loginResult = JsonUtils.parseObject(responseBody, LoginResult.class);
                
                if (loginResult.getCode() != 0) {
                    throw new RuntimeException("Login failed: " + loginResult.getMsg());
                }
                
                return loginResult.getData().getToken();
            }
        } catch (Exception e) {
            throw new RuntimeException("Login error", e);
        }
    }
    
    // 通用API请求方法
    private ApiResponse executeRequest(String method, String endpoint, Object requestBody) {
        try {
            String url = baseUrl + endpoint;
            HttpRequestBase request;
            
            switch (method.toUpperCase()) {
                case "GET":
                    request = new HttpGet(url);
                    break;
                case "POST":
                    request = new HttpPost(url);
                    if (requestBody != null) {
                        ((HttpPost) request).setEntity(new StringEntity(
                            JsonUtils.toJsonString(requestBody), StandardCharsets.UTF_8));
                    }
                    break;
                case "PUT":
                    request = new HttpPut(url);
                    if (requestBody != null) {
                        ((HttpPut) request).setEntity(new StringEntity(
                            JsonUtils.toJsonString(requestBody), StandardCharsets.UTF_8));
                    }
                    break;
                case "DELETE":
                    request = new HttpDelete(url);
                    break;
                default:
                    throw new RuntimeException("Unsupported HTTP method: " + method);
            }
            
            // 设置请求头
            request.setHeader("Content-Type", "application/json");
            request.setHeader("Authorization", "Bearer " + token);
            
            try (CloseableHttpResponse response = httpClient.execute(request)) {
                String responseBody = EntityUtils.toString(response.getEntity());
                return JsonUtils.parseObject(responseBody, ApiResponse.class);
            }
        } catch (Exception e) {
            throw new RuntimeException("API request error", e);
        }
    }
    
    // 获取API响应数据
    public <T> T executeRequest(String method, String endpoint, Object requestBody, Class<T> dataClass) {
        ApiResponse apiResponse = executeRequest(method, endpoint, requestBody);
        
        if (apiResponse.getCode() != 0) {
            throw new RuntimeException("API request failed: " + apiResponse.getMsg());
        }
        
        return JsonUtils.parseObject(JsonUtils.toJsonString(apiResponse.getData()), dataClass);
    }
}
```

### 8.1.2 项目管理API

#### 8.1.2.1 项目CRUD操作

```java
// 项目管理API客户端
public class ProjectApiClient extends DolphinSchedulerApiClient {
    
    public ProjectApiClient(String baseUrl, String username, String password) {
        super(baseUrl, username, password);
    }
    
    // 创建项目
    public ProjectDetail createProject(String projectName, String description) {
        ProjectCreateRequest request = new ProjectCreateRequest();
        request.setProjectName(projectName);
        request.setDescription(description);
        
        return executeRequest("POST", "/projects", request, ProjectDetail.class);
    }
    
    // 获取项目详情
    public ProjectDetail getProject(int projectId) {
        return executeRequest("GET", "/projects/" + projectId, null, ProjectDetail.class);
    }
    
    // 更新项目
    public ProjectDetail updateProject(int projectId, String projectName, String description) {
        ProjectUpdateRequest request = new ProjectUpdateRequest();
        request.setProjectName(projectName);
        request.setDescription(description);
        
        return executeRequest("PUT", "/projects/" + projectId, request, ProjectDetail.class);
    }
    
    // 删除项目
    public void deleteProject(int projectId) {
        executeRequest("DELETE", "/projects/" + projectId, null);
    }
    
    // 查询项目列表
    public PageInfo<ProjectSummary> listProjects(String searchVal, int page, int pageSize) {
        String endpoint = String.format("/projects?searchVal=%s&page=%d&pageSize=%d", 
                                        searchVal, page, pageSize);
        return executeRequest("GET", endpoint, null, PageInfo.class);
    }
    
    // 打开项目
    public ProjectDetail openProject(int projectId) {
        return executeRequest("POST", "/projects/" + projectId + "/open", null, ProjectDetail.class);
    }
    
    // 关闭项目
    public void closeProject(int projectId) {
        executeRequest("POST", "/projects/" + projectId + "/close", null);
    }
}
```

#### 8.1.2.2 项目使用示例

```java
// 项目API使用示例
public class ProjectApiExample {
    
    public static void main(String[] args) {
        // 1. 创建API客户端
        ProjectApiClient client = new ProjectApiClient(
            "http://localhost:12345", "admin", "dolphinscheduler123");
        
        try {
            // 2. 创建项目
            ProjectDetail project = client.createProject("data_warehouse", "数据仓库项目");
            System.out.println("Created project: " + project.getProjectName());
            int projectId = project.getId();
            
            // 3. 获取项目详情
            project = client.getProject(projectId);
            System.out.println("Project details: " + JsonUtils.toJsonString(project));
            
            // 4. 更新项目
            project = client.updateProject(projectId, "data_warehouse", "数据仓库ETL项目");
            System.out.println("Updated project: " + project.getDescription());
            
            // 5. 查询项目列表
            PageInfo<ProjectSummary> projects = client.listProjects("", 1, 10);
            System.out.println("Total projects: " + projects.getTotal());
            
            // 6. 打开项目
            client.openProject(projectId);
            System.out.println("Project opened");
            
            // 7. 关闭项目
            client.closeProject(projectId);
            System.out.println("Project closed");
            
            // 8. 删除项目
            client.deleteProject(projectId);
            System.out.println("Project deleted");
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

### 8.1.3 工作流管理API

#### 8.1.3.1 工作流CRUD操作

```java
// 工作流管理API客户端
public class WorkflowApiClient extends DolphinSchedulerApiClient {
    
    public WorkflowApiClient(String baseUrl, String username, String password) {
        super(baseUrl, username, password);
    }
    
    // 创建工作流
    public WorkflowDetail createWorkflow(int projectId, String workflowName, 
                                         String description, String workflowDefinition) {
        WorkflowCreateRequest request = new WorkflowCreateRequest();
        request.setName(workflowName);
        request.setDescription(description);
        request.setDefinition(workflowDefinition);
        
        String endpoint = "/projects/" + projectId + "/process-definition";
        return executeRequest("POST", endpoint, request, WorkflowDetail.class);
    }
    
    // 获取工作流详情
    public WorkflowDetail getWorkflow(int projectId, int workflowId) {
        String endpoint = "/projects/" + projectId + "/process-definition/" + workflowId;
        return executeRequest("GET", endpoint, null, WorkflowDetail.class);
    }
    
    // 更新工作流
    public WorkflowDetail updateWorkflow(int projectId, int workflowId, 
                                         String workflowName, String description, String workflowDefinition) {
        WorkflowUpdateRequest request = new WorkflowUpdateRequest();
        request.setName(workflowName);
        request.setDescription(description);
        request.setDefinition(workflowDefinition);
        
        String endpoint = "/projects/" + projectId + "/process-definition/" + workflowId;
        return executeRequest("PUT", endpoint, request, WorkflowDetail.class);
    }
    
    // 删除工作流
    public void deleteWorkflow(int projectId, int workflowId) {
        String endpoint = "/projects/" + projectId + "/process-definition/" + workflowId;
        executeRequest("DELETE", endpoint, null);
    }
    
    // 发布工作流
    public WorkflowDetail publishWorkflow(int projectId, int workflowId) {
        String endpoint = "/projects/" + projectId + "/process-definition/" + workflowId + "/release";
        return executeRequest("POST", endpoint, null, WorkflowDetail.class);
    }
    
    // 下线工作流
    public WorkflowDetail offlineWorkflow(int projectId, int workflowId) {
        String endpoint = "/projects/" + projectId + "/process-definition/" + workflowId + "/offline";
        return executeRequest("POST", endpoint, null, WorkflowDetail.class);
    }
    
    // 查询工作流列表
    public PageInfo<WorkflowSummary> listWorkflows(int projectId, String searchVal, 
                                                     int page, int pageSize) {
        String endpoint = String.format("/projects/%d/process-definition?searchVal=%s&page=%d&pageSize=%d", 
                                        projectId, searchVal, page, pageSize);
        return executeRequest("GET", endpoint, null, PageInfo.class);
    }
    
    // 执行工作流
    public WorkflowInstanceDetail runWorkflow(int projectId, int workflowId, 
                                              Map<String, Object> globalParams) {
        WorkflowRunRequest request = new WorkflowRunRequest();
        request.setProcessDefinitionCode(workflowId);
        request.setGlobalParams(convertParamsToJsonString(globalParams));
        
        String endpoint = "/projects/" + projectId + "/process-instances";
        return executeRequest("POST", endpoint, request, WorkflowInstanceDetail.class);
    }
    
    // 转换参数为JSON字符串
    private String convertParamsToJsonString(Map<String, Object> params) {
        if (params == null || params.isEmpty()) {
            return "[]";
        }
        
        List<Map<String, Object>> paramList = new ArrayList<>();
        for (Map.Entry<String, Object> entry : params.entrySet()) {
            Map<String, Object> param = new HashMap<>();
            param.put("prop", entry.getKey());
            param.put("value", entry.getValue().toString());
            paramList.add(param);
        }
        
        return JsonUtils.toJsonString(paramList);
    }
}
```

#### 8.1.3.2 工作流使用示例

```java
// 工作流API使用示例
public class WorkflowApiExample {
    
    public static void main(String[] args) {
        // 1. 创建API客户端
        WorkflowApiClient client = new WorkflowApiClient(
            "http://localhost:12345", "admin", "dolphinscheduler123");
        
        int projectId = 1; // 假设项目ID为1
        
        try {
            // 2. 创建工作流定义
            String workflowDefinition = createSampleWorkflowDefinition();
            WorkflowDetail workflow = client.createWorkflow(
                projectId, "ETL_workflow", "数据ETL工作流", workflowDefinition);
            System.out.println("Created workflow: " + workflow.getName());
            int workflowId = workflow.getId();
            
            // 3. 获取工作流详情
            workflow = client.getWorkflow(projectId, workflowId);
            System.out.println("Workflow details: " + JsonUtils.toJsonString(workflow));
            
            // 4. 更新工作流
            workflowDefinition = updateSampleWorkflowDefinition();
            workflow = client.updateWorkflow(
                projectId, workflowId, "ETL_workflow_v2", "数据ETL工作流v2", workflowDefinition);
            System.out.println("Updated workflow: " + workflow.getName());
            
            // 5. 发布工作流
            workflow = client.publishWorkflow(projectId, workflowId);
            System.out.println("Published workflow: " + workflow.getName());
            
            // 6. 执行工作流
            Map<String, Object> params = new HashMap<>();
            params.put("bizDate", "20230101");
            params.put("source_db", "orders_db");
            
            WorkflowInstanceDetail instance = client.runWorkflow(projectId, workflowId, params);
            System.out.println("Started workflow instance: " + instance.getId());
            
            // 7. 等待工作流完成
            waitForWorkflowCompletion(client, projectId, instance.getId());
            
            // 8. 查询工作流列表
            PageInfo<WorkflowSummary> workflows = client.listWorkflows(projectId, "", 1, 10);
            System.out.println("Total workflows: " + workflows.getTotal());
            
            // 9. 下线工作流
            workflow = client.offlineWorkflow(projectId, workflowId);
            System.out.println("Offline workflow: " + workflow.getName());
            
            // 10. 删除工作流
            client.deleteWorkflow(projectId, workflowId);
            System.out.println("Deleted workflow");
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
    
    // 创建示例工作流定义
    private static String createSampleWorkflowDefinition() {
        Map<String, Object> workflow = new HashMap<>();
        
        // 设置全局参数
        List<Map<String, Object>> globalParams = new ArrayList<>();
        Map<String, Object> param1 = new HashMap<>();
        param1.put("prop", "bizDate");
        param1.put("direct", "IN");
        param1.put("type", "VARCHAR");
        param1.put("value", "${system.biz.date}");
        globalParams.add(param1);
        
        // 设置任务
        List<Map<String, Object>> tasks = new ArrayList<>();
        
        // 任务1：数据抽取
        Map<String, Object> task1 = new HashMap<>();
        task1.put("id", "task-1");
        task1.put("type", "SHELL");
        task1.put("name", "数据抽取");
        Map<String, Object> task1Params = new HashMap<>();
        task1Params.put("rawScript", "echo 'Extract data for ${bizDate}'");
        task1.put("params", task1Params);
        task1.put("preTaskNames", Collections.emptyList());
        tasks.add(task1);
        
        // 任务2：数据加载
        Map<String, Object> task2 = new HashMap<>();
        task2.put("id", "task-2");
        task2.put("type", "SHELL");
        task2.put("name", "数据加载");
        Map<String, Object> task2Params = new HashMap<>();
        task2Params.put("rawScript", "echo 'Load data for ${bizDate}'");
        task2.put("params", task2Params);
        task2.put("preTaskNames", Collections.singletonList("task-1"));
        tasks.add(task2);
        
        workflow.put("globalParams", globalParams);
        workflow.put("tasks", tasks);
        
        return JsonUtils.toJsonString(workflow);
    }
    
    // 更新示例工作流定义
    private static String updateSampleWorkflowDefinition() {
        // 创建更复杂的工作流定义
        return createSampleWorkflowDefinition();
    }
    
    // 等待工作流完成
    private static void waitForWorkflowCompletion(WorkflowApiClient client, 
                                                 int projectId, int instanceId) {
        try {
            while (true) {
                // 获取工作流实例状态
                String endpoint = "/projects/" + projectId + "/process-instances/" + instanceId;
                ApiResponse response = client.executeRequest("GET", endpoint, null);
                
                if (response.getCode() == 0) {
                    Map<String, Object> instanceData = (Map<String, Object>) response.getData();
                    String state = (String) instanceData.get("state");
                    
                    if ("SUCCESS".equals(state)) {
                        System.out.println("Workflow completed successfully");
                        break;
                    } else if ("FAILURE".equals(state)) {
                        System.out.println("Workflow failed");
                        break;
                    }
                }
                
                // 等待5秒后再次检查
                Thread.sleep(5000);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
```

## 8.2 自定义任务类型开发

### 8.2.1 任务类型概述

DolphinScheduler支持开发自定义任务类型，通过扩展TaskExecutor接口实现特定业务需求。

### 8.2.2 自定义任务类型实现

#### 8.2.2.1 基础任务类型

```java
// 自定义任务类型：数据同步任务
public class DataSyncTask implements TaskExecutor {
    
    @Override
    public void execute(TaskExecutionContext context) {
        // 1. 获取任务参数
        DataSyncTaskParams params = parseTaskParams(context.getTaskParams());
        
        // 2. 初始化同步引擎
        DataSyncEngine syncEngine = createDataSyncEngine(params);
        
        // 3. 执行数据同步
        DataSyncResult result = syncEngine.sync();
        
        // 4. 设置输出参数
        setOutputParameters(context, result);
        
        // 5. 记录执行日志
        logExecutionResult(result);
        
        // 6. 根据结果决定退出码
        if (result.isSuccess()) {
            context.setExitStatusCode(TaskConstants.EXIT_CODE_SUCCESS);
        } else {
            context.setExitStatusCode(TaskConstants.EXIT_CODE_FAILURE);
        }
    }
    
    // 解析任务参数
    private DataSyncTaskParams parseTaskParams(TaskParams taskParams) {
        DataSyncTaskParams params = new DataSyncTaskParams();
        
        // 解析源数据源
        params.setSourceDataSourceId(taskParams.getInt("sourceDataSourceId", -1));
        params.setSourceType(taskParams.getString("sourceType", "MYSQL"));
        params.setSourceTable(taskParams.getString("sourceTable"));
        
        // 解析目标数据源
        params.setTargetDataSourceId(taskParams.getInt("targetDataSourceId", -1));
        params.setTargetType(taskParams.getString("targetType", "MYSQL"));
        params.setTargetTable(taskParams.getString("targetTable"));
        
        // 解析同步配置
        params.setSyncMode(taskParams.getString("syncMode", "FULL")); // FULL, INCREMENTAL
        params.setBatchSize(taskParams.getInt("batchSize", 10000));
        params.setConcurrency(taskParams.getInt("concurrency", 4));
        
        // 解析增量配置
        params.setIncrementalColumn(taskParams.getString("incrementalColumn", "id"));
        params.setLastSyncTime(taskParams.getDate("lastSyncTime"));
        
        return params;
    }
    
    // 创建数据同步引擎
    private DataSyncEngine createDataSyncEngine(DataSyncTaskParams params) {
        DataSyncEngine engine = new DataSyncEngine();
        
        // 设置源数据源
        DataSource sourceDataSource = dataSourceService.getDataSource(params.getSourceDataSourceId());
        engine.setSourceDataSource(sourceDataSource);
        engine.setSourceType(params.getSourceType());
        engine.setSourceTable(params.getSourceTable());
        
        // 设置目标数据源
        DataSource targetDataSource = dataSourceService.getDataSource(params.getTargetDataSourceId());
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
        
        return engine;
    }
    
    // 设置输出参数
    private void setOutputParameters(TaskExecutionContext context, DataSyncResult result) {
        // 设置同步记录数
        context.setOutputParam("sync_record_count", result.getSyncCount());
        
        // 设置同步耗时
        context.setOutputParam("sync_duration_ms", result.getDurationMs());
        
        // 设置下次同步时间
        context.setOutputParam("next_sync_time", result.getNextSyncTime());
        
        // 设置最大ID（增量同步）
        context.setOutputParam("max_incremental_id", result.getMaxIncrementalId());
    }
    
    // 记录执行日志
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
}

// 数据同步任务参数
public class DataSyncTaskParams {
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
}

// 数据同步引擎
public class DataSyncEngine {
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
                
                logger.info("Synced {}/{} records", syncCount, totalCount);
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
                updateLastSyncId(maxId);
                
                result.setMaxIncrementalId(maxId);
            }
            
            result.setSuccess(true);
            result.setSyncCount(records.size());
            result.setDurationMs(System.currentTimeMillis() - startTime);
            result.setNextSyncTime(calculateNextSyncTime());
        }
        
        return result;
    }
    
    // 其他辅助方法...
}

// 数据同步结果
public class DataSyncResult {
    private boolean success;
    private int syncCount;
    private long durationMs;
    private Date nextSyncTime;
    private long maxIncrementalId;
    private String errorMessage;
    private Exception exception;
    
    // Getters and Setters
}
```

#### 8.2.2.2 任务类型注册

```java
// 自定义任务类型注册器
@Component
public class CustomTaskTypeRegistrar {
    
    @Autowired
    private TaskPluginManager taskPluginManager;
    
    @PostConstruct
    public void registerCustomTaskTypes() {
        // 1. 注册数据同步任务
        registerDataSyncTask();
        
        // 2. 注册机器学习任务
        registerMLTask();
        
        // 3. 注册数据质量检查任务
        registerDataQualityTask();
    }
    
    // 注册数据同步任务
    private void registerDataSyncTask() {
        TaskPluginDescriptor descriptor = new TaskPluginDescriptor();
        descriptor.setName("DATASYNC");
        descriptor.setDisplayName("数据同步");
        descriptor.setDescription("用于在不同数据源之间同步数据");
        descriptor.setTaskClass(DataSyncTask.class);
        descriptor.setConfigClass(DataSyncTaskConfig.class);
        
        // 设置配置参数
        List<TaskPluginConfigParam> configParams = new ArrayList<>();
        
        // 源数据源
        TaskPluginConfigParam sourceDataSource = new TaskPluginConfigParam();
        sourceDataSource.setName("sourceDataSourceId");
        sourceDataSource.setLabel("源数据源");
        sourceDataSource.setType("DATASOURCE");
        sourceDataSource.setRequired(true);
        sourceDataSource.setPlaceholder("请选择源数据源");
        configParams.add(sourceDataSource);
        
        // 源表
        TaskPluginConfigParam sourceTable = new TaskPluginConfigParam();
        sourceTable.setName("sourceTable");
        sourceTable.setLabel("源表");
        sourceTable.setType("INPUT");
        sourceTable.setRequired(true);
        sourceTable.setPlaceholder("请输入源表名");
        configParams.add(sourceTable);
        
        // 目标数据源
        TaskPluginConfigParam targetDataSource = new TaskPluginConfigParam();
        targetDataSource.setName("targetDataSourceId");
        targetDataSource.setLabel("目标数据源");
        targetDataSource.setType("DATASOURCE");
        targetDataSource.setRequired(true);
        targetDataSource.setPlaceholder("请选择目标数据源");
        configParams.add(targetDataSource);
        
        // 目标表
        TaskPluginConfigParam targetTable = new TaskPluginConfigParam();
        targetTable.setName("targetTable");
        targetTable.setLabel("目标表");
        targetTable.setType("INPUT");
        targetTable.setRequired(true);
        targetTable.setPlaceholder("请输入目标表名");
        configParams.add(targetTable);
        
        // 同步模式
        TaskPluginConfigParam syncMode = new TaskPluginConfigParam();
        syncMode.setName("syncMode");
        syncMode.setLabel("同步模式");
        syncMode.setType("SELECT");
        syncMode.setRequired(true);
        syncMode.setDefaultValue("FULL");
        
        List<Option> syncModeOptions = new ArrayList<>();
        syncModeOptions.add(new Option("FULL", "全量同步"));
        syncModeOptions.add(new Option("INCREMENTAL", "增量同步"));
        syncMode.setOptions(syncModeOptions);
        configParams.add(syncMode);
        
        // 增量列
        TaskPluginConfigParam incrementalColumn = new TaskPluginConfigParam();
        incrementalColumn.setName("incrementalColumn");
        incrementalColumn.setLabel("增量列");
        incrementalColumn.setType("INPUT");
        incrementalColumn.setRequired(false);
        incrementalColumn.setPlaceholder("请输入增量列名，如id");
        configParams.add(incrementalColumn);
        
        // 批量大小
        TaskPluginConfigParam batchSize = new TaskPluginConfigParam();
        batchSize.setName("batchSize");
        batchSize.setLabel("批量大小");
        batchSize.setType("INPUT");
        batchSize.setRequired(false);
        batchSize.setDefaultValue("10000");
        configParams.add(batchSize);
        
        descriptor.setConfigParams(configParams);
        
        // 注册任务类型
        taskPluginManager.registerTaskPlugin(descriptor);
    }
    
    // 注册机器学习任务
    private void registerMLTask() {
        TaskPluginDescriptor descriptor = new TaskPluginDescriptor();
        descriptor.setName("MLTASK");
        descriptor.setDisplayName("机器学习");
        descriptor.setDescription("用于执行机器学习任务");
        descriptor.setTaskClass(MLTask.class);
        descriptor.setConfigClass(MLTaskConfig.class);
        
        // 设置配置参数
        List<TaskPluginConfigParam> configParams = new ArrayList<>();
        
        // 模型类型
        TaskPluginConfigParam modelType = new TaskPluginConfigParam();
        modelType.setName("modelType");
        modelType.setLabel("模型类型");
        modelType.setType("SELECT");
        modelType.setRequired(true);
        
        List<Option> modelTypeOptions = new ArrayList<>();
        modelTypeOptions.add(new Option("CLASSIFICATION", "分类"));
        modelTypeOptions.add(new Option("REGRESSION", "回归"));
        modelTypeOptions.add(new Option("CLUSTERING", "聚类"));
        modelType.setOptions(modelTypeOptions);
        configParams.add(modelType);
        
        // 算法
        TaskPluginConfigParam algorithm = new TaskPluginConfigParam();
        algorithm.setName("algorithm");
        algorithm.setLabel("算法");
        algorithm.setType("SELECT");
        algorithm.setRequired(true);
        
        List<Option> algorithmOptions = new ArrayList<>();
        algorithmOptions.add(new Option("RANDOM_FOREST", "随机森林"));
        algorithmOptions.add(new Option("XGBOOST", "XGBoost"));
        algorithmOptions.add(new Option("LOGISTIC_REGRESSION", "逻辑回归"));
        algorithmOptions.add(new Option("LINEAR_REGRESSION", "线性回归"));
        algorithmOptions.add(new Option("KMEANS", "K-Means"));
        algorithm.setOptions(algorithmOptions);
        configParams.add(algorithm);
        
        // 训练数据路径
        TaskPluginConfigParam trainDataPath = new TaskPluginConfigParam();
        trainDataPath.setName("trainDataPath");
        trainDataPath.setLabel("训练数据路径");
        trainDataPath.setType("INPUT");
        trainDataPath.setRequired(true);
        trainDataPath.setPlaceholder("请输入训练数据路径");
        configParams.add(trainDataPath);
        
        // 模型保存路径
        TaskPluginConfigParam modelSavePath = new TaskPluginConfigParam();
        modelSavePath.setName("modelSavePath");
        modelSavePath.setLabel("模型保存路径");
        modelSavePath.setType("INPUT");
        modelSavePath.setRequired(true);
        modelSavePath.setPlaceholder("请输入模型保存路径");
        configParams.add(modelSavePath);
        
        descriptor.setConfigParams(configParams);
        
        // 注册任务类型
        taskPluginManager.registerTaskPlugin(descriptor);
    }
    
    // 注册数据质量检查任务
    private void registerDataQualityTask() {
        TaskPluginDescriptor descriptor = new TaskPluginDescriptor();
        descriptor.setName("DATAQUALITY");
        descriptor.setDisplayName("数据质量检查");
        descriptor.setDescription("用于检查数据质量");
        descriptor.setTaskClass(DataQualityTask.class);
        descriptor.setConfigClass(DataQualityTaskConfig.class);
        
        // 设置配置参数
        List<TaskPluginConfigParam> configParams = new ArrayList<>();
        
        // 检查规则
        TaskPluginConfigParam checkRules = new TaskPluginConfigParam();
        checkRules.setName("checkRules");
        checkRules.setLabel("检查规则");
        checkRules.setType("TEXTAREA");
        checkRules.setRequired(true);
        checkRules.setPlaceholder("请输入检查规则，JSON格式");
        configParams.add(checkRules);
        
        // 数据源
        TaskPluginConfigParam dataSource = new TaskPluginConfigParam();
        dataSource.setName("dataSourceId");
        dataSource.setLabel("数据源");
        dataSource.setType("DATASOURCE");
        dataSource.setRequired(true);
        dataSource.setPlaceholder("请选择数据源");
        configParams.add(dataSource);
        
        // 表名
        TaskPluginConfigParam tableName = new TaskPluginConfigParam();
        tableName.setName("tableName");
        tableName.setLabel("表名");
        tableName.setType("INPUT");
        tableName.setRequired(true);
        tableName.setPlaceholder("请输入表名");
        configParams.add(tableName);
        
        descriptor.setConfigParams(configParams);
        
        // 注册任务类型
        taskPluginManager.registerTaskPlugin(descriptor);
    }
}
```

## 8.3 插件开发

### 8.3.1 插件概述

DolphinScheduler的插件系统允许开发者扩展系统的功能，包括任务插件、数据源插件、存储插件等。

### 8.3.2 任务插件开发

#### 8.3.2.1 任务插件接口

```java
// 任务插件接口
public interface TaskPlugin {
    
    // 获取插件名称
    String getName();
    
    // 获取插件显示名称
    String getDisplayName();
    
    // 获取插件描述
    String getDescription();
    
    // 获取配置参数
    List<TaskPluginConfigParam> getConfigParams();
    
    // 执行任务
    void execute(TaskExecutionContext context) throws Exception;
    
    // 验证配置
    ValidationResult validateConfig(Map<String, Object> config);
    
    // 停止任务
    void cancel(TaskExecutionContext context) throws Exception;
}

// 任务插件配置参数
public class TaskPluginConfigParam {
    private String name;
    private String label;
    private String type; // INPUT, SELECT, DATASOURCE, TEXTAREA, CHECKBOX
    private boolean required;
    private String placeholder;
    private String defaultValue;
    private List<Option> options; // 用于SELECT类型
    private List<String> values; // 用于CHECKBOX类型
    
    // Getters and Setters
}

// 选项
public class Option {
    private String value;
    private String label;
    
    public Option(String value, String label) {
        this.value = value;
        this.label = label;
    }
    
    // Getters and Setters
}
```

#### 8.3.2.2 自定义任务插件实现

```java
// 大数据ETL任务插件
public class BigDataETLTask implements TaskPlugin {
    
    @Override
    public String getName() {
        return "BIGDATA_ETL";
    }
    
    @Override
    public String getDisplayName() {
        return "大数据ETL";
    }
    
    @Override
    public String getDescription() {
        return "用于执行大数据ETL任务，支持Spark、Flink等引擎";
    }
    
    @Override
    public List<TaskPluginConfigParam> getConfigParams() {
        List<TaskPluginConfigParam> configParams = new ArrayList<>();
        
        // 引擎类型
        TaskPluginConfigParam engineType = new TaskPluginConfigParam();
        engineType.setName("engineType");
        engineType.setLabel("引擎类型");
        engineType.setType("SELECT");
        engineType.setRequired(true);
        
        List<Option> engineTypeOptions = new ArrayList<>();
        engineTypeOptions.add(new Option("SPARK", "Spark"));
        engineTypeOptions.add(new Option("FLINK", "Flink"));
        engineTypeOptions.add(new Option("MAPREDUCE", "MapReduce"));
        engineType.setOptions(engineTypeOptions);
        configParams.add(engineType);
        
        // ETL脚本
        TaskPluginConfigParam etlScript = new TaskPluginConfigParam();
        etlScript.setName("etlScript");
        etlScript.setLabel("ETL脚本");
        etlScript.setType("TEXTAREA");
        etlScript.setRequired(true);
        etlScript.setPlaceholder("请输入ETL脚本");
        configParams.add(etlScript);
        
        // 资源文件
        TaskPluginConfigParam resourceFiles = new TaskPluginConfigParam();
        resourceFiles.setName("resourceFiles");
        resourceFiles.setLabel("资源文件");
        resourceFiles.setType("RESOURCE");
        resourceFiles.setRequired(false);
        resourceFiles.setPlaceholder("请选择资源文件");
        configParams.add(resourceFiles);
        
        // 主类
        TaskPluginConfigParam mainClass = new TaskPluginConfigParam();
        mainClass.setName("mainClass");
        mainClass.setLabel("主类");
        mainClass.setType("INPUT");
        mainClass.setRequired(false);
        mainClass.setPlaceholder("请输入主类名（Java任务需要）");
        configParams.add(mainClass);
        
        // 执行参数
        TaskPluginConfigParam args = new TaskPluginConfigParam();
        args.setName("args");
        args.setLabel("执行参数");
        args.setType("INPUT");
        args.setRequired(false);
        args.setPlaceholder("请输入执行参数");
        configParams.add(args);
        
        // 内存配置
        TaskPluginConfigParam memory = new TaskPluginConfigParam();
        memory.setName("memory");
        memory.setLabel("内存配置");
        memory.setType("INPUT");
        memory.setRequired(false);
        memory.setDefaultValue("2g");
        memory.setPlaceholder("请输入内存配置，如2g");
        configParams.add(memory);
        
        // 核心数
        TaskPluginConfigParam cores = new TaskPluginConfigParam();
        cores.setName("cores");
        cores.setLabel("核心数");
        cores.setType("INPUT");
        cores.setRequired(false);
        cores.setDefaultValue("1");
        cores.setPlaceholder("请输入核心数");
        configParams.add(cores);
        
        return configParams;
    }
    
    @Override
    public void execute(TaskExecutionContext context) throws Exception {
        // 1. 解析配置参数
        BigDataETLConfig config = parseConfig(context);
        
        // 2. 准备执行环境
        prepareExecutionEnvironment(config, context);
        
        // 3. 执行ETL任务
        switch (config.getEngineType()) {
            case "SPARK":
                executeSparkETL(config, context);
                break;
            case "FLINK":
                executeFlinkETL(config, context);
                break;
            case "MAPREDUCE":
                executeMapReduceETL(config, context);
                break;
            default:
                throw new RuntimeException("Unsupported engine type: " + config.getEngineType());
        }
    }
    
    // 解析配置参数
    private BigDataETLConfig parseConfig(TaskExecutionContext context) {
        BigDataETLConfig config = new BigDataETLConfig();
        
        Map<String, String> taskParams = context.getTaskParams();
        
        config.setEngineType(taskParams.get("engineType"));
        config.setEtlScript(taskParams.get("etlScript"));
        config.setResourceFiles(taskParams.get("resourceFiles"));
        config.setMainClass(taskParams.get("mainClass"));
        config.setArgs(taskParams.get("args"));
        config.setMemory(taskParams.get("memory"));
        config.setCores(Integer.parseInt(taskParams.getOrDefault("cores", "1")));
        
        return config;
    }
    
    // 准备执行环境
    private void prepareExecutionEnvironment(BigDataETLConfig config, 
                                             TaskExecutionContext context) throws Exception {
        // 1. 创建工作目录
        String workingDir = context.getExecutePath();
        File workDir = new File(workingDir);
        if (!workDir.exists()) {
            workDir.mkdirs();
        }
        
        // 2. 创建ETL脚本文件
        String scriptFile = workingDir + File.separator + "etl_script.sh";
        try (PrintWriter writer = new PrintWriter(scriptFile)) {
            writer.println("#!/bin/bash");
            writer.println("set -euo pipefail");
            
            switch (config.getEngineType()) {
                case "SPARK":
                    writeSparkScript(writer, config);
                    break;
                case "FLINK":
                    writeFlinkScript(writer, config);
                    break;
                case "MAPREDUCE":
                    writeMapReduceScript(writer, config);
                    break;
            }
        }
        
        // 3. 下载资源文件
        if (config.getResourceFiles() != null && !config.getResourceFiles().isEmpty()) {
            String[] resourceFileIds = config.getResourceFiles().split(",");
            for (String fileId : resourceFileIds) {
                downloadResourceFile(fileId.trim(), workingDir);
            }
        }
        
        // 4. 设置脚本执行权限
        new File(scriptFile).setExecutable(true);
    }
    
    // 写入Spark脚本
    private void writeSparkScript(PrintWriter writer, BigDataETLConfig config) {
        writer.println("#!/bin/bash");
        writer.println("cd " + config.getWorkingDirectory());
        
        // 构建Spark submit命令
        StringBuilder sparkSubmitCmd = new StringBuilder();
        sparkSubmitCmd.append("spark-submit \\");
        
        // 添加资源配置
        sparkSubmitCmd.append("\n  --master yarn \\");
        sparkSubmitCmd.append("\n  --deploy-mode cluster \\");
        sparkSubmitCmd.append("\n  --executor-memory ").append(config.getMemory()).append(" \\");
        sparkSubmitCmd.append("\n  --executor-cores ").append(config.getCores()).append(" \\");
        sparkSubmitCmd.append("\n  --name dolphin-bigdata-etl \\");
        
        // 添加主类（如果是Java任务）
        if (config.getMainClass() != null && !config.getMainClass().isEmpty()) {
            sparkSubmitCmd.append("\n  --class ").append(config.getMainClass()).append(" \\");
        }
        
        // 添加资源文件
        if (config.getResourceFiles() != null && !config.getResourceFiles().isEmpty()) {
            String[] resourceFileIds = config.getResourceFiles().split(",");
            for (String fileId : resourceFileIds) {
                String fileName = getFileNameById(fileId.trim());
                sparkSubmitCmd.append("\n  --files ").append(fileName).append(" \\");
            }
        }
        
        // 添加ETL脚本或JAR包
        if (config.getMainClass() != null && !config.getMainClass().isEmpty()) {
            // Java任务，使用JAR包
            sparkSubmitCmd.append("\n  ").append(getJarFile()).append(" \\");
        } else {
            // Python/Scala任务，使用脚本
            sparkSubmitCmd.append("\n  --py-files ").append(getPyFiles()).append(" \\");
        }
        
        // 添加执行参数
        if (config.getArgs() != null && !config.getArgs().isEmpty()) {
            sparkSubmitCmd.append("\n  ").append(config.getArgs());
        } else {
            sparkSubmitCmd.append("\n  " + config.getEtlScript());
        }
        
        writer.println(sparkSubmitCmd.toString());
    }
    
    // 执行Spark ETL
    private void executeSparkETL(BigDataETLConfig config, TaskExecutionContext context) throws Exception {
        String workingDir = context.getExecutePath();
        String scriptFile = workingDir + File.separator + "etl_script.sh";
        
        // 执行脚本
        ProcessBuilder processBuilder = new ProcessBuilder("bash", scriptFile);
        processBuilder.directory(new File(workingDir));
        processBuilder.redirectErrorStream(true);
        
        Process process = processBuilder.start();
        
        // 设置任务PID
        context.setPid(process.pid());
        
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(process.getInputStream()))) {
            String line;
            while ((line = reader.readLine()) != null) {
                context.getLogger().info(line);
            }
        }
        
        // 等待进程结束
        int exitCode = process.waitFor();
        if (exitCode != 0) {
            throw new RuntimeException("Spark ETL execution failed with exit code: " + exitCode);
        }
    }
    
    // 其他执行方法...
    
    @Override
    public ValidationResult validateConfig(Map<String, Object> config) {
        ValidationResult result = new ValidationResult();
        
        // 验证引擎类型
        if (!config.containsKey("engineType")) {
            result.addError("engineType is required");
        } else {
            String engineType = config.get("engineType").toString();
            if (!Arrays.asList("SPARK", "FLINK", "MAPREDUCE").contains(engineType)) {
                result.addError("Invalid engineType: " + engineType);
            }
        }
        
        // 验证ETL脚本
        if (!config.containsKey("etlScript") || 
            config.get("etlScript").toString().trim().isEmpty()) {
            result.addError("etlScript is required");
        }
        
        // 验证Java任务的主类
        if ("SPARK".equals(config.get("engineType")) && 
            config.containsKey("mainClass") && 
            !config.get("mainClass").toString().trim().isEmpty()) {
            // Java任务需要验证主类格式
            String mainClass = config.get("mainClass").toString();
            if (!mainClass.matches("[a-zA-Z_$][a-zA-Z\\d_$]*\\.[a-zA-Z_$][a-zA-Z\\d_$]*")) {
                result.addError("Invalid main class format: " + mainClass);
            }
        }
        
        return result;
    }
    
    @Override
    public void cancel(TaskExecutionContext context) throws Exception {
        long pid = context.getPid();
        if (pid > 0) {
            // 通过PID终止进程
            Runtime.getRuntime().exec("kill -9 " + pid);
        }
    }
}

// 大数据ETL配置
public class BigDataETLConfig {
    private String engineType;
    private String etlScript;
    private String resourceFiles;
    private String mainClass;
    private String args;
    private String memory;
    private int cores;
    private String workingDirectory;
    
    // Getters and Setters
}
```

## 8.4 扩展开发实践

### 8.4.1 自定义告警插件开发

#### 8.4.1.1 告警插件接口

```java
// 告警插件接口
public interface AlertPlugin {
    
    // 获取插件名称
    String getName();
    
    // 获取插件显示名称
    String getDisplayName();
    
    // 获取插件描述
    String getDescription();
    
    // 获取配置参数
    List<AlertPluginConfigParam> getConfigParams();
    
    // 发送告警
    boolean sendAlert(AlertContext context);
    
    // 验证配置
    ValidationResult validateConfig(Map<String, Object> config);
}

// 告警插件配置参数
public class AlertPluginConfigParam {
    private String name;
    private String label;
    private String type; // INPUT, TEXTAREA, SELECT, CHECKBOX
    private boolean required;
    private String placeholder;
    private String defaultValue;
    private List<Option> options; // 用于SELECT类型
    private List<String> values; // 用于CHECKBOX类型
    
    // Getters and Setters
}

// 告警上下文
public class AlertContext {
    private String title;
    private String content;
    private Map<String, Object> variables;
    private List<AlertReceiver> receivers;
    
    // Getters and Setters
}

// 告警接收者
public class AlertReceiver {
    private String type; // EMAIL, SMS, WEBHOOK
    private String address;
    private Map<String, Object> metadata;
    
    // Getters and Setters
}
```

#### 8.4.1.2 自定义告警插件实现

```java
// 钉钉告警插件
public class DingTalkAlertPlugin implements AlertPlugin {
    
    private static final Logger logger = LoggerFactory.getLogger(DingTalkAlertPlugin.class);
    
    @Override
    public String getName() {
        return "DINGTALK";
    }
    
    @Override
    public String getDisplayName() {
        return "钉钉";
    }
    
    @Override
    public String getDescription() {
        return "通过钉钉机器人发送告警";
    }
    
    @Override
    public List<AlertPluginConfigParam> getConfigParams() {
        List<AlertPluginConfigParam> configParams = new ArrayList<>();
        
        // Webhook地址
        AlertPluginConfigParam webhook = new AlertPluginConfigParam();
        webhook.setName("webhook");
        webhook.setLabel("Webhook地址");
        webhook.setType("INPUT");
        webhook.setRequired(true);
        webhook.setPlaceholder("请输入钉钉机器人Webhook地址");
        configParams.add(webhook);
        
        // 密钥
        AlertPluginConfigParam secret = new AlertPluginConfigParam();
        secret.setName("secret");
        secret.setLabel("密钥");
        secret.setType("INPUT");
        secret.setRequired(false);
        secret.setPlaceholder("请输入钉钉机器人密钥（可选）");
        configParams.add(secret);
        
        // 提醒方式
        AlertPluginConfigParam alertType = new AlertPluginConfigParam();
        alertType.setName("alertType");
        alertType.setLabel("提醒方式");
        alertType.setType("SELECT");
        alertType.setRequired(true);
        alertType.setDefaultValue("all");
        
        List<Option> alertTypeOptions = new ArrayList<>();
        alertTypeOptions.add(new Option("all", "所有人"));
        alertTypeOptions.add(new Option("mobiles", "指定手机号"));
        alertTypeOptions.add(new Option("none", "不提醒"));
        alertType.setOptions(alertTypeOptions);
        configParams.add(alertType);
        
        // 手机号列表
        AlertPluginConfigParam mobiles = new AlertPluginConfigParam();
        mobiles.setName("mobiles");
        mobiles.setLabel("手机号列表");
        mobiles.setType("TEXTAREA");
        mobiles.setRequired(false);
        mobiles.setPlaceholder("请输入手机号列表，每行一个");
        configParams.add(mobiles);
        
        return configParams;
    }
    
    @Override
    public boolean sendAlert(AlertContext context) {
        try {
            // 1. 获取配置
            Map<String, Object> config = getConfig();
            String webhook = (String) config.get("webhook");
            String secret = (String) config.get("secret");
            String alertType = (String) config.getOrDefault("alertType", "all");
            List<String> mobiles = parseMobiles((String) config.get("mobiles"));
            
            // 2. 构建告警消息
            DingTalkMessage message = buildDingTalkMessage(context, alertType, mobiles);
            
            // 3. 签名
            if (secret != null && !secret.isEmpty()) {
                signMessage(message, secret);
            }
            
            // 4. 发送消息
            return sendDingTalkMessage(webhook, message);
        } catch (Exception e) {
            logger.error("Failed to send DingTalk alert", e);
            return false;
        }
    }
    
    // 构建钉钉消息
    private DingTalkMessage buildDingTalkMessage(AlertContext context, 
                                                 String alertType, List<String> mobiles) {
        DingTalkMessage message = new DingTalkMessage();
        message.setMsgtype("markdown");
        
        MarkdownContent content = new MarkdownContent();
        content.setTitle(context.getTitle());
        
        StringBuilder text = new StringBuilder();
        text.append("### ").append(context.getTitle()).append("\n\n");
        
        // 添加内容
        if (context.getContent() != null) {
            text.append(context.getContent()).append("\n\n");
        }
        
        // 添加变量
        if (context.getVariables() != null && !context.getVariables().isEmpty()) {
            text.append("#### 告警详情\n");
            for (Map.Entry<String, Object> entry : context.getVariables().entrySet()) {
                text.append("- **").append(entry.getKey()).append("**: ")
                     .append(entry.getValue()).append("\n");
            }
            text.append("\n");
        }
        
        // 添加时间戳
        text.append("#### 告警时间\n");
        text.append(new SimpleDateFormat("yyyy-MM-dd HH:mm:ss").format(new Date()));
        
        content.setText(text.toString());
        message.setMarkdown(content);
        
        // 设置提醒方式
        if ("all".equals(alertType)) {
            message.setAt(new At(true, null, true));
        } else if ("mobiles".equals(alertType) && !mobiles.isEmpty()) {
            message.setAt(new At(false, mobiles, false));
        }
        
        return message;
    }
    
    // 签名消息
    private void signMessage(DingTalkMessage message, String secret) throws Exception {
        long timestamp = System.currentTimeMillis();
        
        String sign = generateSign(timestamp, secret);
        
        String webhook = message.getWebhook();
        webhook = webhook + (webhook.contains("?") ? "&" : "?") 
                 + "timestamp=" + timestamp + "&sign=" + sign;
        
        message.setWebhook(webhook);
    }
    
    // 生成签名
    private String generateSign(long timestamp, String secret) throws Exception {
        String stringToSign = timestamp + "\n" + secret;
        
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
        byte[] signData = mac.doFinal(stringToSign.getBytes(StandardCharsets.UTF_8));
        
        return URLEncoder.encode(Base64.getEncoder().encodeToString(signData), "UTF-8");
    }
    
    // 解析手机号列表
    private List<String> parseMobiles(String mobilesStr) {
        if (mobilesStr == null || mobilesStr.trim().isEmpty()) {
            return Collections.emptyList();
        }
        
        List<String> mobiles = new ArrayList<>();
        String[] lines = mobilesStr.split("\n");
        for (String line : lines) {
            String mobile = line.trim();
            if (!mobile.isEmpty() && mobile.matches("\\d{11}")) {
                mobiles.add(mobile);
            }
        }
        
        return mobiles;
    }
    
    // 发送钉钉消息
    private boolean sendDingTalkMessage(String webhook, DingTalkMessage message) {
        try {
            CloseableHttpClient httpClient = HttpClients.createDefault();
            HttpPost httpPost = new HttpPost(webhook);
            
            String jsonMessage = JsonUtils.toJsonString(message);
            httpPost.setEntity(new StringEntity(jsonMessage, StandardCharsets.UTF_8));
            httpPost.setHeader("Content-Type", "application/json");
            
            try (CloseableHttpResponse response = httpClient.execute(httpPost)) {
                String responseBody = EntityUtils.toString(response.getEntity());
                DingTalkResponse dingTalkResponse = JsonUtils.parseObject(responseBody, DingTalkResponse.class);
                
                return dingTalkResponse.getErrcode() == 0;
            }
        } catch (Exception e) {
            logger.error("Failed to send DingTalk message", e);
            return false;
        }
    }
    
    @Override
    public ValidationResult validateConfig(Map<String, Object> config) {
        ValidationResult result = new ValidationResult();
        
        // 验证Webhook地址
        if (!config.containsKey("webhook") || 
            config.get("webhook").toString().trim().isEmpty()) {
            result.addError("webhook is required");
        } else {
            String webhook = config.get("webhook").toString();
            if (!webhook.startsWith("https://oapi.dingtalk.com/robot/send?access_token=")) {
                result.addError("Invalid webhook URL");
            }
        }
        
        // 验证提醒方式
        if (!config.containsKey("alertType")) {
            result.addError("alertType is required");
        } else {
            String alertType = config.get("alertType").toString();
            if (!Arrays.asList("all", "mobiles", "none").contains(alertType)) {
                result.addError("Invalid alertType: " + alertType);
            }
        }
        
        // 验证手机号列表（如果指定了mobiles提醒方式）
        if ("mobiles".equals(config.get("alertType")) && 
            (config.containsKey("mobiles") && !config.get("mobiles").toString().trim().isEmpty())) {
            String mobilesStr = config.get("mobiles").toString();
            String[] lines = mobilesStr.split("\n");
            
            for (String line : lines) {
                String mobile = line.trim();
                if (!mobile.isEmpty() && !mobile.matches("\\d{11}")) {
                    result.addError("Invalid mobile number: " + mobile);
                }
            }
        }
        
        return result;
    }
}

// 钉钉消息
public class DingTalkMessage {
    private String msgtype;
    private String webhook;
    private MarkdownContent markdown;
    private At at;
    
    // Getters and Setters
}

// Markdown内容
public class MarkdownContent {
    private String title;
    private String text;
    
    // Getters and Setters
}

// At信息
public class At {
    private boolean isAtAll;
    private List<String> atMobiles;
    private boolean isAtAllInContent;
    
    public At(boolean isAtAll, List<String> atMobiles, boolean isAtAllInContent) {
        this.isAtAll = isAtAll;
        this.atMobiles = atMobiles;
        this.isAtAllInContent = isAtAllInContent;
    }
    
    // Getters and Setters
}

// 钉钉响应
public class DingTalkResponse {
    private int errcode;
    private String errmsg;
    
    // Getters and Setters
}
```

## 8.5 实践案例

### 8.5.1 自定义数据同步任务

#### 8.5.1.1 场景描述

开发一个自定义数据同步任务，支持多种数据源之间的数据同步，并提供增量同步功能。

#### 8.5.1.2 实现步骤

1. 创建任务插件实现类
2. 实现任务执行逻辑
3. 注册任务插件
4. 测试任务插件

### 8.5.2 自定义告警渠道

#### 8.5.2.1 场景描述

开发一个自定义告警渠道，通过企业微信发送告警通知。

#### 8.5.2.2 实现步骤

1. 创建告警插件实现类
2. 实现告警发送逻辑
3. 注册告警插件
4. 配置告警规则

## 8.6 小结

本章详细介绍了DolphinScheduler的API使用与扩展开发：

1. **REST API使用**：API认证、项目管理和工作流管理
2. **自定义任务类型开发**：任务接口实现和参数配置
3. **插件开发**：任务插件和告警插件的开发
4. **实践案例**：自定义数据同步任务和告警渠道

通过本章的学习，您应该能够：

- 使用REST API管理DolphinScheduler资源
- 开发自定义任务类型
- 创建插件扩展系统功能
- 构建集成解决方案

至此，我们已经完成了DolphinScheduler从入门到专家的完整教程。希望这些内容能够帮助您在实际工作中更好地使用和扩展DolphinScheduler！