import os
import platform
import subprocess
import argparse
from pathlib import Path
from third_party_config import THIRD_PARTY_LIBS, ENABLED_LIBS, SUBMODULES
from typing import Optional

class BuildSystem:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.compiler = self.detect_compiler()
        self.build_dir = self.project_root / "build"
        self.bin_dir = self.build_dir / "bin"
        self.obj_dir = self.build_dir / "obj"
        self.system = platform.system().lower()
        self.third_party_dir = self.project_root / "Engine" / "ThirdParty"

    def detect_compiler(self):
        system = platform.system()
        if system == "Windows":
            return "msvc"
        else:
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

    def get_compile_command(self, source_file, output_file):
        include_flags, _, _ = self.get_third_party_flags()
        include_flags_str = " ".join(include_flags)
        
        if self.compiler == "msvc":
            return f"cl /nologo /EHsc /W4 /std:c++17 {include_flags_str} /c {source_file} /Fo{output_file}"
        else:
            return f"g++ -c -std=c++17 -Wall -Wextra {include_flags_str} {source_file} -o {output_file}"

    def get_link_command(self, obj_files, output_file):
        _, lib_dir_flags, lib_flags = self.get_third_party_flags()
        lib_dir_flags_str = " ".join(lib_dir_flags)
        lib_flags_str = " ".join(lib_flags)
        obj_files_str = " ".join(str(f) for f in obj_files)
        
        if self.compiler == "msvc":
            return f"link /nologo {obj_files_str} {lib_dir_flags_str} {lib_flags_str} /out:{output_file}"
        else:
            return f"g++ {obj_files_str} {lib_dir_flags_str} {lib_flags_str} -o {output_file}"

    def prepare_directories(self):
        self.build_dir.mkdir(exist_ok=True)
        self.bin_dir.mkdir(exist_ok=True)
        self.obj_dir.mkdir(exist_ok=True)

    def build(self, target=None):
        self.prepare_directories()
        
        # 编译Engine
        engine_sources = self.collect_sources("Engine")
        engine_objects = self.compile_sources(engine_sources)

        # 编译Project
        project_sources = self.collect_sources("Project")
        project_objects = self.compile_sources(project_sources)

        # 链接最终可执行文件
        all_objects = engine_objects + project_objects
        self._link_executable(all_objects)

    def collect_sources(self, directory):
        sources = []
        for root, _, files in os.walk(self.project_root / directory):
            for file in files:
                if file.endswith(('.cpp', '.cc', '.cxx')):
                    sources.append(Path(root) / file)
        return sources

    def compile_sources(self, sources):
        obj_files = []
        for source in sources:
            rel_path = source.relative_to(self.project_root)
            obj_file = self.obj_dir / f"{rel_path.stem}.obj"
            obj_file.parent.mkdir(parents=True, exist_ok=True)
            
            cmd = self.get_compile_command(source, obj_file)
            print(f"Compiling: {source}")
            subprocess.run(cmd, shell=True, check=True)
            obj_files.append(obj_file)
        return obj_files

    def _link_executable(self, obj_files):
        executable = self.bin_dir / "GameServer"
        if platform.system() == "Windows":
            executable = executable.with_suffix(".exe")
        
        cmd = self.get_link_command(obj_files, executable)
        print(f"Linking: {executable}")
        subprocess.run(cmd, shell=True, check=True)

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
    builder.build(args.target)

if __name__ == "__main__":
    main() 