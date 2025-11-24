#!/bin/bash
# send_signals.sh
# 用于向Gunicorn进程发送信号的脚本

set -e

# Gunicorn PID文件路径
PID_FILE="/tmp/gunicorn_example.pid"

# 检查PID文件是否存在
if [ ! -f "${PID_FILE}" ]; then
    echo "PID file not found at ${PID_FILE}"
    echo "Please start Gunicorn with a PID file:"
    echo "gunicorn -p ${PID_FILE} signal_test:application"
    exit 1
fi

# 读取PID
MASTER_PID=$(cat "${PID_FILE}")

if [ -z "${MASTER_PID}" ]; then
    echo "Failed to read PID from ${PID_FILE}"
    exit 1
fi

# 信号处理函数
send_signal() {
    local signal=$1
    local description=$2
    
    echo "Sending ${signal} (${description}) to Gunicorn master process (PID: ${MASTER_PID})"
    kill -"${signal}" "${MASTER_PID}"
    
    if [ $? -eq 0 ]; then
        echo "Signal sent successfully!"
    else
        echo "Failed to send signal!"
        return 1
    fi
}

# 显示当前Gunicorn进程信息
show_process_info() {
    echo "Gunicorn Process Information:"
    echo "Master PID: ${MASTER_PID}"
    
    if [ -d "/proc/${MASTER_PID}" ]; then
        echo "Master process is running"
        
        # 显示工作进程信息
        echo "Worker processes:"
        pgrep -P "${MASTER_PID}" | while read -r worker_pid; do
            echo "  Worker PID: ${worker_pid}"
        done
    else
        echo "Master process is not running!"
    fi
}

# 主菜单
show_menu() {
    echo ""
    echo "Gunicorn Signal Test Menu:"
    echo "========================="
    echo "1. Show process information"
    echo "2. Send HUP (reload configuration)"
    echo "3. Send TERM (graceful shutdown)"
    echo "4. Send INT (immediate shutdown)"
    echo "5. Send USR1 (reopen logs)"
    echo "6. Send USR2 (upgrade executable)"
    echo "7. Send WINCH (reduce workers)"
    echo "8. Send custom signal"
    echo "9. Exit"
    echo ""
    echo -n "Select an option: "
}

# 发送自定义信号
send_custom_signal() {
    echo -n "Enter signal number (e.g., 10 for SIGUSR1): "
    read -r signal_num
    echo -n "Enter signal description: "
    read -r signal_desc
    
    send_signal "${signal_num}" "${signal_desc}"
}

# 主循环
while true; do
    show_menu
    read -r choice
    
    case ${choice} in
        1)
            show_process_info
            ;;
        2)
            send_signal "HUP" "reload configuration"
            ;;
        3)
            send_signal "TERM" "graceful shutdown"
            ;;
        4)
            send_signal "INT" "immediate shutdown"
            ;;
        5)
            send_signal "USR1" "reopen logs"
            ;;
        6)
            send_signal "USR2" "upgrade executable"
            ;;
        7)
            send_signal "WINCH" "reduce workers"
            ;;
        8)
            send_custom_signal
            ;;
        9)
            echo "Exiting..."
            exit 0
            ;;
        *)
            echo "Invalid option. Please try again."
            ;;
    esac
    
    echo ""
    echo "Press Enter to continue..."
    read -r
done