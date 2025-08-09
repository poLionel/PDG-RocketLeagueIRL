using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.Server;
using System.Net.WebSockets;
using System.Text.Json;

namespace RLIRL.Server.Services.Server
{
    internal class ServerCommandSender(IWebSocketProvider webSocketProvider, IClientCommandQueue clientCommandQueue, ILogger<ServerCommandSender> logger) : IHostedService
    {
        private Task runningTask = Task.CompletedTask;

        private CancellationTokenSource? sharedTokenSource;

        public Task StartAsync(CancellationToken cancellationToken)
        {
            sharedTokenSource = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);

            // Start the command processing task if it is not already running
            if (runningTask.IsCompleted)
                runningTask = ProcessCommandsAsync(cancellationToken);

            return Task.CompletedTask;
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            sharedTokenSource?.Cancel();
            return runningTask;
        }

        private async Task ProcessCommandsAsync(CancellationToken cancellationToken)
        {
            // Fetch the WebSocket client and start sending commands
            using var webSocketClient = await webSocketProvider.GetWebSocketClientAsync(cancellationToken);

            while (!cancellationToken.IsCancellationRequested)
            {
                // Fetch the next command from the queue or exit if none are available
                var item = clientCommandQueue.DequeueCommand();
                if (item == null) continue;

                // Prepare the JSON payload
                var jsonPayload = JsonSerializer.Serialize(item);
                var data = System.Text.Encoding.UTF8.GetBytes(jsonPayload);

                try
                {
                    // Send the command to the WebSocket server
                    await webSocketClient.SendAsync(data, WebSocketMessageType.Text, true, cancellationToken);
                }
                catch(Exception ex)
                {
                    logger.LogError(ex, "Failed to send command to WebSocket server");
                }
            }
        }
    }
}
