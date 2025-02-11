#pragma once
#include "Engine/Core/Server/Server.h"

namespace Game {

class GameServer : public Engine::GameServer {
public:
    GameServer() : GameServer(Engine::ServerProcessType::Game) {}
    ~GameServer() = default;
};

} // namespace Game
