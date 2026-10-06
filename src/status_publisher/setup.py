from glob import glob
from setuptools import setup

PACKAGE_NAME = 'status_publisher'

setup(
    name=PACKAGE_NAME,
    version='0.0.1',
    packages=[PACKAGE_NAME],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + PACKAGE_NAME]),
        ('share/' + PACKAGE_NAME, ['package.xml']),
        ('share/' + PACKAGE_NAME + '/launch',
            glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='your_name',
    maintainer_email='you@example.com',
    description='系统状态采集与可视化显示',
    license='MIT',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'sys_status_pub = status_publisher.sys_status_pub:main',
            'sys_status_display_qt = status_publisher.sys_status_display_qt:main',
            'sys_status_display_tk = status_publisher.sys_status_display_tk:main',
        ],
    },
)
