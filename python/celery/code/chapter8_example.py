"""
Celery在Web应用中的集成示例

本章代码演示了如何将Celery与各种Web框架集成，包括：
1. Flask集成
2. Django集成
3. FastAPI集成
4. 前端状态轮询和WebSocket示例

注意：要运行这些示例，您需要安装相应的依赖包并配置好Redis。
"""

# 第一部分: Flask集成示例

# 示例1: 基础Flask集成
'''
# flask_basic_integration.py
from flask import Flask, request, jsonify
from celery import Celery
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

# 初始化Celery
celery = Celery(
    app.import_name,
    broker=app.config['CELERY_BROKER_URL'],
    backend=app.config['CELERY_RESULT_BACKEND']
)

# 更新Celery配置为Flask应用的配置
celery.conf.update(app.config)

# 可选：创建上下文任务基类
class ContextTask(celery.Task):
    def __call__(self, *args, **kwargs):
        with app.app_context():
            return self.run(*args, **kwargs)

celery.Task = ContextTask

# 定义任务
@celery.task()
def add_together(a, b):
    return a + b

@celery.task()
def process_data(data):
    import time
    time.sleep(2)  # 模拟长时间处理
    return f'Processed: {data}'

@app.route('/')
def index():
    return 'Welcome to Flask-Celery Integration Example'

@app.route('/add/<int:a>/<int:b>')
def add_numbers(a, b):
    # 异步执行任务
    result = add_together.delay(a, b)
    # 返回任务ID，用于后续查询
    return f'Task submitted. Task ID: {result.id}'

@app.route('/result/<task_id>')
def get_result(task_id):
    result = add_together.AsyncResult(task_id)
    if result.ready():
        return f'Result: {result.get()}'
    else:
        return 'Task still processing...'

# 工厂模式示例 (flask_factory_integration.py)
'''

# 示例2: 完整的Flask应用与Celery集成，支持文件处理

# 保存为 flask_celery_integration.py
'''
from flask import Flask, request, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from celery import Celery
import os
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = './uploads'
app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'doc', 'docx', 'csv', 'xlsx'}

# 确保上传文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# 配置Celery
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# 辅助函数
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# 定义Celery任务
@celery.task(bind=True)
def process_file(self, filepath, filename):
    """处理上传的文件"""
    # 更新任务状态为处理中
    self.update_state(state='PROCESSING', meta={'filename': filename, 'progress': 0})
    
    # 根据文件类型执行不同的处理
    file_ext = filename.rsplit('.', 1)[1].lower()
    
    # 模拟文件处理过程
    total_steps = 10
    results = {}
    
    # 步骤1: 读取文件
    time.sleep(1)
    self.update_state(state='PROCESSING', meta={
        'filename': filename,
        'progress': 10,
        'status': 'Reading file...'
    })
    results['read'] = 'File read successfully'
    
    # 步骤2: 解析文件内容（根据类型）
    time.sleep(1)
    self.update_state(state='PROCESSING', meta={
        'filename': filename,
        'progress': 30,
        'status': f'Parsing {file_ext} content...'
    })
    results['parsed'] = f'Content parsed as {file_ext}'
    
    # 步骤3: 处理数据
    time.sleep(2)
    self.update_state(state='PROCESSING', meta={
        'filename': filename,
        'progress': 70,
        'status': 'Processing data...'
    })
    results['processed'] = 'Data processed'
    
    # 步骤4: 生成结果
    time.sleep(1)
    self.update_state(state='PROCESSING', meta={
        'filename': filename,
        'progress': 90,
        'status': 'Generating results...'
    })
    
    # 完成处理
    time.sleep(0.5)
    results['completed'] = True
    results['filename'] = filename
    results['file_type'] = file_ext
    
    return results

# Flask路由
@app.route('/')
def home():
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    # 检查是否有文件部分
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    # 如果用户没有选择文件
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    # 检查文件类型
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # 提交文件处理任务
        task = process_file.delay(filepath, filename)
        
        # 返回任务ID，前端会重定向到状态页面
        return jsonify({'url': url_for('task_status', task_id=task.id)})
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/status/<task_id>')
def task_status(task_id):
    # 这里应该返回HTML模板，为简单起见我们直接返回JSON
    return jsonify({'task_id': task_id, 'status_url': url_for('api_task_status', task_id=task_id)})

@app.route('/api/status/<task_id>')
def api_task_status(task_id):
    task = process_file.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'state': task.state,
            'status': 'Pending...'
        }
    elif task.state == 'PROCESSING':
        response = {
            'state': task.state,
            'status': task.info.get('status', 'Processing...'),
            'progress': task.info.get('progress', 0),
            'filename': task.info.get('filename', '')
        }
    elif task.state != 'FAILURE':
        response = {
            'state': task.state,
            'result': task.result
        }
    else:
        # 任务失败
        response = {
            'state': task.state,
            'error': str(task.result)
        }
    
    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)
'''

# 第二部分: FastAPI集成示例

# fastapi_celery_integration.py
'''
from fastapi import FastAPI, BackgroundTasks, UploadFile, File
from celery import Celery
import os
import time
from typing import Dict

# 创建FastAPI应用
app = FastAPI(title="FastAPI Celery Integration")

# 配置Celery
celery = Celery(
    "tasks",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
)

# 定义Celery任务
@celery.task(name="add_numbers")
def add_numbers(a: int, b: int) -> int:
    """简单的加法任务"""
    return a + b

@celery.task(name="process_data")
def process_data(data: dict) -> dict:
    """处理数据的任务"""
    # 模拟长时间处理
    time.sleep(5)
    return {"processed": True, "data": data}

@celery.task(bind=True)
def process_file_fastapi(self, filename: str) -> Dict:
    """FastAPI文件处理任务"""
    # 更新任务状态
    self.update_state(state='PROCESSING', meta={'filename': filename, 'progress': 0})
    
    # 模拟处理过程
    time.sleep(1)
    self.update_state(state='PROCESSING', meta={
        'filename': filename,
        'progress': 33,
        'status': 'Processing...'
    })
    
    time.sleep(1)
    self.update_state(state='PROCESSING', meta={
        'filename': filename,
        'progress': 66,
        'status': 'Still processing...'
    })
    
    time.sleep(1)
    
    return {
        'filename': filename,
        'size': os.path.getsize(filename) if os.path.exists(filename) else 0,
        'processed_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }

# FastAPI端点
@app.post("/tasks/add/")
def add_task(a: int, b: int):
    """提交加法任务"""
    task = add_numbers.delay(a, b)
    return {"task_id": task.id, "status": "submitted"}

@app.get("/tasks/result/{task_id}")
def get_task_result(task_id: str):
    """获取任务结果"""
    task = add_numbers.AsyncResult(task_id)
    
    if task.ready():
        return {"task_id": task_id, "status": "completed", "result": task.get()}
    else:
        return {"task_id": task_id, "status": "pending"}

@app.post("/upload/", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    """上传文件并提交处理任务"""
    # 保存文件
    try:
        with open(file.filename, "wb") as buffer:
            buffer.write(await file.read())
        
        # 提交任务
        task = process_file_fastapi.delay(file.filename)
        
        return {
            "filename": file.filename,
            "task_id": task.id,
            "status": "submitted"
        }
    except Exception as e:
        return {"error": str(e)}, 500

# 使用FastAPI的BackgroundTasks作为轻量级替代
@app.post("/background-tasks/")
def create_background_task(background_tasks: BackgroundTasks, data: dict):
    """使用FastAPI内置的后台任务（适合轻量级任务）"""
    background_tasks.add_task(process_data_in_background, data)
    return {"message": "Task added to background tasks"}

def process_data_in_background(data: dict):
    """在后台处理数据"""
    time.sleep(5)
    # 这里可以保存结果到数据库等
    return {"processed": True, "data": data}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
'''

# 第三部分: 完整的Celery与Web集成演示

# 本文件提供一个可运行的示例，演示Celery与Web应用的集成
from celery import Celery
import os
import time
import json

# 配置Celery
celery = Celery(
    "web_integration_demo",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# 配置Celery
celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Asia/Shanghai',
    enable_utc=True,
    result_expires=3600,
)

# 示例任务，模拟不同类型的Web应用任务

@celery.task(bind=True)
def process_image(self, image_path):
    """
    模拟图像处理任务
    这在Web应用中很常见，如图像上传后需要调整大小、滤镜处理等
    """
    # 更新进度
    self.update_state(state='PROCESSING', meta={'progress': 0, 'status': '开始处理图像'})
    time.sleep(1)
    
    self.update_state(state='PROCESSING', meta={'progress': 30, 'status': '读取图像数据'})
    time.sleep(1)
    
    self.update_state(state='PROCESSING', meta={'progress': 60, 'status': '应用处理滤镜'})
    time.sleep(1)
    
    self.update_state(state='PROCESSING', meta={'progress': 90, 'status': '保存处理结果'})
    time.sleep(0.5)
    
    return {
        'image_path': image_path,
        'status': '处理完成',
        'processed_path': image_path + '.processed',
        'time_taken': 3.5
    }

@celery.task(bind=True)
def send_bulk_emails(self, email_list, subject, message):
    """
    模拟批量发送邮件任务
    这在用户注册确认、通知等场景中非常常见
    """
    total_emails = len(email_list)
    sent_count = 0
    failed_count = 0
    
    for i, email in enumerate(email_list):
        # 模拟发送过程
        time.sleep(0.2)  # 每个邮件处理时间
        
        # 模拟一些失败情况
        if hash(email) % 10 == 0:  # 10%的失败率
            failed_count += 1
        else:
            sent_count += 1
        
        # 更新进度
        progress = int((i + 1) / total_emails * 100)
        self.update_state(
            state='PROCESSING', 
            meta={
                'progress': progress,
                'status': f'正在发送邮件 ({i+1}/{total_emails})',
                'sent': sent_count,
                'failed': failed_count
            }
        )
    
    return {
        'total': total_emails,
        'sent': sent_count,
        'failed': failed_count,
        'success_rate': (sent_count / total_emails) * 100 if total_emails > 0 else 0
    }

@celery.task(bind=True)
def generate_report(self, report_type, parameters):
    """
    模拟生成报表任务
    在数据分析类Web应用中非常常见
    """
    self.update_state(state='PROCESSING', meta={'progress': 0, 'status': '初始化报表生成'})
    time.sleep(1)
    
    self.update_state(state='PROCESSING', meta={'progress': 25, 'status': '收集数据'})
    time.sleep(2)
    
    self.update_state(state='PROCESSING', meta={'progress': 60, 'status': '处理数据'})
    time.sleep(2)
    
    self.update_state(state='PROCESSING', meta={'progress': 85, 'status': '生成报表'})
    time.sleep(1)
    
    return {
        'report_type': report_type,
        'parameters': parameters,
        'status': '生成完成',
        'report_id': f"report_{int(time.time())}",
        'available_at': time.strftime('%Y-%m-%d %H:%M:%S')
    }

@celery.task(bind=True)
def user_import_task(self, import_file, user_data):
    """
    模拟用户数据导入任务
    在管理系统中常见的数据批量操作
    """
    total_users = len(user_data)
    
    self.update_state(
        state='PROCESSING', 
        meta={
            'progress': 0, 
            'status': f'准备导入 {total_users} 个用户',
            'imported': 0,
            'failed': 0
        }
    )
    time.sleep(1)
    
    imported = 0
    failed = 0
    
    for i, user in enumerate(user_data):
        # 模拟导入过程
        time.sleep(0.3)
        
        # 模拟一些失败
        if hash(user.get('email', '')) % 15 == 0:
            failed += 1
        else:
            imported += 1
        
        progress = int((i + 1) / total_users * 100)
        self.update_state(
            state='PROCESSING',
            meta={
                'progress': progress,
                'status': f'导入用户 {i+1}/{total_users}',
                'imported': imported,
                'failed': failed
            }
        )
    
    return {
        'file': import_file,
        'total': total_users,
        'imported': imported,
        'failed': failed,
        'success_rate': (imported / total_users) * 100 if total_users > 0 else 0
    }

# Web应用示例路由处理函数（伪代码）
'''
在实际的Web框架中，这些函数会是路由处理函数
这里我们只提供逻辑示例
'''

def submit_image_processing(image_path):
    """提交图像处理任务"""
    task = process_image.delay(image_path)
    return {
        'task_id': task.id,
        'status': 'submitted',
        'message': f'图像处理任务已提交，任务ID: {task.id}'
    }

def submit_email_campaign(emails, subject, message):
    """提交邮件活动任务"""
    task = send_bulk_emails.delay(emails, subject, message)
    return {
        'task_id': task.id,
        'total_emails': len(emails),
        'status': 'submitted'
    }

def request_report_generation(report_type, parameters):
    """请求生成报表"""
    task = generate_report.delay(report_type, parameters)
    return {
        'task_id': task.id,
        'report_type': report_type,
        'status': 'submitted'
    }

def import_users(import_file, user_data):
    """导入用户数据"""
    task = user_import_task.delay(import_file, user_data)
    return {
        'task_id': task.id,
        'total_users': len(user_data),
        'status': 'submitted'
    }

# 获取任务状态的通用函数
def get_task_status(task_id, task_type):
    """
    获取任务状态
    task_type: image, email, report, import
    """
    # 根据任务类型选择对应的任务函数
    task_map = {
        'image': process_image,
        'email': send_bulk_emails,
        'report': generate_report,
        'import': user_import_task
    }
    
    task_func = task_map.get(task_type, process_image)
    task = task_func.AsyncResult(task_id)
    
    if task.state == 'PENDING':
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': '任务等待中...',
            'progress': 0
        }
    elif task.state == 'PROCESSING':
        # 处理中的任务有详细进度信息
        info = task.info or {}
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': info.get('status', '处理中...'),
            'progress': info.get('progress', 0)
        }
        
        # 根据任务类型添加特定信息
        if task_type == 'email':
            response['sent'] = info.get('sent', 0)
            response['failed'] = info.get('failed', 0)
        elif task_type == 'import':
            response['imported'] = info.get('imported', 0)
            response['failed'] = info.get('failed', 0)
    elif task.state == 'SUCCESS':
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': '任务完成',
            'result': task.result
        }
    elif task.state == 'FAILURE':
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': '任务失败',
            'error': str(task.result)
        }
    else:
        response = {
            'task_id': task_id,
            'state': task.state,
            'status': '未知状态'
        }
    
    return response

# 前端示例JavaScript代码
'''
// 这段代码应该放在HTML页面的<script>标签内

// 轮询任务状态的函数
function pollTaskStatus(taskId, taskType, updateCallback) {
    fetch(`/api/task-status/${taskId}?type=${taskType}`)
        .then(response => response.json())
        .then(data => {
            updateCallback(data);
            
            if (data.state === 'PROCESSING' || data.state === 'PENDING') {
                // 继续轮询
                setTimeout(() => pollTaskStatus(taskId, taskType, updateCallback), 1000);
            }
        })
        .catch(error => {
            console.error('Error polling task status:', error);
            // 出错后重试
            setTimeout(() => pollTaskStatus(taskId, taskType, updateCallback), 3000);
        });
}

// 更新进度条的回调
function updateProgressUI(data) {
    const progressBar = document.getElementById('progress-bar');
    const statusText = document.getElementById('status-text');
    const resultContainer = document.getElementById('result-container');
    
    // 更新进度条
    progressBar.style.width = `${data.progress}%`;
    progressBar.setAttribute('aria-valuenow', data.progress);
    
    // 更新状态文本
    statusText.textContent = data.status;
    
    // 如果任务完成，显示结果
    if (data.state === 'SUCCESS' && data.result) {
        statusText.textContent = '任务已完成';
        resultContainer.innerHTML = `<pre>${JSON.stringify(data.result, null, 2)}</pre>`;
    } 
    // 如果任务失败，显示错误
    else if (data.state === 'FAILURE') {
        statusText.textContent = '任务失败';
        resultContainer.innerHTML = `<div class="error">错误: ${data.error}</div>`;
    }
}

// 提交任务的函数示例
function submitTask() {
    // 示例：提交图像处理任务
    fetch('/api/process-image', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image_path: '/path/to/image.jpg' })
    })
    .then(response => response.json())
    .then(data => {
        // 开始轮询任务状态
        pollTaskStatus(data.task_id, 'image', updateProgressUI);
    });
}
'''

# 演示函数
def run_demo():
    """
    运行演示，展示Web集成的不同场景
    """
    print("=== Celery Web应用集成演示 ===")
    print("\n此文件包含了与各种Web框架集成的示例代码")
    print("要运行完整的Web应用，需要：")
    print("1. 安装必要的依赖：pip install flask fastapi uvicorn celery redis")
    print("2. 启动Redis服务器")
    print("3. 启动Celery工作进程：celery -A chapter8_example worker --loglevel=info")
    print("4. 运行对应的Web应用文件")
    print("\n以下是一些示例任务的直接调用方法：\n")
    
    # 演示如何直接运行任务
    print("1. 图像处理任务")
    # image_task = process_image.delay("sample_image.jpg")
    print("   process_image.delay(\"sample_image.jpg\")")
    
    print("\n2. 批量邮件任务")
    sample_emails = [f"user{i}@example.com" for i in range(10)]
    # email_task = send_bulk_emails.delay(sample_emails, "Test Subject", "Test Message")
    print(f"   send_bulk_emails.delay({sample_emails[:3]}... , \"Test Subject\", \"Test Message\")")
    
    print("\n3. 报表生成任务")
    # report_task = generate_report.delay("sales", {"start_date": "2023-01-01", "end_date": "2023-12-31"})
    print("   generate_report.delay(\"sales\", {\"start_date\": \"2023-01-01\", \"end_date\": \"2023-12-31\"})")
    
    print("\n4. 用户导入任务")
    sample_users = [{"email": f"user{i}@example.com", "name": f"User {i}"} for i in range(5)]
    # import_task = user_import_task.delay("users.csv", sample_users)
    print(f"   user_import_task.delay(\"users.csv\", {sample_users[:2]}... )")
    
    print("\n在Web应用中，这些任务会通过HTTP API触发，并通过轮询或WebSocket更新状态。")

if __name__ == "__main__":
    run_demo()
