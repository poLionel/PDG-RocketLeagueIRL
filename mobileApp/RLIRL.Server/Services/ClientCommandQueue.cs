using RLIRL.Server.Abstractions.Server;

namespace RLIRL.Server.Services.Server
{
    internal class ClientCommandQueue : IClientCommandQueue
    {
        public IClientCommand DequeueCommand()
        {
            throw new NotImplementedException();
        }

        public void EnqueueCommand(IClientCommand command)
        {
            throw new NotImplementedException();
        }
    }
}
