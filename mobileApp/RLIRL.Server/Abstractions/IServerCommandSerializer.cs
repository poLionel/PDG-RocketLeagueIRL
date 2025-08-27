using RLIRL.Server.Abstractions.Server;

namespace RLIRL.Server.Abstractions
{
    internal interface IServerCommandSerializer
    {
        byte[] SerializeCommand(IClientCommand serverCommand);
    }
}