# Day 14 学习材料

## 核心概念

### 1. 部署架构
生产环境部署需要考虑多个方面，包括高可用性、可扩展性、安全性等。

#### 部署模式
1. **单机部署**
   - 适用于开发测试环境
   - 所有组件运行在同一台机器上
   - 使用本地数据库和执行器

2. **分布式部署**
   - 适用于生产环境
   - 各组件独立部署在不同机器上
   - 支持高可用和负载均衡

3. **容器化部署**
   - 使用Docker和Kubernetes
   - 便于部署和管理
   - 支持弹性伸缩

#### 执行器选择
1. **SequentialExecutor**
   - 顺序执行任务
   - 仅用于开发测试

2. **LocalExecutor**
   - 本地并行执行
   - 适用于单机环境

3. **CeleryExecutor**
   - 分布式任务执行
   - 适用于生产环境

4. **KubernetesExecutor**
   - 基于Kubernetes的任务执行
   - 适用于容器化环境

### 2. 高可用设计
高可用性是生产环境的关键要求。

#### 架构设计原则
1. **无单点故障**
   - 所有组件都应有冗余
   - 数据库、消息队列、WebServer等

2. **负载均衡**
   - 多实例部署
   - 请求分发机制

3. **自动故障转移**
   - 健康检查机制
   - 自动切换策略

#### 数据库高可用
1. **主从复制**
   - 主库写入，从库读取
   - 数据同步机制

2. **集群部署**
   - PostgreSQL集群
   - MySQL集群

#### 消息队列高可用
1. **Redis集群**
   - 主从模式
   - 哨兵模式

2. **RabbitMQ集群**
   - 镜像队列
   - 集群模式

### 3. 监控与告警
完善的监控体系是保障系统稳定运行的重要手段。

#### 监控指标
1. **系统指标**
   - CPU使用率
   - 内存使用率
   - 磁盘空间
   - 网络流量

2. **应用指标**
   - DAG执行状态
   - 任务执行时间
   - 队列长度
   - 错误率

3. **业务指标**
   - 数据处理量
   - 业务完成率
   - SLA达成情况

#### 告警机制
1. **阈值告警**
   - 资源使用率超过阈值
   - 任务执行时间过长

2. **状态告警**
   - DAG执行失败
   - 任务失败

3. **趋势告警**
   - 性能下降趋势
   - 异常波动

### 4. 备份与恢复
数据安全是生产环境的核心要求。

#### 备份策略
1. **全量备份**
   - 定期完整备份
   - 存储在安全位置

2. **增量备份**
   - 备份变化数据
   - 减少备份时间

3. **差异备份**
   - 备份与上次全量备份的差异

#### 恢复方案
1. **灾难恢复**
   - 数据恢复流程
   - 系统重建步骤

2. **故障恢复**
   - 快速恢复机制
   - 数据一致性保障

### 5. 性能调优
性能优化是提升系统效率的关键。

#### 数据库优化
1. **索引优化**
   - 合理创建索引
   - 避免过多索引

2. **查询优化**
   - 优化SQL语句
   - 减少查询次数

3. **连接池配置**
   - 合理设置连接数
   - 避免连接泄露

#### 执行器调优
1. **并发控制**
   - 设置合适的并发数
   - 避免资源争用

2. **资源分配**
   - 合理分配CPU和内存
   - 避免资源浪费

#### 缓存优化
1. **元数据缓存**
   - 缓存DAG定义
   - 减少数据库查询

2. **结果缓存**
   - 缓存任务执行结果
   - 避免重复计算

## 实践指南

### 部署配置示例

#### docker-compose.yml
```yaml
version: '3.7'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres_db_volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5
    restart: always

  redis:
    image: redis:latest
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 30s
      retries: 50
    restart: always

  airflow-webserver:
    image: apache/airflow:2.3.0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
      AIRFLOW__CORE__FERNET_KEY: ''
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
      AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth'
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./config:/opt/airflow/config
      - ./plugins:/opt/airflow/plugins
    ports:
      - "8080:8080"
    command: webserver
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 10s
      retries: 5
    restart: always

  airflow-scheduler:
    image: apache/airflow:2.3.0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
      AIRFLOW__CORE__FERNET_KEY: ''
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./config:/opt/airflow/config
      - ./plugins:/opt/airflow/plugins
    command: scheduler
    restart: always

  airflow-worker:
    image: apache/airflow:2.3.0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
      AIRFLOW__CORE__FERNET_KEY: ''
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./config:/opt/airflow/config
      - ./plugins:/opt/airflow/plugins
    command: celery worker
    restart: always

  airflow-init:
    image: apache/airflow:2.3.0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    environment:
      AIRFLOW__CORE__EXECUTOR: CeleryExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__RESULT_BACKEND: db+postgresql://airflow:airflow@postgres/airflow
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
      AIRFLOW__CORE__FERNET_KEY: ''
      AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
      AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    volumes:
      - ./dags:/opt/airflow/dags
      - ./logs:/opt/airflow/logs
      - ./config:/opt/airflow/config
      - ./plugins:/opt/airflow/plugins
    command: version
    restart: "no"

  flower:
    image: apache/airflow:2.3.0
    depends_on:
      redis:
        condition: service_healthy
    environment:
      AIRFLOW__CELERY__BROKER_URL: redis://redis:6379/0
    ports:
      - "5555:5555"
    command: celery flower
    restart: always

volumes:
  postgres_db_volume:
```

### 配置文件示例

#### airflow.cfg
```ini
[core]
# The folder where your airflow pipelines live, most likely a
# subfolder in a code repository. This path must be absolute.
dags_folder = /opt/airflow/dags

# Hostname by providing a path to a callable, which will resolve the hostname.
hostname_callable = airflow.utils.net.getfqdn

# Default timezone in case supplied date times are naive
# can be utc (default), system, or any IANA timezone string (e.g. Europe/Amsterdam)
default_timezone = utc

# The executor class that airflow should use. Choices include
# ``SequentialExecutor``, ``LocalExecutor``, ``CeleryExecutor``, ``DaskExecutor``,
# ``KubernetesExecutor``, ``CeleryKubernetesExecutor`` or the
# full import path to the class when using a custom executor.
executor = CeleryExecutor

# The SqlAlchemy connection string to the metadata database.
# SqlAlchemy supports many different database engines.
# More information here:
# http://docs.sqlalchemy.org/en/latest/core/engines.html
sql_alchemy_conn = postgresql+psycopg2://airflow:airflow@postgres/airflow

# The encoding for the databases
sql_engine_encoding = utf-8

# Collation for ``dag_id``, ``task_id``, ``key`` for MySQL
# Specify this when creating the database if you have a different collation
# mysql_charset = utf8mb4
# mysql_collation = utf8mb4_unicode_ci

# If SqlAlchemy should pool database connections.
sql_alchemy_pool_enabled = True

# The SqlAlchemy pool size is the maximum number of database connections
# in the pool. 0 indicates no limit.
sql_alchemy_pool_size = 5

# The maximum overflow size of the pool.
# When the number of checked-out connections reaches the size set in pool_size,
# additional connections will be returned up to this limit.
# When those additional connections are returned to the pool, they are disconnected and discarded.
# It follows then that the total number of simultaneous connections the pool will allow
# is pool_size + max_overflow,
# and the total number of "sleeping" connections the pool will allow is pool_size.
# max_overflow can be set to -1 to indicate no overflow limit;
# no limit will be placed on the total number of concurrent connections. Defaults to 10.
sql_alchemy_max_overflow = 10

# The SqlAlchemy pool recycle is the number of seconds a connection
# can be idle in the pool before it is invalidated. This config does
# not apply to sqlite. If the number of DB connections is ever exceeded,
# a lower config value will allow the system to recover faster.
sql_alchemy_pool_recycle = 3600

# Check connection at the start of each connection pool checkout.
# Typically, this is a simple statement like "SELECT 1".
# More information here:
# http://docs.sqlalchemy.org/en/latest/core/pooling.html#disconnect-handling-pessimistic
sql_alchemy_pool_pre_ping = True

# The schema to use for the metadata database.
# SqlAlchemy supports databases with the concept of multiple schemas.
sql_alchemy_schema =

# Import path for connect args in SqlAlchemy. Defaults to an empty dict.
# This is useful when you want to configure db engine args that SqlAlchemy won't parse
# in connection string.
# See https://docs.sqlalchemy.org/en/13/core/engines.html#sqlalchemy.create_engine.params.connect_args
# sql_alchemy_connect_args =

[logging]
# The folder where airflow should store its log files
# This path must be absolute
base_log_folder = /opt/airflow/logs

# Airflow can store logs remotely in AWS S3, Google Cloud Storage or Elastic Search.
# Set this to True if you want to enable remote logging.
remote_logging = False

# Users must supply an Airflow connection id that provides access to the storage
# location.
remote_log_conn_id =

# Path to Google Credential JSON file to use with GCS remote logging.
# If set, this will be used in place of the connection id.
google_key_path =

# GCS remote logging bucket
remote_base_log_folder =

[metrics]
# StatsD (https://github.com/etsy/statsd) integration settings.
# Enables sending metrics to StatsD.
statsd_on = False
statsd_host = localhost
statsd_port = 8125
statsd_prefix = airflow

# If you want to avoid sending all of the available metrics to StatsD,
# you can configure an allow list of prefixes (comma separated) to send only the metrics that
# start with the elements of the list (e.g: "scheduler,executor,dagrun")
statsd_allow_list =

[secrets]
# Full class name of secrets backend to enable (will precede env vars and metastore in search path)
# Example: airflow.providers.amazon.aws.secrets.systems_manager.SystemsManagerParameterStoreBackend
backend =

# The backend_kwargs param is loaded into a dictionary and passed to __init__ of secrets backend class.
# See documentation for the secrets backend you are using. JSON is expected.
# Example for AWS Systems Manager ParameterStore:
# {"connections_prefix": "/airflow/connections", "profile_name": "default"}
backend_kwargs =

[cli]
# In what way should the cli access the API. The LocalClient will use the
# database directly, while the json_client will use the api running on the
# webserver
api_client = airflow.api.client.local_client

# If you set web_server_url_prefix, do NOT forget to update configuration when
# running the api server. It should have the same value as web_server_url_prefix
web_server_url_prefix =

[debug]
# Used only with ``DebugExecutor``. If set to ``True`` DAG will fail with first
# failed task. Helpful for debugging purposes.
fail_fast = False

[api]
# Enables the deprecated experimental API. Please note that these APIs do not have access control.
# The authenticated user has full access.
#
# .. warning::
#
#   This `Experimental REST API <https://airflow.readthedocs.io/en/latest/rest-api-ref.html>`__ is
#   deprecated since version 2.0. Please consider using
#   `the Stable REST API <https://airflow.readthedocs.io/en/latest/stable-rest-api-ref.html>`__
#   instead.
auth_backends = airflow.api.auth.backend.basic_auth

[lineage]
# what lineage backend to use
backend =

[atlas]
sasl_enabled = False
host =
port = 21000
username =
password =

[operators]
# The default owner assigned to each new operator, unless
# provided explicitly or passed via ``default_args``
default_owner = airflow
default_cpus = 1
default_ram = 512
default_disk = 512
default_gpus = 0

[hive]
# Default mapreduce queue for HiveOperator tasks
default_hive_mapred_queue =

[webserver]
# The base url of your website as airflow cannot guess what domain or
# cname you are using. This is used in automated emails that
# airflow sends to point links to the right web server
base_url = http://localhost:8080

# The ip specified when starting the web server
web_server_host = 0.0.0.0

# The port on which to run the web server
web_server_port = 8080

# Paths to the SSL certificate and key for the web server. When both are
# provided SSL will be enabled. This does not change the web server port.
web_server_ssl_cert =

# Paths to the SSL certificate and key for the web server. When both are
# provided SSL will be enabled. This does not change the web server port.
web_server_ssl_key =

# Number of seconds the webserver waits before killing gunicorn master that doesn't respond
web_server_master_timeout = 120

# Number of seconds the gunicorn webserver waits before timing out on a worker
web_server_worker_timeout = 120

# Number of workers to refresh at a time. When set to 0, worker refresh is
# disabled. When nonzero, airflow periodically refreshes webserver workers by
# bringing up new ones and killing old ones.
worker_refresh_batch_size = 1

# Number of seconds to wait before refreshing a batch of workers.
worker_refresh_interval = 30

# If set to True, Airflow will track files in plugins_folder directory. When it detects changes,
# then reload the gunicorn.
reload_on_plugin_change = False

# Secret key used to run your flask app
# It should be as random as possible
secret_key = temporary_key

# Number of workers to run the Gunicorn web server
workers = 4

# The worker class gunicorn should use. Choices include
# sync (default), eventlet, gevent
worker_class = sync

# Log files for the gunicorn webserver. '-' means log to stderr.
access_logfile = -

# Log files for the gunicorn webserver. '-' means log to stderr.
error_logfile = -

# Expose the configuration file in the web server
expose_config = False

# Expose hostname in the web server
expose_hostname = True

# Expose stacktrace in the web server
expose_stacktrace = True

# Default DAG view. Valid values are:
# tree, graph, duration, gantt, landing_times
dag_default_view = tree

# Default DAG orientation. Valid values are:
# LR (Left->Right), TB (Top->Bottom), RL (Right->Left), BT (Bottom->Top)
dag_orientation = LR

# Puts the webserver in demonstration mode; blurs out sensitive data
demo_mode = False

# The amount of time (in secs) webserver will wait for initial handshake
# while fetching logs from other worker machine
log_fetch_timeout_sec = 5

# Time interval (in secs) to wait before next log fetching.
log_fetch_delay_sec = 5

# Distance away from page bottom to enable auto tailing.
log_auto_tailing_offset = 30

# Animation speed for auto tailing log display.
log_animation_speed = 1000

# By default, the webserver shows paused DAGs. Flip this to hide paused
# DAGs by default
hide_paused_dags_by_default = False

# Consistent page size across all listing views in the UI
page_size = 100

# Define the color of navigation bar
navbar_color = #007A87

# Default dagrun to show in UI
default_dag_run_display_number = 25

# Enable werkzeug ``ProxyFix`` middleware for reverse proxy
enable_proxy_fix = False

# Number of values to trust for ``X-Forwarded-For``.
# More info: https://werkzeug.palletsprojects.com/en/0.16.x/middleware/proxy_fix/
proxy_fix_x_for = 1

# Number of values to trust for ``X-Forwarded-Proto``
proxy_fix_x_proto = 1

# Number of values to trust for ``X-Forwarded-Host``
proxy_fix_x_host = 1

# Number of values to trust for ``X-Forwarded-Port``
proxy_fix_x_port = 1

# Number of values to trust for ``X-Forwarded-Prefix``
proxy_fix_x_prefix = 1

# Set secure flag on session cookie
cookie_secure = False

# Set samesite policy on session cookie
cookie_samesite = Lax

# Default setting for wrap toggle on DAG code and TI log views.
default_wrap = False

# Allow the UI to be rendered in a frame
x_frame_enabled = True

# Send anonymous user activity to your analytics tool
# choose from google_analytics, segment, or metarouter
# analytics_tool =

# Unique ID of your account in the analytics tool
# analytics_id =

# 'Recent Tasks' stats will show for old DagRuns if set
show_recent_stats_for_completed_runs = True

# Update FAB permissions and sync security manager roles
# on webserver startup
update_fab_perms = True

[email]
email_backend = airflow.utils.email.send_email_smtp

[smtp]
# If you want airflow to send emails on retries, failure, and you want to use
# the airflow.utils.email.send_email_smtp function, you have to configure an
# smtp server here
smtp_host = localhost
smtp_starttls = True
smtp_ssl = False
# Example: smtp_user = airflow
# smtp_user =
# Example: smtp_password = airflow
# smtp_password =
smtp_port = 25
smtp_mail_from = airflow@example.com

[sentry]
# Sentry (https://docs.sentry.io) integration. Here you can supply
# additional configuration options based on the Python platform. See:
# https://docs.sentry.io/error-reporting/configuration/?platform=python
# Unsupported options: ``integrations``, ``in_app_include``, ``in_app_exclude``,
# ``ignore_errors``, ``before_breadcrumb``, ``before_send``, ``transport``.
sentry_dsn =

[celery]
# This section only applies if you are using the CeleryExecutor in
# ``[core]`` section above

# The app name that will be used by celery
celery_app_name = airflow.executors.celery_executor

# The concurrency that will be used when starting workers with the
# ``airflow celery worker`` command. This defines the number of task instances that
# a worker will take, so size up your workers based on the resources on
# your worker box and the nature of your tasks
worker_concurrency = 16

# The maximum and minimum concurrency that will be used when starting workers with the
# ``airflow celery worker`` command (always keep minimum processes, but grow
# to maximum if necessary). Note the value should be max_concurrency,min_concurrency
# Pick these numbers based on resources on worker box and the nature of the task.
# If autoscale option is available, worker_concurrency will be ignored.
# http://docs.celeryproject.org/en/latest/reference/celery.bin.worker.html#cmdoption-celery-worker-autoscale
# worker_autoscale = 16,12

# When you start an airflow worker, airflow starts a tiny web server
# subprocess to serve the workers local log files to the airflow main
# web server, who then builds pages and sends them to users. This defines
# the port on which the logs are served. It needs to be unused, and open
# visible from the main web server to connect into the workers.
worker_log_server_port = 8793

# The Celery broker URL. Celery supports RabbitMQ, Redis and experimentally
# a sqlalchemy database. Refer to the Celery documentation for more
# information.
broker_url = redis://redis:6379/0

# The Celery result_backend. When a job is done, it needs to be stored somewhere.
# The backend is used for storing the state of the job and any results.
result_backend = db+postgresql://airflow:airflow@postgres/airflow

# Celery Flower is a sweet UI for Celery. Airflow has a shortcut to start
# it ``airflow celery flower``. This defines the IP that Celery Flower runs on
flower_host = 0.0.0.0

# The root URL for Flower
# Example: flower_url_prefix = /flower
flower_url_prefix =

# This defines the port that Celery Flower runs on
flower_port = 5555

# Securing Flower with Basic Authentication
# Accepts user:password pairs separated by a comma
# Example: flower_basic_auth = user1:password1,user2:password2
flower_basic_auth =

# Default queue that tasks get assigned to and that worker listen on.
default_queue = default

# How many processes CeleryExecutor uses to sync task state.
# 0 means to use max(1, number of cores - 1) processes.
sync_parallelism = 0

# Import path for celery configuration options
celery_config_options = airflow.config_templates.default_celery.DEFAULT_CELERY_CONFIG

# In case of using SSL
ssl_active = False
ssl_key =
ssl_cert =
ssl_cacert =

[celery_broker_transport_options]
# This section is for specifying options which can be passed to the
# underlying celery broker transport. See:
# http://docs.celeryproject.org/en/latest/userguide/configuration.html#std:setting-broker_transport_options

# The visibility timeout defines the number of seconds to wait for the worker
# to acknowledge the task before the message is redelivered to another worker.
# Make sure to increase the visibility timeout to match the time of the longest
# ETA you're planning to use.
#
# visibility_timeout is only supported for Redis and SQS celery brokers.
# See:
#   http://docs.celeryproject.org/en/master/userguide/configuration.html#std:setting-broker_transport_options
#
# Example: visibility_timeout = 21600
# visibility_timeout =

[dask]
# This section only applies if you are using the DaskExecutor in
# ``[core]`` section above

# The IP address and port of the Dask cluster's scheduler.
cluster_address = 127.0.0.1:8786

# TLS/ SSL settings to access a secured Dask scheduler.
tls_ca =
tls_cert =
tls_key =

[scheduler]
# Task instances listen for external kill signal (when you clear tasks
# from the CLI or the UI), this defines the frequency at which they should
# listen (in seconds).
job_heartbeat_sec = 5

# The scheduler constantly tries to trigger new tasks (look at the
# scheduler section in the docs for more information). This defines
# how often the scheduler should run (in seconds).
scheduler_heartbeat_sec = 5

# After how much time should the scheduler terminate in seconds
# -1 indicates to run continuously (see also num_runs)
run_duration = -1

# The number of times to try to schedule each DAG file
# -1 indicates unlimited number
num_runs = -1

# The number of seconds to wait between consecutive DAG file processing
processor_poll_interval = 1

# after how much time (seconds) a new DAGs should be picked up from the filesystem
min_file_process_interval = 0

# How often (in seconds) to scan the DAGs directory for new files. Default to 5 minutes.
dag_dir_list_interval = 300

# How often should stats be printed to the logs. Setting to 0 will disable printing stats
print_stats_interval = 30

# If the last scheduler heartbeat happened more than scheduler_health_check_threshold
# ago (in seconds), scheduler is considered unhealthy.
# This is used by the health check in the "/health" endpoint
scheduler_health_check_threshold = 30

# How often (in seconds) should the scheduler check for orphaned tasks.
orphaned_tasks_check_interval = 300

# How often (in seconds) should the scheduler check for tasks that are ready to be retried.
retry_task_check_interval = 300

# How often (in seconds) should the scheduler check for tasks that are ready to be failed.
task_failures_check_interval = 300

# How often (in seconds) should the scheduler check for zombie tasks.
zombie_detection_interval = 300

# Turn off scheduler catchup by setting this to False.
# Default behavior is unchanged and
# Command Line Backfills still work, but the scheduler
# will not do scheduler catchup if this is False,
# however it can be set on a per DAG basis in the
# DAG definition (catchup)
catchup_by_default = True

# This changes the batch size of queries in the scheduling main loop.
# If this is too high, SQL query performance may be impacted by one
# or more of the following:
# - reversion of mutations in the database
# - excessive locking
# - loss of opportunities for parallelism of DB work
# If this is too low, you may encounter:
# - more overhead from having to process more batches
# - inability to schedule high-concurrency DAGs
max_tis_per_query = 512

# Should the scheduler issue ``SELECT ... FOR UPDATE`` in relevant queries.
# If this is set to False then there is a good chance of race conditions
# causing tasks to be run multiple times, and as a result, the scheduler
# will not be "at most once". If you are willing to risk tasks being
# run multiple times, and still want to run the scheduler in a distributed
# setup, you can set this to False.
use_row_level_locking = True

# Max number of DAGs to create DagRun instances for per scheduler loop
max_dagruns_to_create_per_loop = 10

# How many DagRuns should a scheduler examine (and lock) when scheduling
# and queuing tasks.
max_dagruns_per_loop_to_schedule = 20

# Should the Task supervisor process perform a "mini scheduler" to attempt to schedule more tasks of the
# same DAG. Leaving this on will mean tasks in the same DAG execute quicker, but might starve out other
# dags in some circumstances
schedule_after_task_execution = True

# The scheduler can run multiple processes in parallel to parse dags.
# This defines how many processes will run.
parsing_processes = 2

# Turn off scheduler use of cron intervals by setting this to False.
# DAGs submitted manually in the web UI or with trigger_dag will still run.
use_job_schedule = True

# Allow externally triggered DagRuns for Execution Dates in the future
# Only has effect if schedule_interval is set to None in DAG
allow_trigger_in_future = False

[kerberos]
ccache = /tmp/airflow_krb5_ccache

# gets augmented with fqdn
principal = airflow

reinit_frequency = 3600

kinit_path = kinit

keytab = airflow.keytab

[github_enterprise]
api_rev = v3

[admin]
# UI to hide sensitive variable fields when set to True
hide_sensitive_variable_fields = True

[elasticsearch]
# Elasticsearch host
host =

# Format of the log_id, which is used to query for a given tasks logs
log_id_template = {dag_id}-{task_id}-{execution_date}-{try_number}

# Used to mark the end of a log stream for a task
end_of_log_mark = end_of_log

# Qualified URL for an elasticsearch frontend (like Kibana) with a template argument for log_id
# Code will construct log_id using the log_id_template from the argument list
frontend =

# Write the task logs to the stdout of the worker, rather than the default files
write_stdout = False

# Instead of the default log formatter, write the log lines as JSON
json_format = False

# Log fields to also attach to the json output, if enabled
json_fields = asctime, filename, lineno, levelname, message

[elasticsearch_configs]
use_ssl = False
verify_certs = True

[kubernetes]
# The repository, tag and imagePullPolicy of the Kubernetes Image for the Worker to Run
worker_container_repository =

# Relative path to the Kubernetes config file to use for authentication
# If set to empty string (default), we will use the default config file
config_file =

# The command to use to start the Airflow worker
worker_command = airflow celery worker

# When set to True, the worker pods will be deleted upon termination
delete_worker_pods = True

# Number of Kubernetes worker pods to launch at the start
worker_initial_starting_pod_count = 0

# The maximum number of worker pods to launch
worker_maximum_pods = 100

# The maximum number of worker pods to launch per scheduler loop
worker_pods_creation_batch_size = 1

# The maximum number of seconds to wait for a worker pod to start
worker_pods_pending_timeout = 300

# The maximum number of seconds to wait for a worker pod to reach running state
worker_pods_pending_timeout_check_interval = 120

# The maximum number of seconds to wait for a worker pod to complete
worker_pods_queued_check_interval = 60

# The Kubernetes namespace to use for the worker pods
namespace = default

# The name of the Kubernetes configmap containing the Airflow config
configmap =

# The name of the Kubernetes secret containing the Airflow connections
secret =

# The name of the Kubernetes service account to use for the worker pods
service_account_name =

# The name of the Kubernetes image pull secret
image_pull_secrets =

# The Kubernetes node selector to use for the worker pods
node_selectors =

# The Kubernetes affinity to use for the worker pods
affinity =

# The Kubernetes tolerations to use for the worker pods
tolerations =

# The Kubernetes security context to use for the worker pods
security_context =

# The Kubernetes resources to use for the worker pods
resources =

# The Kubernetes annotations to use for the worker pods
annotations =

# The Kubernetes labels to use for the worker pods
labels =

# The Kubernetes env vars to use for the worker pods
env_vars =

# The Kubernetes pod template file to use for the worker pods
pod_template_file =

# The Kubernetes pod override to use for the worker pods
pod_override =

# The Kubernetes image pull policy to use for the worker pods
image_pull_policy = IfNotPresent

# The Kubernetes restart policy to use for the worker pods
restart_policy = Never

# The Kubernetes termination grace period to use for the worker pods
termination_grace_period = 30

# The Kubernetes dns policy to use for the worker pods
dns_policy = ClusterFirst

# The Kubernetes host network to use for the worker pods
hostnetwork = False

# The Kubernetes share process namespace to use for the worker pods
share_process_namespace = False

# The Kubernetes priority class name to use for the worker pods
priority_class_name =

# The Kubernetes scheduler name to use for the worker pods
scheduler_name =

# The Kubernetes init containers to use for the worker pods
init_containers =

# The Kubernetes sidecar containers to use for the worker pods
sidecar_containers =

# The Kubernetes volumes to use for the worker pods
volumes =

# The Kubernetes volume mounts to use for the worker pods
volume_mounts =

# The Kubernetes readiness probe to use for the worker pods
readiness_probe =

# The Kubernetes liveness probe to use for the worker pods
liveness_probe =

# The Kubernetes startup probe to use for the worker pods
startup_probe =

# The Kubernetes lifecycle to use for the worker pods
lifecycle =

# The Kubernetes container ports to use for the worker pods
container_ports =

# The Kubernetes host aliases to use for the worker pods
host_aliases =

# The Kubernetes dns config to use for the worker pods
dns_config =

# The Kubernetes runtime class name to use for the worker pods
runtime_class_name =

# The Kubernetes enable service links to use for the worker pods
enable_service_links = True

# The Kubernetes preemption policy to use for the worker pods
preemption_policy = PreemptLowerPriority

# The Kubernetes topology spread constraints to use for the worker pods
topology_spread_constraints =

# The Kubernetes set hostname as fqdn to use for the worker pods
set_hostname_as_fqdn = False

# The Kubernetes host ipc to use for the worker pods
host_ipc = False

# The Kubernetes host pid to use for the worker pods
host_pid = False

# The Kubernetes image gc policy to use for the worker pods
image_gc_policy = Always

# The Kubernetes node affinity to use for the worker pods
node_affinity =

# The Kubernetes pod affinity to use for the worker pods
pod_affinity =

# The Kubernetes pod anti-affinity to use for the worker pods
pod_anti_affinity =

# The Kubernetes toleration operator to use for the worker pods
toleration_operator = Equal

# The Kubernetes toleration effect to use for the worker pods
toleration_effect =

# The Kubernetes toleration key to use for the worker pods
toleration_key =

# The Kubernetes toleration value to use for the worker pods
toleration_value =

# The Kubernetes toleration toleration seconds to use for the worker pods
toleration_toleration_seconds =

# The Kubernetes security context run as user to use for the worker pods
security_context_run_as_user =

# The Kubernetes security context run as group to use for the worker pods
security_context_run_as_group =

# The Kubernetes security context fs group to use for the worker pods
security_context_fs_group =

# The Kubernetes security context run as non root to use for the worker pods
security_context_run_as_non_root = False

# The Kubernetes security context read only root filesystem to use for the worker pods
security_context_read_only_root_filesystem = False

# The Kubernetes security context allow privilege escalation to use for the worker pods
security_context_allow_privilege_escalation = True

# The Kubernetes security context privileged to use for the worker pods
security_context_privileged = False

# The Kubernetes security context capabilities to use for the worker pods
security_context_capabilities =

# The Kubernetes security context se linux options to use for the worker pods
security_context_se_linux_options =

# The Kubernetes security context windows options to use for the worker pods
security_context_windows_options =

# The Kubernetes security context supplemental groups to use for the worker pods
security_context_supplemental_groups =

# The Kubernetes security context sysctls to use for the worker pods
security_context_sysctls =

# The Kubernetes security context fs group change policy to use for the worker pods
security_context_fs_group_change_policy =

# The Kubernetes security context seccomp profile to use for the worker pods
security_context_seccomp_profile =

# The Kubernetes security context app armor profile to use for the worker pods
security_context_app_armor_profile =

# The Kubernetes security context capabilities add to use for the worker pods
security_context_capabilities_add =

# The Kubernetes security context capabilities drop to use for the worker pods
security_context_capabilities_drop =
```

## 监控配置示例

### prometheus.yml
```yaml
global:
  scrape_interval:     15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
    - targets: ['localhost:9090']

  - job_name: 'airflow'
    static_configs:
    - targets: ['airflow-webserver:8080']
```

### grafana_dashboard.json
```json
{
  "dashboard": {
    "id": null,
    "title": "Airflow Monitoring Dashboard",
    "timezone": "browser",
    "schemaVersion": 16,
    "version": 0,
    "refresh": "25s",
    "rows": [
      {
        "title": "Overview",
        "height": "250px",
        "panels": [
          {
            "id": 1,
            "type": "graph",
            "title": "DAG Execution Time",
            "datasource": "Prometheus",
            "targets": [
              {
                "expr": "airflow_dag_run_duration",
                "legendFormat": "{{dag_id}}",
                "refId": "A"
              }
            ],
            "xaxis": {
              "show": true
            },
            "yaxes": [
              {
                "format": "s",
                "label": "Duration",
                "logBase": 1,
                "show": true
              },
              {
                "format": "short",
                "logBase": 1,
                "show": true
              }
            ]
          }
        ]
      }
    ]
  }
}
```

## 告警规则示例

### alert_rules.yml
```yaml
groups:
- name: airflow_alerts
  rules:
  - alert: AirflowDAGFailed
    expr: airflow_dag_run_state{state="failed"} > 0
    for: 1m
    labels:
      severity: critical
    annotations:
      summary: "Airflow DAG failed"
      description: "DAG {{ $labels.dag_id }} has failed"

  - alert: AirflowTaskFailed
    expr: airflow_task_instance_state{state="failed"} > 0
    for: 1m
    labels:
      severity: warning
    annotations:
      summary: "Airflow task failed"
      description: "Task {{ $labels.task_id }} in DAG {{ $labels.dag_id }} has failed"

  - alert: HighCPUUsage
    expr: rate(node_cpu_seconds_total{mode!="idle"}[1m]) > 0.8
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "High CPU usage"
      description: "CPU usage is above 80% for more than 2 minutes"
```