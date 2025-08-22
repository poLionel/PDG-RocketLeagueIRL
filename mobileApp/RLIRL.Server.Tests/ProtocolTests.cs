using System.Text.Json;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Services;
using RLIRL.Server.Services.ClientCommands;
using System.Net.WebSockets;

namespace RLIRL.Server.Tests
{
    public class ProtocolTests
    {
        private readonly ServerConfiguration serverConfiguration = new()
        {
            Host = "localhost",
            Port = 8000,
            Secure = false,
            IsHostGateway = false,
            MaxPacketSize = 1024 * 1024 // 1 MB
        };

        private readonly IServerCommandSerializer CommandSerializer = new ServerCommandSerializer();

        [Fact]
        public async Task TestMoveCarCommand()
        {
            // Prepare the command
            var command = new MoveCarCommand
            {
                Car = 1,
                Direction = Directions.Forward,
                Boost = true
            };
            var data = CommandSerializer.SerializeCommand(command);

            // Send the command
            using var wsClient = await GetWebSocketClientAsync();
            await wsClient.SendAsync(data, WebSocketMessageType.Text, true, CancellationToken.None);

            // Listen for the response
            var cancellationToken = new CancellationTokenSource(TimeSpan.FromSeconds(5)).Token;
            dynamic? response = await WaitForResponseAsync(wsClient, cancellationToken);

            // Check if the response is valid
            Assert.NotNull(response);
            Assert.Equal("success", (string)response!.status);
        }

        private async Task<object?> WaitForResponseAsync(ClientWebSocket wsClient, CancellationToken cancellationToken)
        {
            var buffer = new byte[serverConfiguration.MaxPacketSize];
            var result = await wsClient.ReceiveAsync(new ArraySegment<byte>(buffer), cancellationToken);
            var message = System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count);
            return JsonConvert.DeserializeObject(message);
        }

        public async Task<ClientWebSocket> GetWebSocketClientAsync()
        {
            SocketsHttpHandler handler = new();
            ClientWebSocket ws = new();

            var host = new Uri($"ws://{serverConfiguration.Host}:{serverConfiguration.Port}");
            await ws.ConnectAsync(host, new HttpMessageInvoker(handler), CancellationToken.None);
            if (ws.State != WebSocketState.Open)
                throw new InvalidOperationException("Failed to connect to the WebSocket server");

            return ws;
        }
    }
}
