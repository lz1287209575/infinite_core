#pragma once

#include <memory>
#include <string>

namespace Engine {

// 服务器进程类型
enum class ServerProcessType {
    Master,     // 主进程，负责管理其他进程
    World,      // 世界进程，负责游戏世界逻辑
    Gate,       // 网关进程，负责客户端连接
    DB,         // 数据库进程，负责数据持久化
    Login,      // 登录进程，负责账号验证
    Game        // 游戏进程，负责具体场景
};

class GameServer {
public:
    GameServer(ServerProcessType type = ServerProcessType::Master);
    ~GameServer();

    // 初始化服务器
    bool Initialize();
    // 运行服务器主循环
    void Run();
    // 关闭服务器
    void Shutdown();

    // 获取进程类型
    ServerProcessType GetProcessType() const { return processType; }
    // 获取进程ID
    uint32_t GetProcessId() const { return processId; }

private:
    class Impl;
    std::unique_ptr<Impl> impl;
    bool isRunning;
    ServerProcessType processType;
    uint32_t processId;
};

} // namespace Engine