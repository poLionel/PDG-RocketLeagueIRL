using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.Server;
using System.Net.WebSockets;
using System.Reflection;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace RLIRL.Server.Services.Server
{
    internal class ServerCommandSender(IWebSocketProvider webSocketProvider, IClientCommandQueue clientCommandQueue, ILogger<ServerCommandSender> logger) : IHostedService
    {
        private Task runningTask = Task.CompletedTask;

        private CancellationTokenSource? sharedTokenSource;

        private readonly Lock serviceLock = new();

        public Task StartAsync(CancellationToken cancellationToken)
        {
            lock(serviceLock)
            {
                // Start the command processing task if it is not already running
                if (runningTask.IsCompleted)
                {
                    sharedTokenSource = CancellationTokenSource.CreateLinkedTokenSource(cancellationToken);
                    runningTask = ProcessCommandsAsync(cancellationToken);
                }
            }

            return Task.CompletedTask;
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            lock (serviceLock)
            {
                sharedTokenSource?.Cancel();
                return runningTask;
            }
        }

        private async Task ProcessCommandsAsync(CancellationToken cancellationToken)
        {
            using var webSocket = await webSocketProvider.GetWebSocketClientAsync(cancellationToken);

            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    // Fetch the next command from the queue or exit if none are available
                    var item = clientCommandQueue.DequeueCommand();
                    if (item == null) continue;

                    // If the command has a CommandNameAttribute, use it as the action property
                    var action = item.GetType().GetCustomAttribute<CommandNameAttribute>()?.Name;
                    var jsonNode = JsonSerializer.SerializeToNode(item) as JsonObject;
                    if (jsonNode != null && action != null)
                    {
                        jsonNode["Action"] = action;
                    }

                    // Prepare the payload
                    var jsonPayload = jsonNode?.ToJsonString() ?? JsonSerializer.Serialize(item);
                    var data = System.Text.Encoding.UTF8.GetBytes(jsonPayload);

                    // Send the command to the WebSocket server
                    await webSocket.SendAsync(data, WebSocketMessageType.Text, true, cancellationToken);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    logger.LogError(ex, "Failed to send command to WebSocket server");
                }
            }
        }
    }
}
