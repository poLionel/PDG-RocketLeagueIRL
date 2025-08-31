using RLIRL.Server.Abstractions.Abstractions;
using System.Collections.Concurrent;

namespace RLIRL.Server.Services
{
    internal class ClientCommandQueue : IClientCommandQueue
    {
        private ConcurrentQueue<IClientCommand> commandQueue = new();

        public void EnqueueCommand(IClientCommand command)
        {
            commandQueue.Enqueue(command);
        }

        public IClientCommand? DequeueCommand()
        {
            return commandQueue.TryDequeue(out IClientCommand? command) ? command : null;
        }
    }
}
