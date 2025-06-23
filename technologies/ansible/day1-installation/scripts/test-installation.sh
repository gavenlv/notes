#!/bin/bash
# Ansible 安装验证脚本 (Linux/macOS)
# 用于验证 Ansible 安装和配置的正确性

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color

# 参数处理
VERBOSE=false
while [[ $# -gt 0 ]]; do
    case $1 in
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -h|--help)
            echo "用法: $0 [-v|--verbose] [-h|--help]"
            echo "  -v, --verbose    显示详细输出"
            echo "  -h, --help       显示帮助信息"
            exit 0
            ;;
        *)
            echo "未知参数: $1"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}=== Ansible 安装验证脚本 ===${NC}"
echo ""

# 1. 检查 Python 版本
echo -e "${CYAN}1. 检查 Python 版本...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓ $PYTHON_VERSION${NC}"
    
    # 检查 Python 版本是否满足要求 (3.6+)
    PYTHON_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
    PYTHON_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")
    
    if [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -ge 6 ]] || [[ $PYTHON_MAJOR -gt 3 ]]; then
        echo -e "${GREEN}✓ Python 版本满足要求 (3.6+)${NC}"
    else
        echo -e "${RED}✗ Python 版本过低，需要 3.6 或更高版本${NC}"
        exit 1
    fi
else
    echo -e "${RED}✗ Python3 未安装或不在 PATH 中${NC}"
    exit 1
fi

# 2. 检查 pip
echo -e "${CYAN}2. 检查 pip...${NC}"
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version 2>&1)
    echo -e "${GREEN}✓ $PIP_VERSION${NC}"
else
    echo -e "${YELLOW}! pip3 不可用，尝试使用 python3 -m pip${NC}"
    if python3 -m pip --version &> /dev/null; then
        echo -e "${GREEN}✓ python3 -m pip 可用${NC}"
    else
        echo -e "${RED}✗ pip 不可用，请安装 pip${NC}"
        exit 1
    fi
fi

# 3. 检查 Ansible 版本
echo -e "${CYAN}3. 检查 Ansible 版本...${NC}"
if command -v ansible &> /dev/null; then
    ANSIBLE_VERSION=$(ansible --version 2>&1 | head -n1)
    echo -e "${GREEN}✓ $ANSIBLE_VERSION${NC}"
    
    if [[ $VERBOSE == true ]]; then
        echo -e "${WHITE}完整版本信息:${NC}"
        ansible --version | sed 's/^/  /'
    fi
else
    echo -e "${RED}✗ Ansible 未安装或不在 PATH 中${NC}"
    echo -e "${YELLOW}请运行: pip3 install ansible${NC}"
    exit 1
fi

# 4. 检查 Ansible 组件
echo -e "${CYAN}4. 检查 Ansible 组件...${NC}"
COMPONENTS=("ansible-playbook" "ansible-galaxy" "ansible-config" "ansible-doc")
for component in "${COMPONENTS[@]}"; do
    if command -v $component &> /dev/null; then
        echo -e "${GREEN}✓ $component 可用${NC}"
    else
        echo -e "${RED}✗ $component 不可用${NC}"
    fi
done

# 5. 测试本地连接
echo -e "${CYAN}5. 测试本地连接...${NC}"
PING_RESULT=$(ansible localhost -m ping 2>&1)
if [[ $? -eq 0 ]]; then
    echo -e "${GREEN}✓ 本地连接测试成功${NC}"
    if [[ $VERBOSE == true ]]; then
        echo -e "${WHITE}详细输出:${NC}"
        echo "$PING_RESULT" | sed 's/^/  /'
    fi
else
    echo -e "${RED}✗ 本地连接测试失败${NC}"
    echo "$PING_RESULT" | sed 's/^/  /'
fi

# 6. 检查配置文件
echo -e "${CYAN}6. 检查配置文件...${NC}"
CONFIG_LOCATIONS=(
    "$ANSIBLE_CONFIG"
    "./ansible.cfg"
    "$HOME/.ansible.cfg"
    "/etc/ansible/ansible.cfg"
)

FOUND_CONFIG=false
for location in "${CONFIG_LOCATIONS[@]}"; do
    if [[ -n "$location" && -f "$location" ]]; then
        echo -e "${GREEN}✓ 找到配置文件: $location${NC}"
        FOUND_CONFIG=true
        
        if [[ $VERBOSE == true ]]; then
            echo -e "${WHITE}配置文件内容预览:${NC}"
            head -n 10 "$location" | sed 's/^/  /'
            echo "  ..."
        fi
        break
    fi
done

if [[ $FOUND_CONFIG == false ]]; then
    echo -e "${YELLOW}! 未找到配置文件，将使用默认配置${NC}"
fi

# 7. 检查 SSH 密钥
echo -e "${CYAN}7. 检查 SSH 配置...${NC}"
if command -v ssh &> /dev/null; then
    SSH_VERSION=$(ssh -V 2>&1)
    echo -e "${GREEN}✓ SSH 客户端可用: $SSH_VERSION${NC}"
    
    # 检查 SSH 密钥
    if [[ -f "$HOME/.ssh/id_rsa" ]]; then
        echo -e "${GREEN}✓ 找到 SSH 私钥: ~/.ssh/id_rsa${NC}"
    elif [[ -f "$HOME/.ssh/id_ed25519" ]]; then
        echo -e "${GREEN}✓ 找到 SSH 私钥: ~/.ssh/id_ed25519${NC}"
    else
        echo -e "${YELLOW}! 未找到 SSH 密钥，建议生成一个:${NC}"
        echo -e "${WHITE}  ssh-keygen -t rsa -b 4096 -C \"your_email@example.com\"${NC}"
    fi
else
    echo -e "${RED}✗ SSH 客户端不可用${NC}"
fi

# 8. 检查系统依赖
echo -e "${CYAN}8. 检查系统依赖...${NC}"
DEPS=("git" "curl" "wget")
for dep in "${DEPS[@]}"; do
    if command -v $dep &> /dev/null; then
        echo -e "${GREEN}✓ $dep 可用${NC}"
    else
        echo -e "${YELLOW}! $dep 不可用 (建议安装)${NC}"
    fi
done

# 9. 测试 Ansible Galaxy
echo -e "${CYAN}9. 测试 Ansible Galaxy...${NC}"
if ansible-galaxy --version &> /dev/null; then
    echo -e "${GREEN}✓ Ansible Galaxy 可用${NC}"
    
    # 测试 Galaxy 连接
    if ansible-galaxy search apache --max 1 &> /dev/null; then
        echo -e "${GREEN}✓ Ansible Galaxy 连接正常${NC}"
    else
        echo -e "${YELLOW}! Ansible Galaxy 连接可能有问题${NC}"
    fi
else
    echo -e "${RED}✗ Ansible Galaxy 不可用${NC}"
fi

# 生成报告
echo ""
echo -e "${GREEN}=== 安装验证完成 ===${NC}"
echo ""
echo -e "${CYAN}建议下一步:${NC}"
echo -e "${WHITE}1. 如果所有检查都通过，可以开始学习 Day 2${NC}"
echo -e "${WHITE}2. 如果有错误，请根据错误信息进行修复${NC}"
echo -e "${WHITE}3. 准备一些测试虚拟机来实践 Ansible${NC}"
echo -e "${WHITE}4. 考虑设置 Docker 测试环境 (见 configs/docker-compose.yml)${NC}"
echo ""

# 保存日志
LOG_FILE="ansible-test-$(date '+%Y%m%d-%H%M%S').log"
cat > "$LOG_FILE" << EOF
Ansible 安装验证报告
生成时间: $(date)
操作系统: $(uname -a)
Python 版本: $PYTHON_VERSION
Ansible 版本: $ANSIBLE_VERSION
配置文件: $(if [[ $FOUND_CONFIG == true ]]; then echo "找到"; else echo "未找到"; fi)
EOF

echo -e "${WHITE}测试日志已保存到: $LOG_FILE${NC}"

echo ""
echo -e "${GREEN}🎉 Ansible 环境检查完成！${NC}" 