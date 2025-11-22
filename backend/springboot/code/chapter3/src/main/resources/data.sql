INSERT INTO posts (title, content, created_at) VALUES 
('第一篇博客', '这是我的第一篇博客文章内容。', NOW()),
('Spring Boot入门', 'Spring Boot是一个非常流行的Java框架，它简化了Spring应用的初始搭建以及开发过程。', NOW()),
('Thymeleaf模板引擎', 'Thymeleaf是一个现代化的服务器端Java模板引擎，适用于Web和独立环境。', NOW());

INSERT INTO comments (content, created_at, post_id) VALUES 
('很好的文章，谢谢分享！', NOW(), 1),
('学到了很多新知识。', NOW(), 1),
('Spring Boot确实让开发变得更简单了。', NOW(), 2);