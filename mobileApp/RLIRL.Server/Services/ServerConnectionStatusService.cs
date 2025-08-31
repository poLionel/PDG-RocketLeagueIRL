using RLIRL.Server.Abstractions.Abstractions;
using System.Net.WebSockets;

namespace RLIRL.Server.Services
{
    internal class ServerConnectionStatusService(IWebSocketProvider webSocketProvider) : IServerConnectionStatusService
    {
        public async Task<bool> IsServerConnectedAsync(CancellationToken cancellationToken = default)
        {
            try
            {
                using var _ = await webSocketProvider.GetWebSocketClientAsync(CancellationToken.None);
                return true;
            }
            catch (WebSocketException)
            {
                // Connection failed
                return false;
            }
        }
    }
}
