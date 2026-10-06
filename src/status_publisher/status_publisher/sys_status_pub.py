import platform

import psutil
import rclpy
from rclpy.node import Node

from status_interfaces.msg import SystemStatus


class SysStatusPub(Node):

    def __init__(self, node_name):
        super().__init__(node_name)
        self.publisher_ = self.create_publisher(SystemStatus, 'sys_status', 10)
        # 每 1 秒采集并发布一次
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.get_logger().info('SysStatusPub 节点已启动，话题: /sys_status')

    def timer_callback(self):
        # 第一次调用 cpu_percent() 会返回无意义的值，这里由定时器自然跳过
        cpu_percent = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        net_io = psutil.net_io_counters()

        msg = SystemStatus()
        msg.stamp = self.get_clock().now().to_msg()
        msg.hostname = platform.node()
        msg.cpu_percent = float(cpu_percent)
        msg.memory_percent = float(memory_info.percent)
        # 统一换算为 MB
        msg.memory_total = float(memory_info.total / 1024 / 1024)
        msg.memory_available = float(memory_info.available / 1024 / 1024)
        msg.net_sent = float(net_io.bytes_sent / 1024 / 1024)
        msg.net_recv = float(net_io.bytes_recv / 1024 / 1024)

        self.get_logger().info(
            f'CPU {msg.cpu_percent:.1f}%  '
            f'MEM {msg.memory_percent:.1f}%  '
            f'NET ↑{msg.net_sent:.1f}MB ↓{msg.net_recv:.1f}MB'
        )
        self.publisher_.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = SysStatusPub('sys_status_pub')
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
