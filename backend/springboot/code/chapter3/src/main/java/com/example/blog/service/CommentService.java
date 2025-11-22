package com.example.blog.service;

import com.example.blog.entity.Comment;
import com.example.blog.repository.CommentRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CommentService {
    
    @Autowired
    private CommentRepository commentRepository;
    
    public List<Comment> getCommentsByPostId(Long postId) {
        return commentRepository.findByPostId(postId);
    }
    
    public Comment saveComment(Comment comment) {
        return commentRepository.save(comment);
    }
    
    public void deleteComment(Long id) {
        commentRepository.deleteById(id);
    }
}