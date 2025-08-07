using RLIRL.Services.Abstractions.Server;

namespace RLIRL.Services.Services.Server
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
