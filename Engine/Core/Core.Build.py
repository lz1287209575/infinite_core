# Engine Core 构建配置
from pathlib import Path

# 项目配置
PROJECT = {
    "name": "Core",
    "type": "static_library",  # static_library, shared_library, executable
    "version": "1.0.0",
}

# 源文件目录
SOURCE_DIRS = [
    "Common",
    "Network",
    "Database",
    "Server",
]

# 包含目录
INCLUDE_DIRS = [
    "../../",  # 项目根目录
    "../../ThirdParty",  # 第三方库目录
]

# 依赖的库
DEPENDENCIES = []

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
    "ENGINE_CORE_EXPORTS",
] 