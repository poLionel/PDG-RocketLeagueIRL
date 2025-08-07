using RLIRL.Server.Abstractions.Server;

namespace RLIRL.Server.Services.Server
{
    internal class ClientCommandQueue : IClientCommandQueue
    {
        public void EnqueueCommand(IClientCommand command)
        {
            throw new NotImplementedException();
        }

        public IClientCommand? DequeueCommand()
        {
            throw new NotImplementedException();
        }
    }
}
