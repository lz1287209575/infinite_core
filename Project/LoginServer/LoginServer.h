#pragma once
#include "Engine/Core/Server/Server.h"

namespace Game {

class LoginServer : public Engine::GameServer {
public:
    LoginServer() : GameServer(Engine::ServerProcessType::Login) {}
    ~LoginServer() = default;
};

} // namespace Game
