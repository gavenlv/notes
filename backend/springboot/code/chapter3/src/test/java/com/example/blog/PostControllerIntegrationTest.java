package com.example.blog;

import com.example.blog.entity.Post;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.test.web.client.TestRestTemplate;
import org.springframework.boot.test.web.server.LocalServerPort;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import static org.assertj.core.api.Assertions.assertThat;

@SpringBootTest(webEnvironment = SpringBootTest.WebEnvironment.RANDOM_PORT)
public class PostControllerIntegrationTest {
    
    @LocalServerPort
    private int port;
    
    @Autowired
    private TestRestTemplate restTemplate;
    
    @Test
    public void testCreateAndGetPost() {
        // 创建一个Post对象
        Post post = new Post();
        post.setTitle("集成测试文章");
        post.setContent("这是一篇用于集成测试的文章。");
        
        // 发送POST请求创建文章
        ResponseEntity<Post> postResponse = restTemplate.postForEntity(
            "http://localhost:" + port + "/api/posts", post, Post.class);
        
        // 验证创建成功
        assertThat(postResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(postResponse.getBody()).isNotNull();
        assertThat(postResponse.getBody().getId()).isNotNull();
        assertThat(postResponse.getBody().getTitle()).isEqualTo("集成测试文章");
        
        Long postId = postResponse.getBody().getId();
        
        // 发送GET请求获取文章
        ResponseEntity<Post> getResponse = restTemplate.getForEntity(
            "http://localhost:" + port + "/api/posts/" + postId, Post.class);
        
        // 验证获取成功
        assertThat(getResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(getResponse.getBody()).isNotNull();
        assertThat(getResponse.getBody().getTitle()).isEqualTo("集成测试文章");
    }
    
    @Test
    public void testUpdatePost() {
        // 创建一个Post对象
        Post post = new Post();
        post.setTitle("原始标题");
        post.setContent("原始内容。");
        
        // 发送POST请求创建文章
        ResponseEntity<Post> postResponse = restTemplate.postForEntity(
            "http://localhost:" + port + "/api/posts", post, Post.class);
        
        Post createdPost = postResponse.getBody();
        Long postId = createdPost.getId();
        
        // 更新文章内容
        Post updatedPost = new Post();
        updatedPost.setTitle("更新后的标题");
        updatedPost.setContent("更新后的内容。");
        
        // 发送PUT请求更新文章
        HttpEntity<Post> requestEntity = new HttpEntity<>(updatedPost);
        ResponseEntity<Post> putResponse = restTemplate.exchange(
            "http://localhost:" + port + "/api/posts/" + postId, 
            HttpMethod.PUT, 
            requestEntity, 
            Post.class);
        
        // 验证更新成功
        assertThat(putResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(putResponse.getBody()).isNotNull();
        assertThat(putResponse.getBody().getTitle()).isEqualTo("更新后的标题");
        
        // 验证GET请求也能获取到更新后的内容
        ResponseEntity<Post> getResponse = restTemplate.getForEntity(
            "http://localhost:" + port + "/api/posts/" + postId, Post.class);
        
        assertThat(getResponse.getStatusCode()).isEqualTo(HttpStatus.OK);
        assertThat(getResponse.getBody().getTitle()).isEqualTo("更新后的标题");
    }
}