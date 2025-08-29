using Microsoft.Extensions.Logging;
using RLIRL.Server.Abstractions.Abstractions;
using System.Net.WebSockets;

namespace RLIRL.Server.Services
{
    internal class ServerCommandSender(
        IWebSocketProvider webSocketProvider,
        IClientCommandQueue clientCommandQueue,
        IServerCommandSerializer commandSerializer,
        ILogger<ServerCommandSender> logger) : IServerCommandSender
    {
        private Task runningTask = Task.CompletedTask;

        private CancellationTokenSource? tokenSource;

        private readonly Lock serviceLock = new();

        private const int POOLING_DELAY_MS = 100;

        public void Start()
        {
            lock (serviceLock)
            {
                // Start the command processing task if it is not already running
                if (runningTask.IsCompleted)
                {
                    tokenSource = new();
                    var token = tokenSource.Token;
                    runningTask = ProcessCommandsAsync(token);
                }
            }
        }

        public void Stop()
        {
            lock (serviceLock)
            {
                tokenSource?.Cancel();
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
                    if (item == null)
                    {
                        // Wait for a short period before checking the queue again
                        await Task.Delay(POOLING_DELAY_MS, cancellationToken);
                        continue;
                    }

                    var data = commandSerializer.SerializeCommand(item);

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
