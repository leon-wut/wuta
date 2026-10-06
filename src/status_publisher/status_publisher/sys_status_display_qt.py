import sys

import rclpy
from rclpy.executors import SingleThreadedExecutor
from rclpy.node import Node

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QWidget

from status_interfaces.msg import SystemStatus


class StatusWindow(QWidget):

    def __init__(self, node):
        super().__init__()
        self.node = node
        self.setWindowTitle('System Status Monitor')
        self.resize(360, 240)

        self.labels = {}
        grid = QGridLayout()
        row = 0
        for key, title in [
            ('hostname', '主机名'),
            ('time', '记录时间'),
            ('cpu_percent', 'CPU 使用率'),
            ('memory_percent', '内存使用率'),
            ('memory_total', '内存总大小'),
            ('memory_available', '剩余内存'),
            ('net_sent', '网络已发送'),
            ('net_recv', '网络已接收'),
        ]:
            name_label = QLabel(title + '：')
            value_label = QLabel('--')
            value_label.setStyleSheet('font-weight: bold;')
            grid.addWidget(name_label, row, 0)
            grid.addWidget(value_label, row, 1)
            self.labels[key] = value_label
            row += 1
        self.setLayout(grid)

        # 订阅话题
        self.sub = node.create_subscription(
            SystemStatus, 'sys_status', self.msg_callback, 10)

        # 用 Qt 的定时器驱动 ROS2 回调，避免阻塞 Qt 主循环
        self.ros_timer = QTimer(self)
        self.ros_timer.timeout.connect(self.spin_once)
        self.ros_timer.start(50)  # 20Hz

    def spin_once(self):
        self._executor.spin_once(timeout_sec=0)

    def bind_executor(self, executor):
        self._executor = executor

    def msg_callback(self, msg):
        secs, nsecs = msg.stamp.sec, msg.stamp.nanosec
        self.labels['hostname'].setText(msg.hostname)
        self.labels['time'].setText(f'{secs}.{nsecs // 1000000:03d} s')
        self.labels['cpu_percent'].setText(f'{msg.cpu_percent:.1f} %')
        self.labels['memory_percent'].setText(f'{msg.memory_percent:.1f} %')
        self.labels['memory_total'].setText(f'{msg.memory_total:.1f} MB')
        self.labels['memory_available'].setText(f'{msg.memory_available:.1f} MB')
        self.labels['net_sent'].setText(f'{msg.net_sent:.2f} MB')
        self.labels['net_recv'].setText(f'{msg.net_recv:.2f} MB')


def main(args=None):
    rclpy.init(args=args)
    node = Node('sys_status_display')

    app = QApplication(sys.argv)
    window = StatusWindow(node)

    executor = SingleThreadedExecutor()
    executor.add_node(node)
    window.bind_executor(executor)

    window.show()
    exit_code = app.exec_()

    node.destroy_node()
    rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
