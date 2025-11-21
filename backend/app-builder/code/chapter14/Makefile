# Makefile for Chapter 14 - Extending Flask App-Builder with Plugins

# 变量定义
PYTHON := python3
PIP := pip
APP := app.py
REQ := requirements.txt
TESTS := tests/

# 默认目标
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  install     - Install dependencies"
	@echo "  run         - Run the application"
	@echo "  test        - Run tests"
	@echo "  clean       - Clean compiled files"
	@echo "  docker-build - Build Docker image"
	@echo "  docker-run   - Run application in Docker"
	@echo "  lint        - Run code linting"
	@echo "  format      - Format code with black"
	@echo "  docs        - Generate documentation"
	@echo "  deploy      - Deploy application"

# 安装依赖
.PHONY: install
install:
	$(PIP) install -r $(REQ)

# 运行应用
.PHONY: run
run:
	$(PYTHON) $(APP)

# 运行测试
.PHONY: test
test:
	$(PYTHON) -m pytest $(TESTS) -v

# 清理编译文件
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	rm -f *.log

# 构建Docker镜像
.PHONY: docker-build
docker-build:
	docker build -t chapter14-app .

# 在Docker中运行应用
.PHONY: docker-run
docker-run:
	docker run -p 8080:8080 chapter14-app

# 代码检查
.PHONY: lint
lint:
	flake8 .
	pylint app.py plugins/*/plugin.py

# 格式化代码
.PHONY: format
format:
	black .
	isort .

# 生成文档
.PHONY: docs
docs:
	sphinx-build -b html docs/ docs/_build/html/

# 部署应用
.PHONY: deploy
deploy:
	@echo "Deploying application..."
	# 添加部署命令，例如推送到服务器或云平台

# 开发模式运行
.PHONY: dev
dev:
	$(PYTHON) $(APP) --debug

# 初始化数据库
.PHONY: db-init
db-init:
	$(PYTHON) -c "from app import app; from app import db; with app.app_context(): db.create_all()"

# 数据库迁移
.PHONY: db-migrate
db-migrate:
	flask db migrate
	flask db upgrade

# 运行Celery Worker
.PHONY: celery-worker
celery-worker:
	celery -A app.celery worker --loglevel=info

# 运行Celery Beat (定时任务)
.PHONY: celery-beat
celery-beat:
	celery -A app.celery beat --loglevel=info

# 监控Celery任务
.PHONY: celery-monitor
celery-monitor:
	flower -A app.celery --port=5555