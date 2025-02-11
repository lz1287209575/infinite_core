import os
import platform
import subprocess
import argparse
from pathlib import Path
from third_party_config import THIRD_PARTY_LIBS, ENABLED_LIBS, SUBMODULES
from typing import Optional
import importlib.util
import sys

class BuildSystem:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.compiler = self.detect_compiler()
        self.build_dir = self.project_root / "Build"
        self.bin_dir = self.build_dir / "Binary"
        self.obj_dir = self.build_dir / "Object"
        self.lib_dir = self.build_dir / "Library"
        self.system = platform.system().lower()
        self.third_party_dir = self.project_root / "Engine" / "ThirdParty"
        self.built_projects = set()  # 记录已构建的项目

    def detect_compiler(self):
        if platform.system() == "Windows":
            # TODO: 检测是否安装了MSVC
            return "msvc"
        else:
            # TODO: 检测是否安装了GCC
            return "gcc"

    def get_third_party_flags(self):
        include_flags = []
        lib_dir_flags = []
        lib_flags = []

        for lib in ENABLED_LIBS:
            if lib in THIRD_PARTY_LIBS:
                config = THIRD_PARTY_LIBS[lib]
                base_path = self.project_root / config['submodule_path']
                platform_config = config[self.system]
                
                # 添加包含目录
                for inc_dir in platform_config['include_dirs']:
                    inc_path = base_path / inc_dir
                    if self.compiler == "msvc":
                        include_flags.append(f"/I{inc_path}")
                    else:
                        include_flags.append(f"-I{inc_path}")
                
                # 添加库目录
                for lib_dir in platform_config['lib_dirs']:
                    lib_path = base_path / lib_dir
                    if self.compiler == "msvc":
                        lib_dir_flags.append(f"/LIBPATH:{lib_path}")
                    else:
                        lib_dir_flags.append(f"-L{lib_path}")
                
                # 添加库
                for lib_name in platform_config['libs']:
                    if self.compiler == "msvc":
                        lib_flags.append(f"{lib_name}.lib")
                    else:
                        lib_flags.append(f"-l{lib_name}")

        return include_flags, lib_dir_flags, lib_flags

    def get_compile_command(self, source, obj_file, config):
        """生成编译命令"""
        cmd = []
        if self.compiler == "msvc":
            cmd = ["cl", "/c", "/nologo", "/EHsc"]
            cmd.extend(config.COMPILE_OPTIONS["msvc"])
            for inc in config.INCLUDE_DIRS:
                cmd.append(f"/I{self.project_root / inc}")
            for define in config.DEFINITIONS:
                cmd.append(f"/D{define}")
            cmd.extend([str(source), f"/Fo{obj_file}"])
        else:
            cmd = ["g++", "-c"]
            cmd.extend(config.COMPILE_OPTIONS["gcc"])
            for inc in config.INCLUDE_DIRS:
                cmd.append(f"-I{self.project_root / inc}")
            for define in config.DEFINITIONS:
                cmd.append(f"-D{define}")
            cmd.extend([str(source), "-o", str(obj_file)])
        return cmd

    def get_link_command(self, obj_files, output_file, config):
        """生成链接命令"""
        cmd = []
        if self.compiler == "msvc":
            cmd = ["link", "/nologo"]
            cmd.extend(config.LINK_OPTIONS["msvc"])
            cmd.extend([str(obj) for obj in obj_files])
            cmd.extend([f"/OUT:{output_file}"])
        else:
            cmd = ["g++"]
            cmd.extend(config.LINK_OPTIONS["gcc"])
            cmd.extend([str(obj) for obj in obj_files])
            cmd.extend(["-o", str(output_file)])
        return cmd

    def prepare_directories(self):
        """准备构建目录"""
        self.build_dir.mkdir(exist_ok=True)
        self.bin_dir.mkdir(exist_ok=True)
        self.obj_dir.mkdir(exist_ok=True)
        self.lib_dir.mkdir(exist_ok=True)

    def load_build_config(self, project_path):
        """加载项目构建配置"""
        try:
            # 使用新的命名格式：{ProjectName}.Build.py
            project_name = project_path.name
            config_path = project_path / f"{project_name}.Build.py"
            
            if not config_path.exists():
                print(f"Build config not found: {config_path}")
                return None
                
            spec = importlib.util.spec_from_file_location("build_config", config_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"Error loading build config {config_path}: {e}")
            return None

    def build_project(self, project_path):
        """构建单个项目"""
        if project_path in self.built_projects:
            return True

        # 加载项目配置
        config = self.load_build_config(project_path)
        if not config:
            return False

        # 首先构建依赖项
        for dep in config.DEPENDENCIES:
            dep_path = self.resolve_dependency_path(dep)
            if not self.build_project(dep_path):
                return False

        print(f"\nBuilding {config.PROJECT['name']}...")

        # 收集源文件
        sources = []
        for src_dir in config.SOURCE_DIRS:
            src_path = project_path / src_dir
            sources.extend(self.collect_sources(src_path))

        # 编译源文件
        obj_files = []
        for source in sources:
            rel_path = source.relative_to(self.project_root)
            obj_file = self.obj_dir / f"{rel_path.stem}.obj"
            obj_file.parent.mkdir(parents=True, exist_ok=True)

            cmd = self.get_compile_command(source, obj_file, config)
            print(f"Compiling: {source}")
            try:
                subprocess.run(cmd, check=True)
                obj_files.append(obj_file)
            except subprocess.CalledProcessError as e:
                print(f"Compilation failed: {e}")
                return False

        # 链接
        if config.PROJECT["type"] == "executable":
            output_file = self.bin_dir / config.PROJECT["name"]
            if platform.system() == "Windows":
                output_file = output_file.with_suffix(".exe")
        else:
            output_file = self.lib_dir / f"{config.PROJECT['name']}.lib"

        cmd = self.get_link_command(obj_files, output_file, config)
        print(f"Linking: {output_file}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            print(f"Linking failed: {e}")
            return False

        self.built_projects.add(project_path)
        return True

    def resolve_dependency_path(self, dep):
        """解析依赖项路径"""
        parts = dep.split('.')
        if parts[0] == "Engine":
            return self.project_root / "Engine" / '/'.join(parts[1:])
        else:
            return self.project_root / "Project" / parts[-1]

    def collect_sources(self, directory):
        """收集源文件"""
        sources = []
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(('.cpp', '.cc', '.cxx')):
                    sources.append(Path(root) / file)
        return sources

    def build_all(self):
        """构建所有项目"""
        self.prepare_directories()
        
        # 构建Engine核心
        engine_core = self.project_root / "Engine/Core"
        if not self.build_project(engine_core):
            return False

        # 构建GamePlay模块
        gameplay = self.project_root / "Engine/GamePlay"
        if not self.build_project(gameplay):
            return False

        # 构建Project下的所有项目
        project_dir = self.project_root / "Project"
        for project_dir in project_dir.iterdir():
            if project_dir.is_dir() and (project_dir / f"{project_dir.name}.Build.py").exists():
                if not self.build_project(project_dir):
                    return False

        return True

    def init_submodules(self):
        """初始化所有git submodules"""
        print("初始化git submodules...")
        
        # 确保ThirdParty目录存在
        self.third_party_dir.mkdir(parents=True, exist_ok=True)

        # 初始化git submodules
        for lib_name, config in SUBMODULES.items():
            submodule_path = THIRD_PARTY_LIBS[lib_name]['submodule_path']
            if not (self.project_root / submodule_path).exists():
                print(f"添加submodule {lib_name}...")
                cmd = f"git submodule add -b {config['branch']} {config['url']} {submodule_path}"
                subprocess.run(cmd, shell=True, check=True)

        # 更新所有submodules
        subprocess.run("git submodule update --init --recursive", shell=True, check=True)

    def build_third_party(self, lib_name: Optional[str] = None):
        """构建指定的或所有第三方库"""
        libs_to_build = [lib_name] if lib_name else ENABLED_LIBS
        
        for lib in libs_to_build:
            if lib not in THIRD_PARTY_LIBS:
                print(f"警告: 未找到库 {lib} 的配置")
                continue

            config = THIRD_PARTY_LIBS[lib]
            build_script = config[self.system].get('build_script')
            if not build_script:
                continue

            lib_path = self.project_root / config['submodule_path']
            print(f"构建 {lib}...")
            
            # 切换到库目录并执行构建脚本
            current_dir = os.getcwd()
            os.chdir(lib_path)
            try:
                subprocess.run(build_script, shell=True, check=True)
            finally:
                os.chdir(current_dir)

    def validate_third_party_libs(self):
        """验证第三方库的路径和可用性"""
        for lib in ENABLED_LIBS:
            if lib not in THIRD_PARTY_LIBS:
                print(f"警告: 未找到库 {lib} 的配置")
                continue
                
            config = THIRD_PARTY_LIBS[lib]
            base_path = self.project_root / config['submodule_path']
            platform_config = config[self.system]
            
            # 检查库目录是否存在
            if not base_path.exists():
                print(f"警告: {lib} 目录不存在: {base_path}")
                continue

            # 检查包含目录
            for inc_dir in platform_config['include_dirs']:
                inc_path = base_path / inc_dir
                if not inc_path.exists():
                    print(f"警告: {lib} 的包含目录不存在: {inc_path}")
            
            # 检查库目录
            for lib_dir in platform_config['lib_dirs']:
                lib_path = base_path / lib_dir
                if not lib_path.exists():
                    print(f"警告: {lib} 的库目录不存在: {lib_path}")

def main():
    parser = argparse.ArgumentParser(description="Game Server Build System")
    parser.add_argument('--target', help='Build target (default: all)')
    parser.add_argument('--clean', action='store_true', help='Clean build files')
    parser.add_argument('--check-libs', action='store_true', help='Check third-party libraries')
    parser.add_argument('--init-submodules', action='store_true', help='Initialize git submodules')
    parser.add_argument('--build-libs', nargs='?', const='all', help='Build third-party libraries')
    args = parser.parse_args()

    builder = BuildSystem()
    
    if args.init_submodules:
        builder.init_submodules()
        return

    if args.build_libs:
        lib_to_build = None if args.build_libs == 'all' else args.build_libs
        builder.build_third_party(lib_to_build)
        return

    if args.check_libs:
        builder.validate_third_party_libs()
        return

    if args.clean:
        import shutil
        shutil.rmtree(builder.build_dir, ignore_errors=True)
        print("Build directory cleaned")
        return

    builder.validate_third_party_libs()  # 在构建前验证库
    if builder.build_all():
        print("\nBuild completed successfully!")
    else:
        print("\nBuild failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 