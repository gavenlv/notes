import org.apache.dolphinscheduler.alert.api.AlertChannel;
import org.apache.dolphinscheduler.alert.api.AlertChannelFactory;
import org.apache.dolphinscheduler.alert.api.AlertConstants;
import org.apache.dolphinscheduler.alert.api.AlertData;
import org.apache.dolphinscheduler.alert.api.AlertInfo;
import org.apache.dolphinscheduler.alert.api.AlertResult;
import org.apache.dolphinscheduler.spi.params.base.PluginParams;
import org.apache.dolphinscheduler.spi.params.base.ParamsOptions;
import org.apache.dolphinscheduler.spi.params.base.PluginParamsProperty;
import org.apache.dolphinscheduler.spi.params.base.Validate;
import org.apache.dolphinscheduler.spi.params.base.input.InputParam;
import org.apache.dolphinscheduler.spi.params.base.select.SelectParam;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.security.InvalidKeyException;
import java.security.NoSuchAlgorithmException;
import java.time.Duration;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Base64;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

import javax.crypto.Mac;
import javax.crypto.spec.SecretKeySpec;

import com.google.gson.Gson;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

/**
 * 钉钉告警插件
 */
public class DingTalkAlertPlugin implements AlertChannel {
    
    private static final Logger logger = LoggerFactory.getLogger(DingTalkAlertPlugin.class);
    private static final Gson gson = new Gson();
    
    @Override
    public AlertResult send(AlertInfo alertInfo) {
        try {
            // 1. 获取配置
            Map<String, String> paramsMap = alertInfo.getAlertParams();
            String webhook = paramsMap.get("webhook");
            String secret = paramsMap.get("secret");
            String alertType = paramsMap.getOrDefault("alertType", "all");
            String mobiles = paramsMap.get("mobiles");
            
            // 2. 构建告警消息
            DingTalkMessage message = buildDingTalkMessage(alertInfo, alertType, mobiles);
            
            // 3. 签名
            if (secret != null && !secret.isEmpty()) {
                signMessage(message, secret);
            } else {
                message.setWebhook(webhook);
            }
            
            // 4. 发送消息
            return sendDingTalkMessage(message);
        } catch (Exception e) {
            logger.error("Failed to send DingTalk alert", e);
            AlertResult alertResult = new AlertResult();
            alertResult.setStatus("false");
            alertResult.setMessage("Failed to send DingTalk alert: " + e.getMessage());
            return alertResult;
        }
    }
    
    /**
     * 构建钉钉消息
     */
    private DingTalkMessage buildDingTalkMessage(AlertInfo alertInfo, 
                                                 String alertType, String mobiles) {
        DingTalkMessage message = new DingTalkMessage();
        message.setMsgtype("markdown");
        
        MarkdownContent content = new MarkdownContent();
        content.setTitle(alertInfo.getAlertTitle());
        
        StringBuilder text = new StringBuilder();
        text.append("### ").append(alertInfo.getAlertTitle()).append("\n\n");
        
        // 添加内容
        if (alertInfo.getContent() != null) {
            text.append(alertInfo.getContent()).append("\n\n");
        }
        
        // 添加告警详情
        text.append("#### 告警详情\n");
        text.append("- **告警类型**: ").append(alertInfo.getAlertType()).append("\n");
        text.append("- **告警时间**: ").append(alertInfo.getCreateTime()).append("\n");
        text.append("- **告警内容**: ").append(alertInfo.getAlertContent()).append("\n");
        
        content.setText(text.toString());
        message.setMarkdown(content);
        
        // 设置提醒方式
        if ("all".equals(alertType)) {
            message.setAt(new At(true, null, true));
        } else if ("mobiles".equals(alertType) && mobiles != null && !mobiles.trim().isEmpty()) {
            List<String> mobileList = Arrays.asList(mobiles.split(","));
            message.setAt(new At(false, mobileList, false));
        }
        
        return message;
    }
    
    /**
     * 签名消息
     */
    private void signMessage(DingTalkMessage message, String secret) 
        throws NoSuchAlgorithmException, InvalidKeyException {
        long timestamp = System.currentTimeMillis();
        
        String sign = generateSign(timestamp, secret);
        
        String webhook = message.getWebhook();
        webhook = webhook + (webhook.contains("?") ? "&" : "?") 
                 + "timestamp=" + timestamp + "&sign=" + sign;
        
        message.setWebhook(webhook);
    }
    
    /**
     * 生成签名
     */
    private String generateSign(long timestamp, String secret) 
        throws NoSuchAlgorithmException, InvalidKeyException {
        String stringToSign = timestamp + "\n" + secret;
        
        Mac mac = Mac.getInstance("HmacSHA256");
        mac.init(new SecretKeySpec(secret.getBytes(StandardCharsets.UTF_8), "HmacSHA256"));
        byte[] signData = mac.doFinal(stringToSign.getBytes(StandardCharsets.UTF_8));
        
        return java.net.URLEncoder.encode(
            Base64.getEncoder().encodeToString(signData), StandardCharsets.UTF_8);
    }
    
    /**
     * 发送钉钉消息
     */
    private AlertResult sendDingTalkMessage(DingTalkMessage message) {
        AlertResult alertResult = new AlertResult();
        
        try {
            HttpClient httpClient = HttpClient.newBuilder()
                .connectTimeout(Duration.ofSeconds(10))
                .build();
            
            String jsonMessage = gson.toJson(message);
            HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(message.getWebhook()))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonMessage))
                .build();
            
            HttpResponse<String> response = httpClient.send(request, 
                                                        HttpResponse.BodyHandlers.ofString());
            
            String responseBody = response.body();
            logger.info("DingTalk response: {}", responseBody);
            
            DingTalkResponse dingTalkResponse = gson.fromJson(responseBody, DingTalkResponse.class);
            
            if (dingTalkResponse.getErrcode() == 0) {
                alertResult.setStatus("true");
                alertResult.setMessage("DingTalk alert sent successfully");
            } else {
                alertResult.setStatus("false");
                alertResult.setMessage("DingTalk alert failed: " + dingTalkResponse.getErrmsg());
            }
            
        } catch (Exception e) {
            logger.error("Failed to send DingTalk message", e);
            alertResult.setStatus("false");
            alertResult.setMessage("Failed to send DingTalk message: " + e.getMessage());
        }
        
        return alertResult;
    }
    
    /**
     * 钉钉消息
     */
    public static class DingTalkMessage {
        private String msgtype;
        private String webhook;
        private MarkdownContent markdown;
        private At at;
        
        // Getters and Setters
        public String getMsgtype() {
            return msgtype;
        }
        
        public void setMsgtype(String msgtype) {
            this.msgtype = msgtype;
        }
        
        public String getWebhook() {
            return webhook;
        }
        
        public void setWebhook(String webhook) {
            this.webhook = webhook;
        }
        
        public MarkdownContent getMarkdown() {
            return markdown;
        }
        
        public void setMarkdown(MarkdownContent markdown) {
            this.markdown = markdown;
        }
        
        public At getAt() {
            return at;
        }
        
        public void setAt(At at) {
            this.at = at;
        }
    }
    
    /**
     * Markdown内容
     */
    public static class MarkdownContent {
        private String title;
        private String text;
        
        // Getters and Setters
        public String getTitle() {
            return title;
        }
        
        public void setTitle(String title) {
            this.title = title;
        }
        
        public String getText() {
            return text;
        }
        
        public void setText(String text) {
            this.text = text;
        }
    }
    
    /**
     * At信息
     */
    public static class At {
        private boolean isAtAll;
        private List<String> atMobiles;
        private boolean isAtAllInContent;
        
        public At(boolean isAtAll, List<String> atMobiles, boolean isAtAllInContent) {
            this.isAtAll = isAtAll;
            this.atMobiles = atMobiles;
            this.isAtAllInContent = isAtAllInContent;
        }
        
        // Getters and Setters
        public boolean isAtAll() {
            return isAtAll;
        }
        
        public void setAtAll(boolean isAtAll) {
            this.isAtAll = isAtAll;
        }
        
        public List<String> getAtMobiles() {
            return atMobiles;
        }
        
        public void setAtMobiles(List<String> atMobiles) {
            this.atMobiles = atMobiles;
        }
        
        public boolean isAtAllInContent() {
            return isAtAllInContent;
        }
        
        public void setAtAllInContent(boolean isAtAllInContent) {
            this.isAtAllInContent = isAtAllInContent;
        }
    }
    
    /**
     * 钉钉响应
     */
    public static class DingTalkResponse {
        private int errcode;
        private String errmsg;
        
        // Getters and Setters
        public int getErrcode() {
            return errcode;
        }
        
        public void setErrcode(int errcode) {
            this.errcode = errcode;
        }
        
        public String getErrmsg() {
            return errmsg;
        }
        
        public void setErrmsg(String errmsg) {
            this.errmsg = errmsg;
        }
    }
    
    /**
     * 钉钉告警渠道工厂
     */
    public static class DingTalkAlertChannelFactory implements AlertChannelFactory {
        
        @Override
        public String getName() {
            return "DingTalk";
        }
        
        @Override
        public List<PluginParams> getParams() {
            List<PluginParams> paramsList = new ArrayList<>();
            
            // Webhook地址
            InputParam webhookParam = InputParam.newBuilder(PluginParamsProperty.newBuilder()
                    .name("webhook")
                    .desc("Webhook地址")
                    .placeholder("请输入钉钉机器人Webhook地址")
                    .type(PluginParamsProperty.Type.STRING)
                    .required(true)
                    .build())
                .setValue("")
                .addValidate(Validate.newBuilder()
                    .setRequired(true)
                    .setMessage("Webhook地址不能为空")
                    .build())
                .build();
            
            // 密钥
            InputParam secretParam = InputParam.newBuilder(PluginParamsProperty.newBuilder()
                    .name("secret")
                    .desc("密钥")
                    .placeholder("请输入钉钉机器人密钥（可选）")
                    .type(PluginParamsProperty.Type.STRING)
                    .required(false)
                    .build())
                .setValue("")
                .build();
            
            // 提醒方式
            ParamsOptions[] alertTypeOptions = new ParamsOptions[]{
                    new ParamsOptions("所有人", "all"),
                    new ParamsOptions("指定手机号", "mobiles"),
                    new ParamsOptions("不提醒", "none")
            };
            
            SelectParam alertTypeParam = SelectParam.newBuilder(PluginParamsProperty.newBuilder()
                    .name("alertType")
                    .desc("提醒方式")
                    .type(PluginParamsProperty.Type.SELECT)
                    .required(true)
                    .options(alertTypeOptions)
                    .defaultValue("all")
                    .build())
                .setValue("all")
                .build();
            
            // 手机号列表
            InputParam mobilesParam = InputParam.newBuilder(PluginParamsProperty.newBuilder()
                    .name("mobiles")
                    .desc("手机号列表")
                    .placeholder("请输入手机号列表，逗号分隔")
                    .type(PluginParamsProperty.Type.STRING)
                    .required(false)
                    .dependency("alertType", "mobiles")
                    .build())
                .setValue("")
                .build();
            
            paramsList.add(webhookParam);
            paramsList.add(secretParam);
            paramsList.add(alertTypeParam);
            paramsList.add(mobilesParam);
            
            return paramsList;
        }
        
        @Override
        public Map<String, Object> webHookParams(Map<String, String> params) {
            Map<String, Object> result = new HashMap<>();
            
            // 验证Webhook地址
            if (!params.containsKey("webhook") || 
                params.get("webhook").trim().isEmpty()) {
                throw new RuntimeException("webhook is required");
            }
            
            String webhook = params.get("webhook");
            if (!webhook.startsWith("https://oapi.dingtalk.com/robot/send?access_token=")) {
                throw new RuntimeException("Invalid webhook URL");
            }
            
            // 验证提醒方式
            if (!params.containsKey("alertType")) {
                throw new RuntimeException("alertType is required");
            }
            
            String alertType = params.get("alertType");
            if (!Arrays.asList("all", "mobiles", "none").contains(alertType)) {
                throw new RuntimeException("Invalid alertType: " + alertType);
            }
            
            // 验证手机号列表（如果指定了mobiles提醒方式）
            if ("mobiles".equals(alertType) && 
                params.containsKey("mobiles") && !params.get("mobiles").trim().isEmpty()) {
                String mobilesStr = params.get("mobiles");
                String[] mobiles = mobilesStr.split(",");
                
                for (String mobile : mobiles) {
                    String trimmedMobile = mobile.trim();
                    if (!trimmedMobile.isEmpty() && !trimmedMobile.matches("\\d{11}")) {
                        throw new RuntimeException("Invalid mobile number: " + trimmedMobile);
                    }
                }
            }
            
            result.put("webhook", params.get("webhook"));
            result.put("secret", params.getOrDefault("secret", ""));
            result.put("alertType", alertType);
            result.put("mobiles", params.getOrDefault("mobiles", ""));
            
            return result;
        }
        
        @Override
        public AlertChannel create() {
            return new DingTalkAlertPlugin();
        }
    }
}