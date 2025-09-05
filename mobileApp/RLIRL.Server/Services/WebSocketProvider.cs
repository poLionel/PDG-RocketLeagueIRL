using Microsoft.Extensions.Options;
using RLIRL.Server.Abstractions.Abstractions;
using System.Net.WebSockets;

namespace RLIRL.Server.Services
{
    internal class WebSocketProvider(IOptions<ServerConfiguration> serverConfiguration, IGatewayProvider gatewayProvider) : IWebSocketProvider, IDisposable
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
                var host = GetHost() ?? throw new WebSocketException("No valid host found for the server");
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

        private Uri? GetHost()
        {
            var protocol = serverConfiguration.Value.Secure ? "wss" : "ws";

            // If the server is not the network gateway, return the configured host
            if (!serverConfiguration.Value.IsHostDefaultGateway)
            {
                if (string.IsNullOrEmpty(serverConfiguration.Value.Host)) return null;
                return new Uri($"{protocol}://{serverConfiguration.Value.Host}:{serverConfiguration.Value.Port}");
            }

            // Otherwise return the gateway address
            var gateway = gatewayProvider.GetGateway();
            if (gateway == null) return null;
            return new Uri($"{protocol}://{gateway}:{serverConfiguration.Value.Port}");
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