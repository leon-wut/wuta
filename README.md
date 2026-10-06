# WUTA 无人组 2026 招新笔试 — 系统状态监视器

基于 **Ubuntu 22.04 + ROS2 Humble** 实现，两个功能包：

| 包名 | 构建类型 | 职责 |
|---|---|---|
| `status_interfaces` | ament_cmake | 自定义消息接口 `SystemStatus.msg`（8 个字段） |
| `status_publisher` | ament_python | 采集系统状态并发布；提供 GUI 显示节点 |

## 一、系统架构

```
src/
├── status_interfaces/                    # 接口包 (ament_cmake)
│   ├── CMakeLists.txt                    # CMake 构建配置
│   ├── package.xml                       # 包清单 (rosidl_interface_packages)
│   ├── LICENSE
│   └── msg/
│       └── SystemStatus.msg              # 自定义消息定义 (8 个字段)
│
└── status_publisher/                     # Python 功能包 (ament_python)
    ├── package.xml                       # 依赖 rclpy + status_interfaces
    ├── setup.py                          # 注册入口点
    ├── setup.cfg
    ├── LICENSE
    ├── resource/
    │   └── status_publisher              # ament 索引标记文件
    ├── launch/
    │   └── status_monitor_launch.py      # 一键启动两个节点
    └── status_publisher/
        ├── __init__.py
        ├── sys_status_pub.py             # 采集并发布 /sys_status
        ├── sys_status_display_qt.py      # PyQt5 显示窗口（推荐）
        └── sys_status_display_tk.py      # tkinter 显示窗口（Qt 不可用时的兜底）
```

数据流：

```
[psutil / platform 采集] --> sys_status_pub --话题 /sys_status--> sys_status_display --> [GUI 窗口]
```

## 二、消息定义

```
builtin_interfaces/Time stamp
string hostname
float32 cpu_percent
float32 memory_percent
float32 memory_total
float32 memory_available
float32 net_sent
float32 net_recv
```

**单位约定**（写进 README 是工程习惯，别让评审猜）：

| 字段 | 单位 |
|---|---|
| `stamp` | ROS 时间戳（s + ns） |
| `cpu_percent` / `memory_percent` | 百分比 % |
| `memory_total` / `memory_available` | MB |
| `net_sent` / `net_recv` | MB（开机以来累计流量，非瞬时速率） |

## 三、依赖

```bash
# ROS2 环境（Ubuntu 22.04 + ROS2 Humble）
# https://docs.ros.org/en/humble/Installation.html

# Python 采集库
pip3 install psutil

# GUI 方案 A：PyQt5（题目建议）
sudo apt install -y python3-pyqt5

# GUI 方案 B：tkinter（Qt/X server 起不来时的兜底，Python 自带）
sudo apt install -y python3-tk
```

## 四、编译

```bash
# 仓库根目录执行（src/ 的上一级）
colcon build

# 或者只编某一个包
colcon build --packages-select status_interfaces
colcon build --packages-select status_publisher

# 每次开新终端都要 source
source install/setup.bash
```

> ⚠️ `status_publisher` 依赖 `status_interfaces`，必须先编好接口包。首次建议先 `--packages-select status_interfaces`。

## 五、运行

**方式一：三个终端分别启动**

```bash
# 终端 1 — 采集与发布
source install/setup.bash
ros2 run status_publisher sys_status_pub

# 终端 2 — GUI 显示（二选一）
source install/setup.bash
ros2 run status_publisher sys_status_display_qt      # Qt 版
ros2 run status_publisher sys_status_display_tk      # tkinter 版

# 终端 3 — 命令行验证
source install/setup.bash
ros2 topic echo /sys_status
```

**方式二：launch 一键启动**

```bash
source install/setup.bash
ros2 launch status_publisher status_monitor_launch.py
```

## 六、验证清单

```bash
# 1. 确认消息接口已生成
ros2 interface show status_interfaces/msg/SystemStatus

# 2. 确认话题有数据
ros2 topic list | grep sys_status
ros2 topic echo /sys_status

# 3. 确认发布频率
ros2 topic hz /sys_status

# 4. 看节点图
rqt_graph
```

预期输出示例：

```
hostname: 'DESKTOP-XXXX'
cpu_percent: 12.4
memory_percent: 45.8
memory_total: 16250.0
memory_available: 8803.2
net_sent: 124.55
net_recv: 1023.87
```

## 七、WSL2 上跑 GUI 的注意事项

WSL2 默认没有显示器，GUI 需要：

- **Win11**：内置 WSLg，通常开箱可用。先确认 `echo $DISPLAY` 有输出。
- **Win10**：装 [VcXsrv](https://sourceforge.net/projects/vcxsrv/)，启动时勾选 "Disable access control"，再在 Ubuntu 里执行：
  ```bash
  echo "export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}'):0" >> ~/.bashrc
  source ~/.bashrc
  ```

若 90 分钟内搞不定，直接切 tkinter 版本（`sys_status_display_tk.py`），功能等价，不影响评分。

## 八、已知限制

- `cpu_percent()` 第一次调用返回的是系统启动以来的平均值，第一条数据可能不准，从第二条开始正常。
- 网络流量是**累计值**，不是瞬时速率；如需速率可在接收端做差分。
- GUI 与 ROS2 回调的桥接：Qt 版用 `QTimer` 20Hz 触发 `spin_once`，tkinter 版在 `update()` 循环中触发，避免阻塞各自的事件循环。
