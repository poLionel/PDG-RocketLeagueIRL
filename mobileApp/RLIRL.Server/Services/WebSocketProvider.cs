using Microsoft.Extensions.Options;
using RLIRL.Server.Abstractions.Abstractions;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Net.WebSockets;

namespace RLIRL.Server.Services
{
    internal class WebSocketProvider(IOptions<ServerConfiguration> serverConfiguration) : IWebSocketProvider, IDisposable
    {
        private ClientWebSocket? currentWebSocketClient;
        private readonly SemaphoreSlim webSocketClientSemaphore = new(1, 1);
        private bool disposed = false;

        public async Task<ClientWebSocket> GetWebSocketClientAsync(CancellationToken cancellationToken)
        {
            await webSocketClientSemaphore.WaitAsync(cancellationToken);

            try
            {
                // Check if we have an open connection and return it if so
                if (currentWebSocketClient?.State == WebSocketState.Open)
                    return currentWebSocketClient;

                // Clean up any existing closed/failed connection
                if (currentWebSocketClient != null)
                {
                    currentWebSocketClient.Dispose();
                    currentWebSocketClient = null;
                }

                // Create a new connection
                var host = await GetHostAsync() ?? throw new WebSocketException("No valid host found for the server");
                using var handler = new SocketsHttpHandler();
                var ws = new ClientWebSocket();

                try
                {
                    await ws.ConnectAsync(host, new HttpMessageInvoker(handler), cancellationToken);
                    if (ws.State != WebSocketState.Open)
                        throw new WebSocketException("Failed to connect to the WebSocket server");

                    // Store the successful connection
                    currentWebSocketClient = ws;
                    return ws;
                }
                catch
                {
                    // Clean up failed connection attempt
                    ws.Dispose();
                    throw;
                }
            }
            finally
            {
                webSocketClientSemaphore.Release();
            }
        }

        private async Task<Uri?> GetHostAsync()
        {
            // If the server is not the network gateway, return the configured host
            if (!serverConfiguration.Value.IsHostGateway)
            {
                if (string.IsNullOrEmpty(serverConfiguration.Value.Host)) return null;
                var protocol = serverConfiguration.Value.Secure ? "wss" : "ws";
                return new Uri($"{protocol}://{serverConfiguration.Value.Host}:{serverConfiguration.Value.Port}");
            }

            // Look for the first available gateway address
            var gatewayAddresses = NetworkInterface.GetAllNetworkInterfaces()
                .Where(ni => ni.OperationalStatus == OperationalStatus.Up)
                .SelectMany(ni => ni.GetIPProperties().GatewayAddresses);

            // Try to connect to each gateway address and return the first one that is available
            foreach (var gateway in gatewayAddresses)
            {
                if (await IsServerAvailableAsync(gateway.Address, serverConfiguration.Value.Port))
                {
                    var protocol = serverConfiguration.Value.Secure ? "wss" : "ws";
                    return new Uri($"{protocol}://{gateway.Address}:{serverConfiguration.Value.Port}");
                }
            }

            // If no gateway is available, return null
            return null;
        }

        private async Task<bool> IsServerAvailableAsync(IPAddress ipAddress, short port)
        {
            try
            {
                // Attempt to connect to the server using TCP
                using var client = new TcpClient();
                await client.ConnectAsync(ipAddress, port);
                return true;
            }
            catch (SocketException)
            {
                return false;
            }
        }

        public void Dispose()
        {
            if (!disposed)
            {
                currentWebSocketClient?.Dispose();
                webSocketClientSemaphore?.Dispose();
                disposed = true;
            }
        }
    }
}