#!/usr/bin/env python3
import os
from pathlib import Path

# 服务器类型定义
SERVER_TYPES = [
    "Master",
    "World",
    "Gate",
    "DB",
    "Login",
    "Game"
]

# 服务器头文件模板
HEADER_TEMPLATE = '''#pragma once
#include "Engine/Core/Server/Server.h"

namespace Game {{

class {server_type}Server : public Engine::GameServer {{
public:
    {server_type}Server() : GameServer(Engine::ServerProcessType::{server_type}) {{}}
    ~{server_type}Server() = default;
}};

}} // namespace Game
'''

# Main.cpp 模板
MAIN_TEMPLATE = '''#include <memory>
#include <csignal>
#include <iostream>
#include <string>

#include "MasterServer/MasterServer.h"
#include "WorldServer/WorldServer.h"
#include "GateServer/GateServer.h"
#include "DBServer/DBServer.h"
#include "LoginServer/LoginServer.h"
#include "GameServer/GameServer.h"

std::unique_ptr<Engine::GameServer> gServer;

void SignalHandler(int signal) {
    if (gServer) {
        gServer->Shutdown();
    }
}

void PrintUsage() {
    std::cout << "Usage: server [process_type]" << std::endl;
    std::cout << "Process types:" << std::endl;
    std::cout << "  master  - Master server process" << std::endl;
    std::cout << "  world   - World server process" << std::endl;
    std::cout << "  gate    - Gate server process" << std::endl;
    std::cout << "  db      - Database server process" << std::endl;
    std::cout << "  login   - Login server process" << std::endl;
    std::cout << "  game    - Game server process" << std::endl;
}

std::unique_ptr<Engine::GameServer> CreateServer(const std::string& type) {
    if (type == "master") return std::make_unique<Game::MasterServer>();
    if (type == "world") return std::make_unique<Game::WorldServer>();
    if (type == "gate") return std::make_unique<Game::GateServer>();
    if (type == "db") return std::make_unique<Game::DBServer>();
    if (type == "login") return std::make_unique<Game::LoginServer>();
    if (type == "game") return std::make_unique<Game::GameServer>();
    return std::make_unique<Game::MasterServer>(); // 默认为主服务器
}

int main(int argc, char* argv[]) {
    if (argc > 1 && (std::string(argv[1]) == "-h" || std::string(argv[1]) == "--help")) {
        PrintUsage();
        return 0;
    }

    // 注册信号处理
    signal(SIGINT, SignalHandler);
    signal(SIGTERM, SignalHandler);

    try {
        std::string serverType = argc > 1 ? argv[1] : "master";
        gServer = CreateServer(serverType);
        
        if (!gServer->Initialize()) {
            std::cerr << "Failed to initialize server" << std::endl;
            return 1;
        }

        gServer->Run();
        
        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    }
}
'''

def create_server_files():
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.parent
    servers_dir = project_root / "Project" / "Servers"

    # 创建服务器目录
    servers_dir.mkdir(parents=True, exist_ok=True)
    print(f"Created directory: {servers_dir}")

    # 创建各个服务器的目录和文件
    for server_type in SERVER_TYPES:
        # 创建服务器目录
        server_dir = servers_dir / f"{server_type}Server"
        server_dir.mkdir(exist_ok=True)
        print(f"Created directory: {server_dir}")

        # 创建头文件
        header_path = server_dir / f"{server_type}Server.h"
        with open(header_path, 'w', encoding='utf-8') as f:
            f.write(HEADER_TEMPLATE.format(server_type=server_type))
        print(f"Created file: {header_path}")

    # 创建主入口文件
    main_path = servers_dir / "Main.cpp"
    with open(main_path, 'w', encoding='utf-8') as f:
        f.write(MAIN_TEMPLATE)
    print(f"Created file: {main_path}")

if __name__ == "__main__":
    create_server_files()
    print("\nServer files creation completed!") 