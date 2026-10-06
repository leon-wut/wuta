from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='status_publisher',
            executable='sys_status_pub',
            name='sys_status_pub',
            output='screen',
        ),
        Node(
            package='status_publisher',
            executable='sys_status_display_qt',
            name='sys_status_display',
            output='screen',
        ),
    ])
