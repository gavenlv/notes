package com.example.restassured.advanced;

import io.restassured.response.Response;
import org.apache.commons.lang3.StringUtils;
import org.json.JSONArray;
import org.json.JSONObject;
import org.json.JSONTokener;

import java.util.*;
import java.util.function.Function;
import java.util.regex.Pattern;

import static org.hamcrest.CoreMatchers.*;
import static org.hamcrest.MatcherAssert.assertThat;
import static org.hamcrest.Matchers.*;

/**
 * 响应验证器
 * 提供高级响应验证功能，包括复杂JSON结构验证、数据完整性检查等
 */
public class ResponseValidator {
    
    private Response response;
    private List<ValidationError> validationErrors = new ArrayList<>();
    
    public ResponseValidator(Response response) {
        this.response = response;
    }
    
    /**
     * 验证响应状态码
     */
    public ResponseValidator assertStatusCode(int expectedStatusCode) {
        int actualStatusCode = response.getStatusCode();
        if (actualStatusCode != expectedStatusCode) {
            validationErrors.add(new ValidationError(
                "status_code", 
                "Expected status code " + expectedStatusCode + " but got " + actualStatusCode
            ));
        }
        return this;
    }
    
    /**
     * 验证响应内容类型
     */
    public ResponseValidator assertContentType(String expectedContentType) {
        String actualContentType = response.getContentType();
        if (actualContentType == null || !actualContentType.contains(expectedContentType)) {
            validationErrors.add(new ValidationError(
                "content_type", 
                "Expected content type to contain '" + expectedContentType + "' but got '" + actualContentType + "'"
            ));
        }
        return this;
    }
    
    /**
     * 验证响应时间不超过指定毫秒数
     */
    public ResponseValidator assertResponseTimeLessThan(long maxTimeMs) {
        long actualTime = response.getTime();
        if (actualTime > maxTimeMs) {
            validationErrors.add(new ValidationError(
                "response_time", 
                "Response time " + actualTime + "ms exceeded maximum " + maxTimeMs + "ms"
            ));
        }
        return this;
    }
    
    /**
     * 验证响应头
     */
    public ResponseValidator assertHeader(String headerName, String expectedValue) {
        String actualValue = response.getHeader(headerName);
        if (!StringUtils.equals(actualValue, expectedValue)) {
            validationErrors.add(new ValidationError(
                "header:" + headerName, 
                "Expected header '" + headerName + "' to be '" + expectedValue + "' but got '" + actualValue + "'"
            ));
        }
        return this;
    }
    
    /**
     * 验证响应头存在
     */
    public ResponseValidator assertHeaderExists(String headerName) {
        String actualValue = response.getHeader(headerName);
        if (actualValue == null) {
            validationErrors.add(new ValidationError(
                "header:" + headerName, 
                "Expected header '" + headerName + "' to be present"
            ));
        }
        return this;
    }
    
    /**
     * 验证响应体包含指定JSON路径的值
     */
    public ResponseValidator assertJsonPath(String jsonPath, Object expectedValue) {
        try {
            Object actualValue = response.jsonPath().get(jsonPath);
            
            if (expectedValue == null && actualValue != null) {
                validationErrors.add(new ValidationError(
                    "json_path:" + jsonPath, 
                    "Expected null but got '" + actualValue + "'"
                ));
            } else if (expectedValue != null && !expectedValue.equals(actualValue)) {
                validationErrors.add(new ValidationError(
                    "json_path:" + jsonPath, 
                    "Expected '" + expectedValue + "' but got '" + actualValue + "'"
                ));
            }
        } catch (Exception e) {
            validationErrors.add(new ValidationError(
                "json_path:" + jsonPath, 
                "Failed to extract value: " + e.getMessage()
            ));
        }
        return this;
    }
    
    /**
     * 验证响应体包含指定JSON路径的值（使用Hamcrest匹配器）
     */
    public ResponseValidator assertJsonPath(String jsonPath, org.hamcrest.Matcher<?> matcher) {
        try {
            Object actualValue = response.jsonPath().get(jsonPath);
            assertThat("JSON Path: " + jsonPath, actualValue, matcher);
        } catch (AssertionError e) {
            validationErrors.add(new ValidationError(
                "json_path:" + jsonPath, 
                "Value does not match matcher: " + e.getMessage()
            ));
        } catch (Exception e) {
            validationErrors.add(new ValidationError(
                "json_path:" + jsonPath, 
                "Failed to extract value: " + e.getMessage()
            ));
        }
        return this;
    }
    
    /**
     * 验证JSON响应中的字段存在
     */
    public ResponseValidator assertFieldExists(String fieldName) {
        return assertJsonPath(fieldName, notNullValue());
    }
    
    /**
     * 验证JSON响应中的字段不存在
     */
    public ResponseValidator assertFieldNotExists(String fieldName) {
        try {
            Object value = response.jsonPath().get(fieldName);
            if (value != null) {
                validationErrors.add(new ValidationError(
                    "field_exists:" + fieldName, 
                    "Field '" + fieldName + "' should not exist but found value: " + value
                ));
            }
        } catch (Exception e) {
            // 字段不存在，这是预期的
        }
        return this;
    }
    
    /**
     * 验证数组大小
     */
    public ResponseValidator assertArraySize(String jsonPath, int expectedSize) {
        try {
            List<Object> array = response.jsonPath().getList(jsonPath);
            if (array == null || array.size() != expectedSize) {
                validationErrors.add(new ValidationError(
                    "array_size:" + jsonPath, 
                    "Expected array size " + expectedSize + " but got " + 
                    (array == null ? "null" : array.size())
                ));
            }
        } catch (Exception e) {
            validationErrors.add(new ValidationError(
                "array_size:" + jsonPath, 
                "Failed to extract array: " + e.getMessage()
            ));
        }
        return this;
    }
    
    /**
     * 验证数组不为空
     */
    public ResponseValidator assertArrayNotEmpty(String jsonPath) {
        try {
            List<Object> array = response.jsonPath().getList(jsonPath);
            if (array == null || array.isEmpty()) {
                validationErrors.add(new ValidationError(
                    "array_empty:" + jsonPath, 
                    "Expected non-empty array"
                ));
            }
        } catch (Exception e) {
            validationErrors.add(new ValidationError(
                "array_empty:" + jsonPath, 
                "Failed to extract array: " + e.getMessage()
            ));
        }
        return this;
    }
    
    /**
     * 验证字符串字段匹配正则表达式
     */
    public ResponseValidator assertStringMatches(String jsonPath, String regexPattern) {
        try {
            String value = response.jsonPath().getString(jsonPath);
            if (value == null) {
                validationErrors.add(new ValidationError(
                    "string_match:" + jsonPath, 
                    "Expected string value but got null"
                ));
            } else if (!Pattern.matches(regexPattern, value)) {
                validationErrors.add(new ValidationError(
                    "string_match:" + jsonPath, 
                    "Value '" + value + "' does not match pattern '" + regexPattern + "'"
                ));
            }
        } catch (Exception e) {
            validationErrors.add(new ValidationError(
                "string_match:" + jsonPath, 
                "Failed to extract value: " + e.getMessage()
            ));
        }
        return this;
    }
    
    /**
     * 验证数值字段在指定范围内
     */
    public ResponseValidator assertNumberInRange(String jsonPath, Number min, Number max) {
        try {
            Number value = response.jsonPath().get(jsonPath);
            if (value == null) {
                validationErrors.add(new ValidationError(
                    "number_range:" + jsonPath, 
                    "Expected numeric value but got null"
                ));
            } else {
                double doubleValue = value.doubleValue();
                if (doubleValue < min.doubleValue() || doubleValue > max.doubleValue()) {
                    validationErrors.add(new ValidationError(
                        "number_range:" + jsonPath, 
                        "Value " + doubleValue + " is not in range [" + min + ", " + max + "]"
                    ));
                }
            }
        } catch (Exception e) {
            validationErrors.add(new ValidationError(
                "number_range:" + jsonPath, 
                "Failed to extract value: " + e.getMessage()
            ));
        }
        return this;
    }
    
    /**
     * 验证字段值在指定列表中
     */
    public ResponseValidator assertValueInList(String jsonPath, List<?> allowedValues) {
        try {
            Object value = response.jsonPath().get(jsonPath);
            if (value == null) {
                validationErrors.add(new ValidationError(
                    "value_in_list:" + jsonPath, 
                    "Expected value but got null"
                ));
            } else if (!allowedValues.contains(value)) {
                validationErrors.add(new ValidationError(
                    "value_in_list:" + jsonPath, 
                    "Value '" + value + "' is not in allowed list: " + allowedValues
                ));
            }
        } catch (Exception e) {
            validationErrors.add(new ValidationError(
                "value_in_list:" + jsonPath, 
                "Failed to extract value: " + e.getMessage()
            ));
        }
        return this;
    }
    
    /**
     * 验证响应JSON与预期JSON匹配
     */
    public ResponseValidator assertJsonEquals(String expectedJson) {
        try {
            String actualJson = response.getBody().asString();
            
            JSONTokener actualTokener = new JSONTokener(actualJson);
            JSONTokener expectedTokener = new JSONTokener(expectedJson);
            
            Object actualObject;
            Object expectedObject;
            
            // 判断是对象还是数组
            char actualFirstChar = actualJson.trim().charAt(0);
            char expectedFirstChar = expectedJson.trim().charAt(0);
            
            if (actualFirstChar == '{' && expectedFirstChar == '{') {
                actualObject = new JSONObject(actualTokener);
                expectedObject = new JSONObject(expectedTokener);
            } else if (actualFirstChar == '[' && expectedFirstChar == '[') {
                actualObject = new JSONArray(actualTokener);
                expectedObject = new JSONArray(expectedTokener);
            } else {
                validationErrors.add(new ValidationError(
                    "json_equals", 
                    "JSON structure mismatch: one is an object, the other is an array"
                ));
                return this;
            }
            
            // 比较JSON结构
            if (!actualObject.equals(expectedObject)) {
                validationErrors.add(new ValidationError(
                    "json_equals", 
                    "Actual JSON does not match expected JSON"
                ));
            }
        } catch (Exception e) {
            validationErrors.add(new ValidationError(
                "json_equals", 
                "Failed to compare JSON: " + e.getMessage()
            ));
        }
        return this;
    }
    
    /**
     * 验证响应包含预期JSON的子集
     */
    public ResponseValidator assertJsonContains(String expectedJson) {
        try {
            String actualJson = response.getBody().asString();
            
            JSONObject actualObject = new JSONObject(actualJson);
            JSONObject expectedObject = new JSONObject(expectedJson);
            
            // 检查所有预期字段是否存在且匹配
            for (String key : expectedObject.keySet()) {
                if (!actualObject.has(key)) {
                    validationErrors.add(new ValidationError(
                        "json_contains", 
                        "Missing expected field: " + key
                    ));
                } else {
                    Object expectedValue = expectedObject.get(key);
                    Object actualValue = actualObject.get(key);
                    
                    if (!expectedValue.equals(actualValue)) {
                        validationErrors.add(new ValidationError(
                            "json_contains", 
                            "Field '" + key + "' expected '" + expectedValue + "' but got '" + actualValue + "'"
                        ));
                    }
                }
            }
        } catch (Exception e) {
            validationErrors.add(new ValidationError(
                "json_contains", 
                "Failed to verify JSON contains: " + e.getMessage()
            ));
        }
        return this;
    }
    
    /**
     * 验证响应体不为空
     */
    public ResponseValidator assertBodyNotEmpty() {
        String body = response.getBody().asString();
        if (StringUtils.isBlank(body)) {
            validationErrors.add(new ValidationError(
                "body_empty", 
                "Expected non-empty response body"
            ));
        }
        return this;
    }
    
    /**
     * 使用自定义验证函数
     */
    public ResponseValidator assertCustom(String name, Function<Response, Boolean> validator, String errorMessage) {
        try {
            if (!validator.apply(response)) {
                validationErrors.add(new ValidationError(name, errorMessage));
            }
        } catch (Exception e) {
            validationErrors.add(new ValidationError(
                name, 
                "Custom validation failed: " + e.getMessage()
            ));
        }
        return this;
    }
    
    /**
     * 验证所有先前的断言
     */
    public void validateAll() {
        if (!validationErrors.isEmpty()) {
            StringBuilder errorMessage = new StringBuilder("Validation errors found:\n");
            for (ValidationError error : validationErrors) {
                errorMessage.append(" - ").append(error.toString()).append("\n");
            }
            throw new AssertionError(errorMessage.toString());
        }
    }
    
    /**
     * 获取所有验证错误
     */
    public List<ValidationError> getValidationErrors() {
        return new ArrayList<>(validationErrors);
    }
    
    /**
     * 检查是否有验证错误
     */
    public boolean hasValidationErrors() {
        return !validationErrors.isEmpty();
    }
    
    /**
     * 重置验证错误
     */
    public void resetErrors() {
        validationErrors.clear();
    }
    
    /**
     * 验证错误类
     */
    public static class ValidationError {
        private final String field;
        private final String message;
        
        public ValidationError(String field, String message) {
            this.field = field;
            this.message = message;
        }
        
        public String getField() {
            return field;
        }
        
        public String getMessage() {
            return message;
        }
        
        @Override
        public String toString() {
            return field + ": " + message;
        }
    }
}