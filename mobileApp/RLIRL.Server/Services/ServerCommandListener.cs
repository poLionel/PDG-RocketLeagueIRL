using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;
using RLIRL.Server.Abstractions;
using System.Net.WebSockets;

namespace RLIRL.Server.Services.Server
{
    internal class ServerCommandListener(IWebSocketProvider webSocketProvider, IOptions<ServerConfiguration> serverConfiguration) : IHostedService
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
            using var webSocket = await webSocketProvider.GetWebSocketClientAsync(cancellationToken);

            // Allocate the buffer for receiving messages
            var buffer = new byte[serverConfiguration.Value.MaxPacketSize];

            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    // Clear the buffer before receiving a new message
                    Array.Clear(buffer, 0, buffer.Length);

                    // Listen for incoming commands from the WebSocket server
                    var result = await webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), cancellationToken);
                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        // Handle WebSocket close message
                        await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", cancellationToken);
                        break;
                    }

                    // Parse the received command
                    var message = System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    // Log any exceptions that occur during command processing
                    Console.WriteLine($"Error processing command: {ex.Message}");
                }
            }
        }
    }
}
