#pragma once
#include "Engine/Core/Server/Server.h"

namespace Game {

class WorldServer : public Engine::GameServer {
public:
    WorldServer() : GameServer(Engine::ServerProcessType::World) {}
    ~WorldServer() = default;
};

} // namespace Game
