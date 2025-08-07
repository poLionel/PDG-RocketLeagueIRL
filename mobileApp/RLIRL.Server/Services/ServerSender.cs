using RLIRL.Server.Abstractions.Server;

namespace RLIRL.Server.Services.Server
{
    internal class ServerSender : IServerSender
    {
        public void SendCommand(IServerCommand command)
        {
            throw new NotImplementedException();
        }

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
