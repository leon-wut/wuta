"""tkinter 兜底版显示节点。

Qt / X server 在你的 WSL2 上跑不起来时的备胎。
用法与 Qt 版完全一致： ros2 run status_publisher sys_status_display_tk
"""
import platform
import sys
import tkinter as tk
from datetime import datetime

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node

from status_interfaces.msg import SystemStatus

FIELDS = [
    ('hostname', '主机名'),
    ('time', '记录时间'),
    ('cpu_percent', 'CPU 使用率'),
    ('memory_percent', '内存使用率'),
    ('memory_total', '内存总大小'),
    ('memory_available', '剩余内存'),
    ('net_sent', '网络已发送'),
    ('net_recv', '网络已接收'),
]


class StatusWindow(tk.Tk):

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.title('System Status Monitor')
        self.geometry('380x260')

        self.values = {}
        for row, (key, title) in enumerate(FIELDS):
            tk.Label(self, text=title + '：', anchor='w').grid(
                row=row, column=0, sticky='w', padx=10, pady=4)
            var = tk.StringVar(value='--')
            tk.Label(self, textvariable=var, anchor='w',
                     fg='#185FA5').grid(row=row, column=1, sticky='w', pady=4)
            self.values[key] = var

        node.create_subscription(
            SystemStatus, 'sys_status', self.msg_callback, 10)

        self.protocol('WM_DELETE_WINDOW', self.on_close)

    def msg_callback(self, msg):
        self.values['hostname'].set(msg.hostname)
        self.values['time'].set(
            datetime.now().strftime('%H:%M:%S.%f')[:-3])
        self.values['cpu_percent'].set(f'{msg.cpu_percent:.1f} %')
        self.values['memory_percent'].set(f'{msg.memory_percent:.1f} %')
        self.values['memory_total'].set(f'{msg.memory_total:.1f} MB')
        self.values['memory_available'].set(f'{msg.memory_available:.1f} MB')
        self.values['net_sent'].set(f'{msg.net_sent:.2f} MB')
        self.values['net_recv'].set(f'{msg.net_recv:.2f} MB')

    def on_close(self):
        self.destroy()


def main(args=None):
    rclpy.init(args=args)
    node = Node('sys_status_display_tk')

    window = StatusWindow(node)
    executor = SingleThreadedExecutor()
    executor.add_node(node)

    try:
        while True:
            if not window.winfo_exists():
                break
            executor.spin_once(timeout_sec=0.01)
            window.update()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()
    return 0


if __name__ == '__main__':
    sys.exit(main())
