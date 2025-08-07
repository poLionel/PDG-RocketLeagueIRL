using RLIRL.Services.Abstractions.Server;

namespace RLIRL.Services.Services.Server
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
