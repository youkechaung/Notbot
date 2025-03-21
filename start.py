import subprocess
import sys
import os
import time
import signal
import atexit

def kill_processes():
    """关闭所有相关进程"""
    print("正在关闭所有进程...")
    # 关闭 Python 进程
    for proc in processes:
        if proc.poll() is None:  # 如果进程还在运行
            try:
                proc.terminate()  # 尝试优雅地终止
                proc.wait(timeout=5)  # 等待最多5秒
            except:
                proc.kill()  # 如果还没终止，强制结束

# 存储所有启动的进程
processes = []

def main():
    # 注册退出时的清理函数
    atexit.register(kill_processes)
    
    # 获取当前脚本所在目录
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    try:
        # 启动 wx_easy.py
        print("正在启动 wx_easy.py...")
        # wx_process = subprocess.Popen([sys.executable, 'wx_easy.py'], 
        #                             cwd=base_dir)
        # processes.append(wx_process)
        
        # 等待一下确保 wx_easy.py 启动
        time.sleep(2)
        
        # 启动 app.py
        print("正在启动 web 服务...")
        app_process = subprocess.Popen([sys.executable, 'app.py'],
                                     cwd=base_dir)
        processes.append(app_process)
        
        print("\n所有服务已启动!")
        print("按 Ctrl+C 可以安全地关闭所有服务")
        
        # 等待任意子进程结束
        while True:
            # if wx_process.poll() is not None:
            #     print("WeChat 服务已停止运行")
            #     break
            if app_process.poll() is not None:
                print("Web 服务已停止运行")
                break
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n收到终止信号，正在关闭服务...")
    finally:
        kill_processes()

if __name__ == "__main__":
    main()
