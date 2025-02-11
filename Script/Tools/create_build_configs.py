#!/usr/bin/env python3
import os
from pathlib import Path

# 构建配置模板
BUILD_CONFIG_TEMPLATE = '''# {project_name} 构建配置
from pathlib import Path

# 项目配置
PROJECT = {{
    "name": "{project_name}",
    "type": "{project_type}",  # static_library, shared_library, executable
    "version": "1.0.0",
}}

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
DEPENDENCIES = {dependencies}

# 编译选项
COMPILE_OPTIONS = {{
    "msvc": ["/std:c++17", "/W4"],
    "gcc": ["-std=c++17", "-Wall", "-Wextra"],
    "clang": ["-std=c++17", "-Wall", "-Wextra"],
}}

# 链接选项
LINK_OPTIONS = {{
    "msvc": [],
    "gcc": ["-pthread"],
    "clang": ["-pthread"],
}}

# 预处理器定义
DEFINITIONS = [
    "{project_upper}_EXPORTS",
]

# 输出目录
OUTPUT_DIR = "../../bin"
'''

# 项目配置
PROJECTS = {
    "MasterServer": {
        "type": "executable",
        "dependencies": [
            "Engine.Core.Server",
            "Engine.Core.Network",
        ]
    },
    "WorldServer": {
        "type": "executable",
        "dependencies": [
            "Engine.Core.Server",
            "Engine.Core.Network",
            "Engine.GamePlay.Entity",
        ]
    },
    "GateServer": {
        "type": "executable",
        "dependencies": [
            "Engine.Core.Server",
            "Engine.Core.Network",
        ]
    },
    "DBServer": {
        "type": "executable",
        "dependencies": [
            "Engine.Core.Server",
            "Engine.Core.Database",
        ]
    },
    "LoginServer": {
        "type": "executable",
        "dependencies": [
            "Engine.Core.Server",
            "Engine.Core.Network",
            "Engine.Core.Database",
        ]
    },
    "GameServer": {
        "type": "executable",
        "dependencies": [
            "Engine.Core.Server",
            "Engine.Core.Network",
            "Engine.GamePlay.Entity",
            "Engine.GamePlay.Combat",
        ]
    },
    "GameLogic": {
        "type": "static_library",
        "dependencies": [
            "Engine.Core.Common",
            "Engine.GamePlay.Entity",
        ]
    }
}

def create_build_configs():
    project_root = Path(__file__).parent.parent.parent
    
    for project_name, config in PROJECTS.items():
        # 确定项目目录
        project_dir = project_root / "Project" / project_name
            
        # 创建项目目录
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建构建配置文件
        build_config = BUILD_CONFIG_TEMPLATE.format(
            project_name=project_name,
            project_type=config["type"],
            project_upper=project_name.upper(),
            dependencies=config["dependencies"]
        )
        
        # 使用新的命名格式：{ProjectName}.Build.py
        build_file = project_dir / f"{project_name}.Build.py"
        with open(build_file, 'w', encoding='utf-8') as f:
            f.write(build_config)
            
        print(f"Created build config: {build_file}")

if __name__ == "__main__":
    create_build_configs() 