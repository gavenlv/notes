import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.HashMap;
import java.util.Map;

/**
 * DolphinScheduler项目管理API客户端示例
 */
public class ProjectApiClient {
    
    private String baseUrl;
    private String token;
    private HttpClient httpClient;
    
    public ProjectApiClient(String baseUrl, String username, String password) {
        this.baseUrl = baseUrl.endsWith("/") ? baseUrl.substring(0, baseUrl.length() - 1) : baseUrl;
        this.httpClient = HttpClient.newHttpClient();
        
        // 登录获取Token
        this.token = login(username, password);
    }
    
    /**
     * 登录获取Token
     */
    private String login(String username, String password) {
        try {
            String loginUrl = baseUrl + "/login";
            
            String requestBody = String.format("userName=%s&userPassword=%s", 
                                             username, password);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(loginUrl))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() != 200) {
                throw new RuntimeException("Login failed with status code: " + response.statusCode());
            }
            
            // 简单解析响应获取token
            String responseBody = response.body();
            int tokenStart = responseBody.indexOf("\"token\":\"") + 9;
            int tokenEnd = responseBody.indexOf("\"", tokenStart);
            
            if (tokenStart > 8 && tokenEnd > tokenStart) {
                return responseBody.substring(tokenStart, tokenEnd);
            }
            
            throw new RuntimeException("Failed to parse token from response");
        } catch (Exception e) {
            throw new RuntimeException("Login error", e);
        }
    }
    
    /**
     * 创建项目
     */
    public Map<String, Object> createProject(String projectName, String description) {
        try {
            String url = baseUrl + "/projects";
            
            String requestBody = String.format(
                "{\"projectName\":\"%s\",\"description\":\"%s\"}", 
                projectName, description);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + token)
                .POST(HttpRequest.BodyPublishers.ofString(requestBody))
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() != 200) {
                throw new RuntimeException("Create project failed with status code: " + response.statusCode());
            }
            
            // 简单解析响应
            return parseResponse(response.body());
        } catch (Exception e) {
            throw new RuntimeException("Create project error", e);
        }
    }
    
    /**
     * 获取项目详情
     */
    public Map<String, Object> getProject(int projectId) {
        try {
            String url = baseUrl + "/projects/" + projectId;
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Authorization", "Bearer " + token)
                .GET()
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() != 200) {
                throw new RuntimeException("Get project failed with status code: " + response.statusCode());
            }
            
            return parseResponse(response.body());
        } catch (Exception e) {
            throw new RuntimeException("Get project error", e);
        }
    }
    
    /**
     * 更新项目
     */
    public Map<String, Object> updateProject(int projectId, String projectName, String description) {
        try {
            String url = baseUrl + "/projects/" + projectId;
            
            String requestBody = String.format(
                "{\"projectName\":\"%s\",\"description\":\"%s\"}", 
                projectName, description);
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Content-Type", "application/json")
                .header("Authorization", "Bearer " + token)
                .PUT(HttpRequest.BodyPublishers.ofString(requestBody))
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() != 200) {
                throw new RuntimeException("Update project failed with status code: " + response.statusCode());
            }
            
            return parseResponse(response.body());
        } catch (Exception e) {
            throw new RuntimeException("Update project error", e);
        }
    }
    
    /**
     * 删除项目
     */
    public void deleteProject(int projectId) {
        try {
            String url = baseUrl + "/projects/" + projectId;
            
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(url))
                .header("Authorization", "Bearer " + token)
                .DELETE()
                .build();
            
            HttpResponse<String> response = httpClient.send(request, HttpResponse.BodyHandlers.ofString());
            
            if (response.statusCode() != 200) {
                throw new RuntimeException("Delete project failed with status code: " + response.statusCode());
            }
        } catch (Exception e) {
            throw new RuntimeException("Delete project error", e);
        }
    }
    
    /**
     * 简单解析API响应
     */
    private Map<String, Object> parseResponse(String responseBody) {
        // 这里应该使用JSON库如Gson或Jackson进行解析
        // 为了简化示例，使用简单的字符串处理
        Map<String, Object> result = new HashMap<>();
        
        // 解析code
        int codeIndex = responseBody.indexOf("\"code\":");
        if (codeIndex >= 0) {
            int valueStart = codeIndex + 7;
            int valueEnd = responseBody.indexOf(",", valueStart);
            if (valueEnd < 0) valueEnd = responseBody.indexOf("}", valueStart);
            
            if (valueEnd > valueStart) {
                String codeStr = responseBody.substring(valueStart, valueEnd);
                result.put("code", Integer.parseInt(codeStr));
            }
        }
        
        // 解析msg
        int msgIndex = responseBody.indexOf("\"msg\":");
        if (msgIndex >= 0) {
            int valueStart = msgIndex + 6;
            int valueEnd = responseBody.indexOf(",", valueStart);
            if (valueEnd < 0) valueEnd = responseBody.indexOf("}", valueStart);
            
            if (valueEnd > valueStart) {
                String msgStr = responseBody.substring(valueStart + 1, valueEnd - 1);
                result.put("msg", msgStr);
            }
        }
        
        // 解析data
        int dataIndex = responseBody.indexOf("\"data\":");
        if (dataIndex >= 0) {
            int valueStart = dataIndex + 7;
            int valueEnd = responseBody.indexOf("}", valueStart) + 1;
            
            if (valueEnd > valueStart) {
                String dataStr = responseBody.substring(valueStart, valueEnd);
                result.put("data", dataStr);
            }
        }
        
        return result;
    }
    
    public static void main(String[] args) {
        try {
            // 1. 创建API客户端
            ProjectApiClient client = new ProjectApiClient(
                "http://localhost:12345", "admin", "dolphinscheduler123");
            
            // 2. 创建项目
            Map<String, Object> project = client.createProject("data_warehouse", "数据仓库项目");
            System.out.println("Created project response: " + project);
            
            // 3. 获取项目详情
            // 假设项目ID为1（实际应从响应中获取）
            project = client.getProject(1);
            System.out.println("Project details: " + project);
            
            // 4. 更新项目
            project = client.updateProject(1, "data_warehouse_v2", "数据仓库项目v2");
            System.out.println("Updated project response: " + project);
            
            // 5. 删除项目
            client.deleteProject(1);
            System.out.println("Project deleted");
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}