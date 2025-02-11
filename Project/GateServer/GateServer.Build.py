# GateServer 构建配置
from pathlib import Path

# 项目配置
PROJECT = {
    "name": "GateServer",
    "type": "executable",  # static_library, shared_library, executable
    "version": "1.0.0",
}

# 源文件目录
SOURCE_DIRS = [
    ".",  # 当前目录
]

# 包含目录
INCLUDE_DIRS = [
    "../../",  # 项目根目录
    "../../Engine",  # 引擎目录
]

# 依赖的库
DEPENDENCIES = ['Engine.Core.Server', 'Engine.Core.Network']

# 编译选项
COMPILE_OPTIONS = {
    "msvc": ["/std:c++17", "/W4"],
    "gcc": ["-std=c++17", "-Wall", "-Wextra"],
    "clang": ["-std=c++17", "-Wall", "-Wextra"],
}

# 链接选项
LINK_OPTIONS = {
    "msvc": [],
    "gcc": ["-pthread"],
    "clang": ["-pthread"],
}

# 预处理器定义
DEFINITIONS = [
    "GATESERVER_EXPORTS",
]

# 输出目录
OUTPUT_DIR = "../../bin"
