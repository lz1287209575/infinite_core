#pragma once
#include "Engine/Core/Server/Server.h"

namespace Game {

class DBServer : public Engine::GameServer {
public:
    DBServer() : GameServer(Engine::ServerProcessType::DB) {}
    ~DBServer() = default;
};

} // namespace Game
