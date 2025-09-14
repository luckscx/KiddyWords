#!/bin/bash

# 汉字奇趣岛 - 部署启动脚本
# 使用 uv 虚拟环境管理依赖，启动常驻后台Web服务

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="syword"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"
PID_FILE="$PROJECT_DIR/syword.pid"
LOG_FILE="$PROJECT_DIR/syword.log"
PORT=8083
HOST="0.0.0.0"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_debug() {
    echo -e "${BLUE}[DEBUG]${NC} $1"
}

# 检查uv是否安装
check_uv() {
    if ! command -v uv &> /dev/null; then
        log_error "uv 未安装，请先安装 uv:"
        echo "curl -LsSf https://astral.sh/uv/install.sh | sh"
        exit 1
    fi
    log_info "uv 已安装: $(uv --version)"
}

# 创建虚拟环境
create_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        log_info "创建虚拟环境..."
        uv venv
        log_info "虚拟环境创建完成"
    else
        log_info "虚拟环境已存在"
    fi
}

# 安装依赖
install_dependencies() {
    log_info "安装项目依赖..."
    uv pip install -r requirements.txt
    log_info "依赖安装完成"
}

# 检查服务是否运行
is_running() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0
        else
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# 启动服务
start_service() {
    if is_running; then
        log_warn "服务已在运行中 (PID: $(cat $PID_FILE))"
        return 0
    fi
    
    log_info "启动 $PROJECT_NAME 服务..."
    
    # 激活虚拟环境并启动应用
    export PORT=$PORT
    nohup uv run python app.py > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$PID_FILE"
    
    # 等待服务启动
    sleep 2
    
    if is_running; then
        log_info "服务启动成功!"
        log_info "PID: $pid"
        log_info "端口: $PORT"
        log_info "访问地址: http://$HOST:$PORT"
        log_info "日志文件: $LOG_FILE"
    else
        log_error "服务启动失败，请检查日志: $LOG_FILE"
        exit 1
    fi
}

# 停止服务
stop_service() {
    if ! is_running; then
        log_warn "服务未运行"
        return 0
    fi
    
    local pid=$(cat "$PID_FILE")
    log_info "停止服务 (PID: $pid)..."
    
    kill "$pid"
    rm -f "$PID_FILE"
    
    # 等待进程完全停止
    sleep 2
    
    if ! is_running; then
        log_info "服务已停止"
    else
        log_warn "服务可能仍在运行，尝试强制停止..."
        kill -9 "$pid" 2>/dev/null || true
        rm -f "$PID_FILE"
    fi
}

# 重启服务
restart_service() {
    log_info "重启服务..."
    stop_service
    sleep 1
    start_service
}

# 查看服务状态
status_service() {
    if is_running; then
        local pid=$(cat "$PID_FILE")
        log_info "服务正在运行 (PID: $pid)"
        log_info "端口: $PORT"
        log_info "访问地址: http://$HOST:$PORT"
        
        # 显示最近的日志
        if [ -f "$LOG_FILE" ]; then
            echo ""
            log_info "最近的日志:"
            tail -n 10 "$LOG_FILE"
        fi
    else
        log_warn "服务未运行"
    fi
}

# 查看日志
view_logs() {
    if [ -f "$LOG_FILE" ]; then
        log_info "显示日志 (按 Ctrl+C 退出):"
        tail -f "$LOG_FILE"
    else
        log_warn "日志文件不存在: $LOG_FILE"
    fi
}

# 显示帮助信息
show_help() {
    echo "汉字奇趣岛 - 部署管理脚本"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  status    查看服务状态"
    echo "  logs      查看实时日志"
    echo "  deploy    完整部署 (创建环境 + 安装依赖 + 启动服务)"
    echo "  help      显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 deploy    # 完整部署"
    echo "  $0 start     # 启动服务"
    echo "  $0 status    # 查看状态"
    echo "  $0 logs      # 查看日志"
}

# 完整部署
deploy() {
    log_info "开始完整部署..."
    check_uv
    create_venv
    install_dependencies
    start_service
    log_info "部署完成!"
}

# 主函数
main() {
    cd "$PROJECT_DIR"
    
    case "${1:-help}" in
        "start")
            check_uv
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            check_uv
            restart_service
            ;;
        "status")
            status_service
            ;;
        "logs")
            view_logs
            ;;
        "deploy")
            deploy
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            log_error "未知命令: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
