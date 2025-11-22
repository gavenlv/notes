package com.example.blog;

import com.example.blog.entity.Post;
import com.example.blog.repository.PostRepository;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import java.util.List;
import java.util.Optional;

import static org.assertj.core.api.Assertions.assertThat;

@DataJpaTest
public class PostRepositoryTest {
    
    @Autowired
    private TestEntityManager entityManager;
    
    @Autowired
    private PostRepository postRepository;
    
    @Test
    public void testSaveAndFindPost() {
        // 创建一个Post对象
        Post post = new Post();
        post.setTitle("测试文章");
        post.setContent("这是一篇用于测试的文章内容。");
        
        // 保存到数据库
        Post savedPost = postRepository.save(post);
        
        // 验证保存成功
        assertThat(savedPost.getId()).isNotNull();
        
        // 根据ID查找
        Optional<Post> foundPost = postRepository.findById(savedPost.getId());
        assertThat(foundPost).isPresent();
        assertThat(foundPost.get().getTitle()).isEqualTo("测试文章");
        assertThat(foundPost.get().getContent()).isEqualTo("这是一篇用于测试的文章内容。");
    }
    
    @Test
    public void testFindByTitleContainingIgnoreCase() {
        // 创建测试数据
        Post post1 = new Post();
        post1.setTitle("Spring Boot教程");
        post1.setContent("Spring Boot相关内容...");
        
        Post post2 = new Post();
        post2.setTitle("Java基础");
        post2.setContent("Java基础内容...");
        
        entityManager.persist(post1);
        entityManager.persist(post2);
        entityManager.flush();
        
        // 测试搜索功能
        List<Post> results = postRepository.findByTitleContainingIgnoreCase("spring");
        assertThat(results).hasSize(1);
        assertThat(results.get(0).getTitle()).isEqualTo("Spring Boot教程");
    }
}