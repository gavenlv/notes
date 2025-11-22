package com.example.blog.controller;

import com.example.blog.entity.Comment;
import com.example.blog.entity.Post;
import com.example.blog.service.CommentService;
import com.example.blog.service.PostService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@Controller
public class WebController {
    
    @Autowired
    private PostService postService;
    
    @Autowired
    private CommentService commentService;
    
    @GetMapping("/")
    public String index(Model model) {
        List<Post> posts = postService.getAllPosts();
        model.addAttribute("posts", posts);
        return "index";
    }
    
    @GetMapping("/post/{id}")
    public String post(@PathVariable Long id, Model model) {
        return postService.getPostById(id)
            .map(p -> {
                model.addAttribute("post", p);
                List<Comment> comments = commentService.getCommentsByPostId(id);
                model.addAttribute("comments", comments);
                return "post";
            })
            .orElse("redirect:/");
    }
    
    @PostMapping("/comment")
    public String addComment(@RequestParam Long postId, @RequestParam String content) {
        Comment comment = new Comment();
        comment.setContent(content);
        
        // 设置关联的文章
        postService.getPostById(postId).ifPresent(comment::setPost);
        
        commentService.saveComment(comment);
        return "redirect:/post/" + postId;
    }
    
    @GetMapping("/search")
    public String search(@RequestParam String keyword, Model model) {
        List<Post> posts = postService.searchPosts(keyword);
        model.addAttribute("posts", posts);
        model.addAttribute("keyword", keyword);
        return "index";
    }
}