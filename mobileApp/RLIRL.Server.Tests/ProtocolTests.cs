using System.Text.Json;
using RLIRL.Server.Services;
using System.Net.WebSockets;
using Newtonsoft.Json;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

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
                Direction = Direction.Backward,
                Steering = 0,
                Boost = "true"
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

        [Fact]
        public async Task TestGetFreeCarsCommand()
        {
            // Prepare the command
            var command = new GetFreeCarsCommand();
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
            Assert.Equal("get_free_cars", (string)response!.action);
            Assert.NotNull(response!.free_cars);
        }

        [Fact]
        public async Task TestSelectCarCommand()
        {
            // Prepare the command
            var command = new SelectCarCommand
            {
                Car = 1
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
            Assert.Equal("select_car", (string)response!.action);
            Assert.Equal(1, (int)response!.car);
        }

        [Fact]
        public async Task TestFreeCarCommand()
        {
            // Prepare the command
            var command = new FreeCarCommand
            {
                Car = 1
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
            Assert.Equal("free_car", (string)response!.action);
            Assert.Equal(1, (int)response!.car);
        }

        [Fact]
        public async Task TestGetCarStatusCommand()
        {
            // Prepare the command
            var command = new GetCarStatusCommand
            {
                Car = 1
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
            Assert.Equal("get_car_status", (string)response!.action);
            Assert.Equal(1, (int)response!.car);
            Assert.NotNull(response!.battery_level);
            Assert.NotNull(response!.move);
            Assert.NotNull(response!.x);
            Assert.NotNull(response!.boost);
            Assert.NotNull(response!.boost_value);
        }

        [Fact]
        public async Task TestGetAccessibleCarFeedsCommand()
        {
            // Prepare the command
            var command = new GetAccessibleCarFeedsCommand();
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
            Assert.Equal("get_accessible_car_feeds", (string)response!.action);
            Assert.NotNull(response!.accessible_feeds);
        }

        [Fact]
        public async Task TestGetCarVideoFeedCommand()
        {
            // Prepare the command
            var command = new GetCarVideoFeedCommand
            {
                Car = 1
            };
            var data = CommandSerializer.SerializeCommand(command);

            // Send the command
            using var wsClient = await GetWebSocketClientAsync();
            await wsClient.SendAsync(data, WebSocketMessageType.Text, true, CancellationToken.None);

            // Listen for the response (this should return raw JPEG data, not JSON)
            var cancellationToken = new CancellationTokenSource(TimeSpan.FromSeconds(5)).Token;
            var buffer = new byte[serverConfiguration.MaxPacketSize];
            var result = await wsClient.ReceiveAsync(new ArraySegment<byte>(buffer), cancellationToken);
            
            // Check if we received some data (should be JPEG)
            Assert.True(result.Count > 0);
        }

        [Fact]
        public async Task TestGoalScoredCommand()
        {
            // Prepare the command
            var command = new GoalScoredCommand
            {
                Team = "red"
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
            Assert.Equal("goal_scored", (string)response!.action);
            Assert.NotNull(response!.message);
        }

        [Fact]
        public async Task TestGetGameStatusCommand()
        {
            // Prepare the command
            var command = new GetGameStatusCommand();
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
            Assert.Equal("get_game_status", (string)response!.action);
            Assert.NotNull(response!.game_status);
            Assert.NotNull(response!.game_status!.teams);
            Assert.NotNull(response!.game_status!.time_remaining);
        }

        [Fact]
        public async Task TestStartGameCommand()
        {
            // Prepare the command
            var command = new StartGameCommand();
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
            Assert.Equal("start_game", (string)response!.action);
            Assert.NotNull(response!.message);
        }

        [Fact]
        public async Task TestStopGameCommand()
        {
            // Prepare the command
            var command = new StopGameCommand();
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
            Assert.Equal("stop_game", (string)response!.action);
            Assert.NotNull(response!.message);
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
