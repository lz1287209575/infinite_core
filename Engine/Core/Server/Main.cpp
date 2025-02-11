#include "Server.h"
#include <iostream>
#include <csignal>
#include <string>
#include <memory>

// 全局服务器实例
std::unique_ptr<Engine::GameServer> gServer;

// 信号处理函数
void SignalHandler(int signal) {
    std::cout << "Received signal: " << signal << std::endl;
    if (gServer) {
        gServer->Shutdown();
    }
}

// 注册所有信号处理
void RegisterSignalHandlers() {
    signal(SIGINT, SignalHandler);   // Ctrl+C
    signal(SIGTERM, SignalHandler);  // 终止信号
#ifdef _WIN32
    signal(SIGBREAK, SignalHandler); // Ctrl+Break
#else
    signal(SIGHUP, SignalHandler);   // 终端关闭
#endif
}

int main(int argc, char* argv[]) {
    try {
        // 注册信号处理器
        RegisterSignalHandlers();

        // 解析命令行参数，确定服务器类型
        Engine::ServerProcessType serverType = Engine::ServerProcessType::Master;
        if (argc > 1) {
            std::string type = argv[1];
            if (type == "world") serverType = Engine::ServerProcessType::World;
            else if (type == "gate") serverType = Engine::ServerProcessType::Gate;
            else if (type == "db") serverType = Engine::ServerProcessType::DB;
            else if (type == "login") serverType = Engine::ServerProcessType::Login;
            else if (type == "game") serverType = Engine::ServerProcessType::Game;
        }

        // 创建服务器实例
        gServer = std::make_unique<Engine::GameServer>(serverType);

        // 初始化服务器
        if (!gServer->Initialize()) {
            std::cerr << "Failed to initialize server" << std::endl;
            return 1;
        }

        // 运行服务器主循环
        gServer->Run();

        return 0;
    }
    catch (const std::exception& e) {
        std::cerr << "Fatal error: " << e.what() << std::endl;
        return 1;
    }
} 