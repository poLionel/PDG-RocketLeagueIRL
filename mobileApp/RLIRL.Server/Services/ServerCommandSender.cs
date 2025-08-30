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
        private const int CONNEXION_POOLING_DELAY_MS = 1000;

        private Task runningTask = Task.CompletedTask;

        private CancellationTokenSource? tokenSource;

        private readonly Lock serviceLock = new();

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

                    // Log any unhandled exceptions from the task
                    runningTask.ContinueWith(t =>
                    {
                        if (t.Exception == null) return;
                        logger.LogError(t.Exception, "ServerCommandSender crashed");

                    }, TaskContinuationOptions.OnlyOnFaulted);
                }
            }
        }

        public void Stop()
        {
            lock (serviceLock)
            {
                tokenSource?.Cancel();
                tokenSource?.Dispose();
                tokenSource = null;
            }
        }

        private async Task ProcessCommandsAsync(CancellationToken cancellationToken)
        {
            // Pool web socket clients to handle commands so if the web socket is closed, we can reconnect
            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    using var webSocket = await webSocketProvider.GetWebSocketClientAsync(cancellationToken);
                    await ProcessCommandsAsync(webSocket, cancellationToken);
                }
                catch
                {
                    // Before retrying, wait for a short period
                    await Task.Delay(CONNEXION_POOLING_DELAY_MS, cancellationToken);
                }
            }
        }

        private async Task ProcessCommandsAsync(ClientWebSocket webSocket, CancellationToken cancellationToken)
        {
            // Ensure the WebSocket is connected before processing commands
            while (webSocket.State == WebSocketState.Open)
            {
                try
                {
                    // Wait for an item to be available in the queue
                    var item = await clientCommandQueue.DequeueCommandAsync(cancellationToken);

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
