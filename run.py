#!/usr/bin/env python3
"""
汉字奇趣岛 - 看图认字游戏启动脚本
"""

import os
import sys
import subprocess

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import flask
        print("✅ Flask 已安装")
        return True
    except ImportError:
        print("❌ Flask 未安装，正在安装...")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError:
            print("❌ 依赖安装失败")
            return False

def main():
    """主函数"""
    print("🎮 汉字奇趣岛 - 看图认字游戏")
    print("=" * 40)
    
    # 检查依赖
    if not check_dependencies():
        print("请手动安装依赖: pip install -r requirements.txt")
        return
    
    # 启动Flask应用
    print("🚀 启动游戏服务器...")
    print("📱 游戏地址: http://localhost:8080")
    print("🛑 按 Ctrl+C 停止服务器")
    print("=" * 40)
    
    try:
        from app import app
        app.run(debug=True, host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        print("\n👋 游戏服务器已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

if __name__ == '__main__':
    main()
