#pragma once
#include "Engine/Core/Server/Server.h"

namespace Game {

class GateServer : public Engine::GameServer {
public:
    GateServer() : GameServer(Engine::ServerProcessType::Gate) {}
    ~GateServer() = default;
};

} // namespace Game
