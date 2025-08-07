using RLIRL.Server.Abstractions.Server;

namespace RLIRL.Server.Services.Server
{
    internal class ServerListener : IServerListener
    {
        public Task StartAsync(CancellationToken cancellationToken)
        {
            throw new NotImplementedException();
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            throw new NotImplementedException();
        }
    }
}
