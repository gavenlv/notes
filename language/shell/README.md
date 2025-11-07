# Shell 脚本学习笔记

## 概述

Shell脚本是一种为Shell编写的脚本程序，用于自动化执行一系列命令。Shell是用户与操作系统内核之间的接口，它解释用户输入的命令并将其传递给操作系统执行。常见的Shell包括Bash（Bourne Again Shell）、Zsh、Ksh等。Shell脚本广泛应用于系统管理、任务自动化、文件处理、软件开发等领域，是Linux/Unix系统管理员和开发人员必备的技能之一。

## 目录结构

```
shell/
├── basics/                 # Shell基础
│   ├── introduction.md    # Shell介绍
│   ├── shell-types.md     # Shell类型
│   ├── first-script.md    # 第一个脚本
│   ├── execution.md       # 脚本执行
│   └── shebang.md         # Shebang解释
├── syntax/                 # 语法基础
│   ├── variables.md       # 变量
│   ├── strings.md         # 字符串
│   ├── arrays.md          # 数组
│   ├── parameters.md      # 参数
│   └── comments.md        # 注释
├── commands/               # 常用命令
│   ├── file-operations.md # 文件操作
│   ├── text-processing.md # 文本处理
│   ├── process-management.md # 进程管理
│   ├── system-info.md     # 系统信息
│   └── network.md         # 网络命令
├── flow-control/           # 流程控制
│   ├── conditionals.md    # 条件语句
│   ├── loops.md           # 循环
│   ├── functions.md       # 函数
│   ├── case.md            # case语句
│   └── exit-codes.md      # 退出码
├── io-redirection/         # 输入输出重定向
│   ├── redirection.md     # 重定向
│   ├── pipes.md           # 管道
│   ├── file-descriptors.md # 文件描述符
│   └── here-documents.md  # Here文档
├── pattern-matching/       # 模式匹配
│   ├── wildcards.md       # 通配符
│   ├── regular-expressions.md # 正则表达式
│   ├── globbing.md        # 文件名展开
│   └── pattern-substitution.md # 模式替换
├── text-processing/        # 文本处理
│   ├── grep.md            # grep命令
│   ├── sed.md             # sed命令
│   ├── awk.md             # awk命令
│   ├── cut.md             # cut命令
│   └── sort.md            # sort命令
├── process-management/     # 进程管理
│   ├── background.md      # 后台进程
│   ├── job-control.md     # 作业控制
│   ├── signals.md         # 信号
│   ├── ps.md              # ps命令
│   └── kill.md            # kill命令
├── file-system/            # 文件系统
│   ├── permissions.md     # 文件权限
│   ├── ownership.md       # 文件所有权
│   ├── find.md            # find命令
│   ├── ln.md              # 链接
│   └── mount.md           # 挂载
├── networking/             # 网络编程
│   ├── tcp-ip.md          # TCP/IP基础
│   ├── curl.md            # curl命令
│   ├── wget.md            # wget命令
│   ├── ssh.md             # SSH命令
│   └── netstat.md         # netstat命令
├── automation/             # 自动化
│   ├── cron.md            # 定时任务
│   ├── systemd.md         # systemd服务
│   ├── backup.md          # 备份脚本
│   └── monitoring.md      # 监控脚本
├── debugging/              # 调试
│   ├── debugging.md       # 调试技巧
│   ├── logging.md         # 日志记录
│   ├── error-handling.md  # 错误处理
│   └── testing.md         # 脚本测试
├── security/               # 安全
│   ├── permissions.md     # 权限管理
│   ├── encryption.md      # 加密
│   ├── security-hardening.md # 安全加固
│   └── audit.md           # 安全审计
├── performance/            # 性能优化
│   ├── profiling.md       # 性能分析
│   ├── optimization.md    # 优化技巧
│   ├── parallelism.md     # 并行处理
│   └── benchmarking.md    # 性能测试
├── advanced/               # 高级主题
│   ├── advanced-scripts.md # 高级脚本
│   ├── libraries.md       # 脚本库
│   ├── gui.md             # GUI脚本
│   ├── database.md        # 数据库交互
│   └── api.md             # API交互
└── examples/               # 示例脚本
    ├── system-admin.md    # 系统管理示例
    ├── file-processing.md # 文件处理示例
    ├── backup-restore.md # 备份恢复示例
    ├── monitoring.md      # 监控示例
    └── automation.md      # 自动化示例
```

## 学习路径

### 初学者路径
1. **Shell基础** - 了解Shell的概念、类型和基本用法
2. **第一个脚本** - 编写并执行简单的Shell脚本
3. **基本语法** - 学习变量、字符串、注释等基本语法
4. **常用命令** - 掌握常用的文件操作和系统命令
5. **流程控制** - 学习条件语句和循环

### 进阶路径
1. **输入输出重定向** - 掌握重定向和管道的使用
2. **模式匹配** - 学习通配符和正则表达式
3. **文本处理** - 掌握grep、sed、awk等文本处理工具
4. **函数和参数** - 学习如何定义函数和处理参数
5. **错误处理** - 掌握错误处理和调试技巧

### 高级路径
1. **进程管理** - 学习后台进程、作业控制和信号处理
2. **文件系统** - 深入了解文件权限、所有权和文件系统操作
3. **网络编程** - 掌握网络命令和网络编程基础
4. **自动化** - 学习定时任务、系统服务和监控脚本
5. **高级主题** - 探索脚本库、GUI脚本和API交互

## 常见问题

### Q: Bash和其他Shell（如Zsh、Ksh）有什么区别？
A: 不同Shell的主要区别：
- **Bash**：最常用的Shell，大多数Linux发行版的默认Shell
- **Zsh**：功能更丰富的Shell，支持更多插件和主题
- **Ksh**：Korn Shell，语法更接近传统Shell
- **Fish**：用户友好的Shell，具有智能补全功能
- **兼容性**：Bash脚本通常在其他Shell中运行良好，但特定功能可能不兼容
- **性能**：不同Shell的启动和执行速度可能有差异
- **特性**：不同Shell支持不同的特性和语法扩展

### Q: 如何处理Shell脚本中的空格和特殊字符？
A: 处理空格和特殊字符的方法：
- **引号**：使用单引号或双引号包围包含空格的字符串
- **转义**：使用反斜杠(\)转义特殊字符
- **变量引用**：使用双引号包围变量引用以处理空格
- **数组**：使用数组处理包含空格的多个值
- **IFS**：调整内部字段分隔符处理空格
- **find命令**：使用-print0和xargs -0处理包含空格的文件名

### Q: 如何使Shell脚本更安全？
A: 提高Shell脚本安全性的方法：
- **使用set命令**：启用严格模式(set -euo pipefail)
- **输入验证**：验证所有用户输入
- **最小权限**：以最小必要权限运行脚本
- **避免eval**：避免使用eval等危险命令
- **引用变量**：正确引用变量以防止注入攻击
- **错误处理**：添加适当的错误处理和日志记录
- **临时文件**：安全创建和处理临时文件

## 资源链接

- [Bash参考手册](https://www.gnu.org/software/bash/manual/)
- [Shell脚本编程指南](https://google.github.io/styleguide/shellguide.html)
- [Advanced Bash-Scripting Guide](https://tldp.org/LDP/abs/html/)
- [ShellCheck - Shell脚本分析工具](https://www.shellcheck.net/)
- [ExplainShell - Shell命令解释器](https://explainshell.com/)

## 代码示例

### 基本语法

```bash
#!/bin/bash

# 注释：这是Shell脚本

# 变量定义和引用
name="Alice"
age=30
echo "姓名: $name"
echo "年龄: $age"

# 命令替换
current_date=$(date)
echo "当前日期: $current_date"

# 算术运算
a=10
b=5
sum=$((a + b))
echo "10 + 5 = $sum"

# 条件语句
if [ $age -ge 18 ]; then
    echo "成年人"
else
    echo "未成年人"
fi

# 循环
for i in {1..5}; do
    echo "数字: $i"
done

# 函数
greet() {
    echo "Hello, $1!"
}

greet "Bob"

# 数组
fruits=("apple" "banana" "orange")
echo "第一个水果: ${fruits[0]}"
echo "所有水果: ${fruits[@]}"
```

### 字符串操作

```bash
#!/bin/bash

# 字符串定义
str1="Hello"
str2="World"

# 字符串连接
greeting="$str1 $str2"
echo "$greeting"

# 字符串长度
echo "字符串长度: ${#greeting}"

# 子字符串提取
echo "子字符串: ${greeting:0:5}"  # 从位置0开始，取5个字符

# 字符串替换
echo "替换前: $greeting"
echo "替换后: ${greeting/World/Shell}"

# 字符串查找
if [[ $greeting == *"World"* ]]; then
    echo "字符串包含'World'"
fi

# 大小写转换
echo "大写: ${greeting^^}"
echo "小写: ${greeting,,}"

# 字符串分割
IFS=' ' read -ra words <<< "$greeting"
echo "第一个单词: ${words[0]}"
echo "第二个单词: ${words[1]}"

# 去除前后空格
trim_str="   Hello World   "
trimmed=$(echo "$trim_str" | xargs)
echo "去除空格后: '$trimmed'"

# 字符串比较
str3="hello"
if [[ "$str1" == "$str3" ]]; then
    echo "字符串相等"
else
    echo "字符串不相等"
fi

# 模式匹配
filename="document.txt"
if [[ $filename == *.txt ]]; then
    echo "这是一个文本文件"
fi

# 正则表达式匹配
if [[ $filename =~ ^[a-z]+\.txt$ ]]; then
    echo "文件名符合模式"
fi
```

### 数组操作

```bash
#!/bin/bash

# 数组定义
fruits=("apple" "banana" "orange" "grape")

# 访问数组元素
echo "第一个水果: ${fruits[0]}"
echo "所有水果: ${fruits[@]}"

# 数组长度
echo "水果数量: ${#fruits[@]}"

# 遍历数组
echo "遍历数组:"
for fruit in "${fruits[@]}"; do
    echo "- $fruit"
done

# 添加元素
fruits+=("mango")
echo "添加后: ${fruits[@]}"

# 删除元素
unset fruits[1]  # 删除索引1的元素
echo "删除后: ${fruits[@]}"

# 数组切片
echo "数组切片: ${fruits[@]:1:2}"  # 从索引1开始，取2个元素

# 关联数组（字典）
declare -A person
person[name]="Alice"
person[age]=30
person[city]="New York"

echo "姓名: ${person[name]}"
echo "年龄: ${person[age]}"
echo "城市: ${person[city]}"

# 遍历关联数组
echo "遍历关联数组:"
for key in "${!person[@]}"; do
    echo "$key: ${person[$key]}"
done

# 数组排序
numbers=(5 2 8 1 9)
IFS=$'\n' sorted=($(sort -n <<<"${numbers[*]}"))
unset IFS
echo "排序前: ${numbers[@]}"
echo "排序后: ${sorted[@]}"

# 数组去重
declare -A seen
unique=()
for item in "${numbers[@]}"; do
    if [[ -z "${seen[$item]}" ]]; then
        seen[$item]=1
        unique+=("$item")
    fi
done
echo "去重后: ${unique[@]}"

# 数组交集
array1=(1 2 3 4 5)
array2=(4 5 6 7 8)
declare -A temp
intersection=()

for item in "${array1[@]}"; do
    temp[$item]=1
done

for item in "${array2[@]}"; do
    if [[ -n "${temp[$item]}" ]]; then
        intersection+=("$item")
    fi
done

echo "数组1: ${array1[@]}"
echo "数组2: ${array2[@]}"
echo "交集: ${intersection[@]}"
```

### 流程控制

```bash
#!/bin/bash

# if-elif-else语句
age=25

if [ $age -lt 18 ]; then
    echo "未成年人"
elif [ $age -lt 65 ]; then
    echo "成年人"
else
    echo "老年人"
fi

# 字符串比较
name="Alice"

if [ "$name" = "Alice" ]; then
    echo "欢迎, Alice!"
elif [ "$name" = "Bob" ]; then
    echo "欢迎, Bob!"
else
    echo "欢迎, 访客!"
fi

# 文件测试
file="example.txt"

if [ -f "$file" ]; then
    echo "$file 是一个普通文件"
elif [ -d "$file" ]; then
    echo "$file 是一个目录"
else
    echo "$file 不存在或不是普通文件"
fi

# 逻辑运算
num=10

if [ $num -gt 0 ] && [ $num -lt 100 ]; then
    echo "$num 在0和100之间"
fi

if [ $num -le 0 ] || [ $num -ge 100 ]; then
    echo "$num 不在0和100之间"
fi

# case语句
fruit="apple"

case $fruit in
    "apple")
        echo "这是苹果"
        ;;
    "banana")
        echo "这是香蕉"
        ;;
    "orange"|"grape")
        echo "这是橙子或葡萄"
        ;;
    *)
        echo "未知水果"
        ;;
esac

# for循环
echo "使用for循环遍历数字:"
for i in {1..5}; do
    echo "数字: $i"
done

echo "使用for循环遍历数组:"
colors=("red" "green" "blue")
for color in "${colors[@]}"; do
    echo "颜色: $color"
done

echo "使用for循环遍历文件:"
for file in *.txt; do
    echo "文件: $file"
done

# while循环
count=1
echo "使用while循环:"
while [ $count -le 5 ]; do
    echo "计数: $count"
    ((count++))
done

# until循环
count=1
echo "使用until循环:"
until [ $count -gt 5 ]; do
    echo "计数: $count"
    ((count++))
done

# 循环控制
echo "使用break和continue:"
for i in {1..10}; do
    if [ $i -eq 3 ]; then
        continue  # 跳过3
    fi
    
    if [ $i -eq 7 ]; then
        break     # 在7处停止
    fi
    
    echo "数字: $i"
done

# select循环（菜单）
echo "选择一个选项:"
select option in "选项1" "选项2" "选项3" "退出"; do
    case $option in
        "选项1")
            echo "你选择了选项1"
            ;;
        "选项2")
            echo "你选择了选项2"
            ;;
        "选项3")
            echo "你选择了选项3"
            ;;
        "退出")
            echo "退出菜单"
            break
            ;;
        *)
            echo "无效选项"
            ;;
    esac
done
```

### 函数和参数

```bash
#!/bin/bash

# 基本函数定义
greet() {
    echo "Hello, World!"
}

# 调用函数
greet

# 带参数的函数
greet_person() {
    echo "Hello, $1!"
}

greet_person "Alice"

# 带多个参数的函数
add() {
    local sum=$(( $1 + $2 ))
    echo "$1 + $2 = $sum"
}

add 5 3

# 返回值
check_number() {
    if [ $1 -gt 0 ]; then
        return 0  # 成功
    else
        return 1  # 失败
    fi
}

check_number 10
if [ $? -eq 0 ]; then
    echo "数字是正数"
else
    echo "数字不是正数"
fi

# 返回值（使用echo）
multiply() {
    local result=$(( $1 * $2 ))
    echo $result
}

product=$(multiply 4 5)
echo "4 * 5 = $product"

# 默认参数
greet_with_default() {
    local name=${1:-"Guest"}
    echo "Hello, $name!"
}

greet_with_default          # 使用默认值
greet_with_default "Bob"   # 使用提供的值

# 可变参数
sum_all() {
    local sum=0
    for num in "$@"; do
        sum=$((sum + num))
    done
    echo $sum
}

total=$(sum_all 1 2 3 4 5)
echo "总和: $total"

# 局部变量和全局变量
global_var="全局变量"

test_scope() {
    local local_var="局部变量"
    echo "函数内: $global_var"
    echo "函数内: $local_var"
}

test_scope
echo "函数外: $global_var"
# echo "函数外: $local_var"  # 这行会出错，local_var在函数外不可见

# 递归函数
factorial() {
    local n=$1
    if [ $n -le 1 ]; then
        echo 1
    else
        local prev=$(factorial $((n - 1)))
        echo $((n * prev))
    fi
}

fact=$(factorial 5)
echo "5! = $fact"

# 函数库
# 创建函数库文件: mylib.sh
# source mylib.sh  # 在脚本中加载函数库

# 命令行参数处理
process_args() {
    echo "脚本名称: $0"
    echo "参数数量: $#"
    echo "所有参数: $@"
    
    # 使用getopts处理选项
    while getopts ":a:b:" opt; do
        case $opt in
            a)
                echo "选项 -a 的值: $OPTARG"
                ;;
            b)
                echo "选项 -b 的值: $OPTARG"
                ;;
            \?)
                echo "无效选项: -$OPTARG"
                ;;
            :)
                echo "选项 -$OPTARG 需要参数"
                ;;
        esac
    done
}

# 调用函数处理参数
process_args "$@"
```

### 文件操作

```bash
#!/bin/bash

# 检查文件是否存在
file="example.txt"

if [ -f "$file" ]; then
    echo "$file 存在"
else
    echo "$file 不存在"
fi

# 创建文件
touch "$file"
echo "创建了文件: $file"

# 写入文件
echo "Hello, World!" > "$file"  # 覆盖写入
echo "追加内容" >> "$file"      # 追加写入

# 读取文件
echo "文件内容:"
cat "$file"

# 逐行读取文件
echo "逐行读取:"
while IFS= read -r line; do
    echo "行: $line"
done < "$file"

# 复制文件
cp "$file" "${file}.bak"
echo "复制了文件: ${file}.bak"

# 移动/重命名文件
mv "${file}.bak" "backup.txt"
echo "重命名文件为: backup.txt"

# 删除文件
rm "backup.txt"
echo "删除了文件: backup.txt"

# 文件权限
chmod 644 "$file"
echo "设置文件权限为644"

# 文件信息
echo "文件信息:"
ls -l "$file"

# 文件大小
size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
echo "文件大小: $size 字节"

# 文件修改时间
mtime=$(stat -c%y "$file" 2>/dev/null || stat -f%Sm "$file" 2>/dev/null)
echo "修改时间: $mtime"

# 查找文件
echo "查找当前目录下的所有.txt文件:"
find . -name "*.txt" -type f

echo "查找大于1KB的文件:"
find . -size +1k -type f

# 目录操作
dir="test_dir"

# 创建目录
mkdir -p "$dir"
echo "创建了目录: $dir"

# 创建子目录
mkdir -p "$dir/subdir1" "$dir/subdir2"
echo "创建了子目录"

# 列出目录内容
echo "目录内容:"
ls -la "$dir"

# 复制目录
cp -r "$dir" "${dir}_copy"
echo "复制了目录: ${dir}_copy"

# 移动目录
mv "${dir}_copy" "backup_dir"
echo "移动了目录: backup_dir"

# 删除目录
rm -rf "backup_dir"
echo "删除了目录: backup_dir"

# 检查目录是否为空
if [ -z "$(ls -A "$dir")" ]; then
    echo "目录 $dir 为空"
else
    echo "目录 $dir 不为空"
fi

# 临时文件
temp_file=$(mktemp)
echo "创建了临时文件: $temp_file"
echo "临时内容" > "$temp_file"

# 使用临时文件
cat "$temp_file"

# 删除临时文件
rm "$temp_file"
echo "删除了临时文件"

# 文件内容处理
# 统计行数
line_count=$(wc -l < "$file")
echo "文件行数: $line_count"

# 统计单词数
word_count=$(wc -w < "$file")
echo "文件单词数: $word_count"

# 统计字符数
char_count=$(wc -c < "$file")
echo "文件字符数: $char_count"

# 查找包含特定文本的行
echo "包含'Hello'的行:"
grep "Hello" "$file"

# 替换文件中的文本
sed -i 's/World/Shell/g' "$file"
echo "替换后的文件内容:"
cat "$file"

# 提取文件的特定列
echo "提取文件的第一个单词:"
cut -d' ' -f1 "$file"

# 排序文件内容
echo "排序文件内容:"
sort "$file"

# 去重
echo "去重后的内容:"
sort "$file" | uniq
```

### 进程管理

```bash
#!/bin/bash

# 查看当前Shell的进程ID
echo "当前Shell进程ID: $$"

# 查看父进程ID
echo "父进程ID: $PPID"

# 后台运行命令
echo "在后台运行sleep命令:"
sleep 10 &
bg_pid=$!
echo "后台进程ID: $bg_pid"

# 查看进程状态
ps -p $bg_pid

# 等待后台进程完成
echo "等待后台进程完成..."
wait $bg_pid
echo "后台进程已完成"

# 作业控制
echo "启动多个后台作业:"
sleep 5 &  # 作业1
sleep 10 & # 作业2
sleep 15 & # 作业3

# 查看当前作业
echo "当前作业:"
jobs

# 将后台作业切换到前台
echo "将作业2切换到前台:"
%2

# 挂起当前前台作业（按Ctrl+Z）
# 将挂起的作业放到后台执行
bg

# 终止作业
kill %1  # 终止作业1

# 查看系统进程
echo "系统进程信息:"
ps aux

# 查看特定进程
echo "查看bash进程:"
ps aux | grep bash

# 查看进程树
echo "进程树:"
pstree

# 查看进程资源使用情况
echo "进程资源使用情况:"
top -b -n 1 | head -20

# 终止进程
echo "终止进程示例:"
sleep 100 &
pid=$!
echo "启动了进程: $pid"

# 发送SIGTERM信号（优雅终止）
kill $pid
echo "发送了SIGTERM信号"

# 检查进程是否存在
if kill -0 $pid 2>/dev/null; then
    echo "进程 $pid 仍在运行"
else
    echo "进程 $pid 已终止"
fi

# 强制终止进程
# kill -9 $pid  # 发送SIGKILL信号（强制终止）

# 查看进程打开的文件
echo "查看当前Shell打开的文件:"
lsof -p $$

# 查看端口使用情况
echo "查看端口使用情况:"
netstat -tuln 2>/dev/null || ss -tuln

# 查看网络连接
echo "查看网络连接:"
netstat -tuln 2>/dev/null || ss -tuln

# 限制进程资源使用
echo "限制CPU使用时间:"
ulimit -t 60  # 限制CPU时间为60秒

# 查看当前资源限制
echo "当前资源限制:"
ulimit -a

# 进程优先级
echo "查看当前进程优先级:"
ps -o pid,ppid,ni,cmd -p $$

# 调整进程优先级
echo "降低当前进程优先级:"
renice +10 -p $$

# 后台守护进程示例
create_daemon() {
    # 创建守护进程
    (
        # 切换到根目录
        cd /
        
        # 重定向标准输入、输出和错误
        exec < /dev/null
        exec > /var/log/daemon.log 2>&1
        
        # 主循环
        while true; do
            echo "Daemon running at $(date)"
            sleep 60
        done
    ) &
    
    echo "守护进程已启动，PID: $!"
}

# 注意：实际运行守护进程需要适当的权限
# create_daemon

# 进程间通信（使用命名管道）
echo "进程间通信示例:"
pipe="/tmp/test_pipe"

# 创建命名管道
mkfifo "$pipe"

# 在后台启动读取进程
(
    while true; do
        if read -r msg < "$pipe"; then
            echo "读取进程收到消息: $msg"
            if [ "$msg" = "exit" ]; then
                break
            fi
        fi
    done
) &

reader_pid=$!

# 发送消息
echo "Hello" > "$pipe"
sleep 1
echo "World" > "$pipe"
sleep 1
echo "exit" > "$pipe"

# 等待读取进程完成
wait $reader_pid

# 清理命名管道
rm "$pipe"
```

### 输入输出重定向

```bash
#!/bin/bash

# 标准输出重定向
echo "这行文本将被重定向到文件" > output.txt
echo "这行文本将被追加到文件" >> output.txt

# 标准错误重定向
ls /nonexistent_directory 2> error.log
echo "错误信息已重定向到error.log"

# 同时重定向标准输出和标准错误
echo "这行文本和错误信息都将被重定向" > output.txt 2>&1
# 或者使用更简洁的语法
echo "这行文本和错误信息都将被重定向" &> output.txt

# 丢弃输出
echo "这行文本将被丢弃" > /dev/null
ls /nonexistent_directory 2> /dev/null

# 输入重定向
echo "使用输入重定向读取文件内容:"
wc -l < output.txt

# Here文档
cat << EOF
这是一个Here文档
可以包含多行文本
变量替换: $USER
命令替换: $(date)
EOF

# Here字符串
grep "world" <<< "hello world"

# 管道
echo "使用管道连接命令:"
ls -l | grep ".txt" | wc -l

# 复杂管道示例
echo "查找包含'error'的日志行并统计:"
cat /var/log/syslog 2>/dev/null | grep "error" | wc -l

# 文件描述符
echo "使用文件描述符:"
exec 3> output.txt  # 打开文件描述符3用于写入
echo "通过文件描述符3写入" >&3
exec 3>&-          # 关闭文件描述符3

# 读取文件描述符
exec 4< input.txt  # 打开文件描述符4用于读取
while read -u 4 line; do
    echo "读取: $line"
done
exec 4<&-          # 关闭文件描述符4

# 进程替换
echo "使用进程替换:"
diff <(ls -l) <(ls -al)

# 同时使用多个重定向
echo "多重重定向示例:"
{
    echo "标准输出"
    echo "标准错误" >&2
} > output.txt 2> error.txt

# 临时重定向
echo "临时重定向示例:"
exec 3>&1  # 保存标准输出到文件描述符3
exec > output.txt  # 重定向标准输出到文件
echo "这行文本将写入文件"
exec 1>&3  # 恢复标准输出
exec 3>&-  # 关闭文件描述符3
echo "这行文本将显示在终端"

# 重定向循环输出
echo "重定向循环输出:"
for i in {1..5}; do
    echo "数字: $i"
done > loop_output.txt

# 子Shell中的重定向
echo "子Shell中的重定向:"
(echo "子Shell输出") > subshell_output.txt

# 使用tee命令同时输出到文件和终端
echo "使用tee命令:"
echo "这行文本将同时显示在终端和文件中" | tee -a tee_output.txt

# 重定向到多个文件
echo "重定向到多个文件:"
echo "多目标输出" | tee file1.txt > file2.txt

# 条件重定向
echo "条件重定向示例:"
if command -v ls >/dev/null 2>&1; then
    echo "ls命令存在"
else
    echo "ls命令不存在"
fi

# 使用重定向进行错误处理
echo "使用重定向进行错误处理:"
if ! ls /nonexistent_directory >/dev/null 2>&1; then
    echo "目录不存在"
fi

# 重定向和函数
redirect_function() {
    echo "函数输出"
    echo "函数错误" >&2
}

echo "重定向函数输出:"
redirect_function > function_output.txt 2> function_error.txt

# 使用重定向创建空文件
echo "创建空文件:"
> empty_file.txt
touch empty_file2.txt  # 另一种方法

# 使用重定向截断文件
echo "截断文件:"
echo "一些内容" > truncate.txt
echo "文件内容:"
cat truncate.txt
> truncate.txt  # 截断文件
echo "截断后的文件内容:"
cat truncate.txt
```

## 最佳实践

1. **脚本编写**
   - 使用适当的Shebang（#!/bin/bash）
   - 添加脚本描述和使用说明
   - 使用有意义的变量和函数名
   - 添加适当的注释和文档

2. **错误处理**
   - 使用set -euo pipefail启用严格模式
   - 检查命令执行状态
   - 提供有意义的错误信息
   - 使用trap命令处理清理工作

3. **安全性**
   - 验证所有用户输入
   - 使用绝对路径
   - 避免使用eval等危险命令
   - 正确引用变量以防止注入攻击

4. **性能优化**
   - 避免不必要的子Shell
   - 使用内置命令代替外部命令
   - 合理使用管道和重定向
   - 考虑使用并行处理提高效率

5. **可维护性**
   - 将复杂脚本分解为函数
   - 使用配置文件管理参数
   - 编写单元测试
   - 使用版本控制系统

## 贡献指南

欢迎对本学习笔记进行贡献！请遵循以下指南：

1. 确保内容准确、清晰、实用
2. 使用规范的Markdown格式
3. 代码示例需要完整且可运行
4. 添加适当的注释和说明
5. 保持目录结构的一致性

## 注意事项

- 注意不同Shell之间的语法差异
- 考虑脚本的跨平台兼容性
- 正确处理特殊字符和空格
- 注意脚本的执行权限
- 考虑脚本的安全性和性能

---

*最后更新: 2023年*