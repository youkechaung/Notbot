import os
import psutil

def find_python_processes():
    """查找运行中的 wx_easy.py 和 app.py 进程"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    wx_easy_path = os.path.join(base_dir, 'wx_easy.py')
    app_path = os.path.join(base_dir, 'app.py')
    
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info['cmdline']
            if cmdline and len(cmdline) > 1:
                if wx_easy_path in cmdline or app_path in cmdline:
                    processes.append(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return processes

def main():
    print("正在停止所有服务...")
    
    # 关闭 Python 进程
    processes = find_python_processes()
    for proc in processes:
        try:
            print(f"正在停止进程: {proc.pid}")
            proc.terminate()
            proc.wait(timeout=5)
        except:
            proc.kill()
    
    print("所有服务已停止!")

if __name__ == "__main__":
    main()
