#pragma once
#include "Engine/Core/Server/Server.h"

namespace Game {

class MasterServer : public Engine::GameServer {
public:
    MasterServer() : GameServer(Engine::ServerProcessType::Master) {}
    ~MasterServer() = default;
};

} // namespace Game
