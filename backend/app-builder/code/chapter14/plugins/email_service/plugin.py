from flask_appbuilder import BasePlugin
from flask_mail import Mail, Message
from flask import current_app
import threading
import logging
from jinja2 import Template
import os

class EmailServicePlugin(BasePlugin):
    name = "Email Service"
    category = "Services"
    version = "1.0.0"
    
    def __init__(self, appbuilder):
        super().__init__(appbuilder)
        self.mail = Mail(current_app)
        self.logger = logging.getLogger('email_service')
    
    def send_email_async(self, subject, recipients, body=None, html_body=None, attachments=None):
        """异步发送邮件"""
        def send_async_email(app, msg):
            try:
                with app.app_context():
                    self.mail.send(msg)
                self.logger.info(f"Email sent successfully to {recipients}")
            except Exception as e:
                self.logger.error(f"Failed to send email to {recipients}: {str(e)}")
        
        msg = Message(
            subject=subject,
            recipients=recipients,
            body=body,
            html=html_body
        )
        
        # 添加附件
        if attachments:
            for attachment in attachments:
                if isinstance(attachment, dict):
                    # 字典形式的附件
                    if 'filename' in attachment and 'data' in attachment:
                        msg.attach(
                            filename=attachment['filename'],
                            content_type=attachment.get('content_type', 'application/octet-stream'),
                            data=attachment['data']
                        )
                else:
                    # 文件路径形式的附件
                    if os.path.exists(attachment):
                        with open(attachment, 'rb') as fp:
                            msg.attach(
                                filename=os.path.basename(attachment),
                                content_type='application/octet-stream',
                                data=fp.read()
                            )
        
        thread = threading.Thread(
            target=send_async_email,
            args=(current_app._get_current_object(), msg)
        )
        thread.start()
        return thread
    
    def send_notification(self, user, message, subject="Notification"):
        """发送通知邮件"""
        if hasattr(user, 'email') and user.email:
            return self.send_email_async(
                subject=subject,
                recipients=[user.email],
                body=message
            )
        else:
            self.logger.warning(f"User {user} has no email address")
    
    def send_template_email(self, template_name, recipients, subject, context=None, **kwargs):
        """发送模板邮件"""
        # 查找模板文件
        template_paths = [
            os.path.join(current_app.root_path, 'templates', 'emails', f'{template_name}.html'),
            os.path.join(current_app.root_path, 'templates', 'emails', f'{template_name}.txt'),
            os.path.join(os.path.dirname(__file__), 'templates', f'{template_name}.html'),
            os.path.join(os.path.dirname(__file__), 'templates', f'{template_name}.txt')
        ]
        
        template_content = None
        is_html = False
        
        for template_path in template_paths:
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    template_content = f.read()
                is_html = template_path.endswith('.html')
                break
        
        if not template_content:
            self.logger.error(f"Template {template_name} not found")
            return None
        
        # 渲染模板
        template = Template(template_content)
        rendered_content = template.render(context or {})
        
        # 发送邮件
        if is_html:
            return self.send_email_async(
                subject=subject,
                recipients=recipients,
                html_body=rendered_content,
                **kwargs
            )
        else:
            return self.send_email_async(
                subject=subject,
                recipients=recipients,
                body=rendered_content,
                **kwargs
            )
    
    def send_bulk_emails(self, emails_data):
        """批量发送邮件"""
        threads = []
        for email_data in emails_data:
            thread = self.send_email_async(**email_data)
            threads.append(thread)
        return threads
    
    def send_welcome_email(self, user):
        """发送欢迎邮件"""
        if hasattr(user, 'email') and user.email:
            context = {
                'username': user.username,
                'email': user.email,
                'app_name': current_app.config.get('APP_NAME', 'Our Application')
            }
            
            return self.send_template_email(
                template_name='welcome',
                recipients=[user.email],
                subject=f"Welcome to {context['app_name']}!",
                context=context
            )

# 预定义的邮件模板
WELCOME_EMAIL_TEMPLATE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Welcome</title>
</head>
<body>
    <h2>Welcome to {{ app_name }}!</h2>
    <p>Hello {{ username }},</p>
    <p>Welcome to our platform! We're excited to have you on board.</p>
    <p>Your account has been successfully created with email: {{ email }}</p>
    <p>If you have any questions, feel free to contact our support team.</p>
    <br>
    <p>Best regards,<br>The {{ app_name }} Team</p>
</body>
</html>
"""

WELCOME_EMAIL_TEMPLATE_TXT = """
Welcome to {{ app_name }}!

Hello {{ username }},

Welcome to our platform! We're excited to have you on board.

Your account has been successfully created with email: {{ email }}

If you have any questions, feel free to contact our support team.

Best regards,
The {{ app_name }} Team
"""