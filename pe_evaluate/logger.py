"""
日志模块
提供同时输出到控制台和文件的日志功能
"""

import os
import sys
from datetime import datetime
from typing import Optional


class DualLogger:
    """双重日志记录器：同时输出到控制台和文件"""
    
    def __init__(self, log_dir: str = "results/logs", enable_console: bool = True):
        """
        初始化日志记录器
        
        Args:
            log_dir: 日志文件目录
            enable_console: 是否同时输出到控制台
        """
        self.enable_console = enable_console
        
        # 创建日志目录
        os.makedirs(log_dir, exist_ok=True)
        
        # 生成日志文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"execute_log_{timestamp}.log"
        self.log_path = os.path.join(log_dir, log_filename)
        
        # 打开日志文件
        self.log_file = open(self.log_path, 'w', encoding='utf-8')
        
        # 写入日志头
        self._write_header()
    
    def _write_header(self):
        """写入日志文件头部信息"""
        header = f"""{'='*60}
AI角色Prompt评测系统 - 执行日志
{'='*60}
开始时间: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
{'='*60}

"""
        self.log_file.write(header)
        self.log_file.flush()
    
    def print(self, *args, **kwargs):
        """
        打印并记录日志
        使用方式与内置print()完全相同
        """
        # 获取要打印的内容
        output = ' '.join(str(arg) for arg in args)
        
        # 处理 end 参数（默认换行）
        end = kwargs.get('end', '\n')
        
        # 输出到控制台
        if self.enable_console:
            print(*args, **kwargs)
        
        # 写入日志文件
        self.log_file.write(output + end)
        self.log_file.flush()  # 立即刷新到文件
    
    def separator(self, char: str = "=", length: int = 60):
        """打印分隔线"""
        self.print(char * length)
    
    def section(self, title: str, emoji: str = ""):
        """打印章节标题"""
        self.separator()
        if emoji:
            self.print(f"{emoji} {title}")
        else:
            self.print(title)
        self.separator()
    
    def close(self):
        """关闭日志文件"""
        if self.log_file and not self.log_file.closed:
            # 写入日志尾部
            footer = f"""
{'='*60}
结束时间: {datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")}
日志文件: {self.log_path}
{'='*60}
"""
            self.log_file.write(footer)
            self.log_file.close()
    
    def get_log_path(self) -> str:
        """获取日志文件路径"""
        return self.log_path
    
    def __enter__(self):
        """支持 with 语句"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """支持 with 语句"""
        self.close()
        return False


# 全局日志实例（可选）
_global_logger: Optional[DualLogger] = None


def init_logger(log_dir: str = "results/logs", enable_console: bool = True) -> DualLogger:
    """初始化全局日志记录器"""
    global _global_logger
    _global_logger = DualLogger(log_dir, enable_console)
    return _global_logger


def get_logger() -> Optional[DualLogger]:
    """获取全局日志记录器"""
    return _global_logger


def close_logger():
    """关闭全局日志记录器"""
    global _global_logger
    if _global_logger:
        _global_logger.close()
        _global_logger = None

