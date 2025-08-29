using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Options;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Data;
using System.Net.WebSockets;
using System.Reflection;
using System.Text.Json;
using System.Text.Json.Nodes;

namespace RLIRL.Server.Services
{
    internal class ServerCommandListener(
        IWebSocketProvider webSocketProvider,
        IOptions<ServerConfiguration> serverConfiguration,
        IServiceProvider serviceProvider,
        ILogger<ServerCommandListener> logger) : IServerCommandListener
    {
        private Task runningTask = Task.CompletedTask;

        private CancellationTokenSource? tokenSource;

        private readonly Lock serviceLock = new();

        private readonly IDictionary<string, Type> commandTypes = GetCommandTypes();

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
            // Allocate the buffer for receiving messages
            var buffer = new byte[serverConfiguration.Value.MaxPacketSize];

            // Pool web socket clients to handle incoming commands so if one fails, it will retry with a new one
            while (!cancellationToken.IsCancellationRequested)
            {
                using var webSocket = await webSocketProvider.GetWebSocketClientAsync(cancellationToken);
                await ProcessCommandsAsync(webSocket, buffer, cancellationToken);
            }
        }

        private async Task ProcessCommandsAsync(ClientWebSocket webSocket, byte[] buffer, CancellationToken cancellationToken)
        {
            // Ensure the WebSocket is connected before processing commands
            while (webSocket.State == WebSocketState.Open)
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

                    // Retrieve the message and its command action
                    var message = System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count);
                    var commandAction = JsonNode.Parse(message)?["action"]?.GetValue<string>();
                    if (string.IsNullOrEmpty(commandAction)) throw new InvalidOperationException("Received command with no action type");
                    if (!commandTypes.TryGetValue(commandAction, out var commandType))
                        throw new InvalidOperationException($"No command type found for action '{commandAction}'");

                    // Deserialize the command message into the appropriate command object
                    var command = JsonSerializer.Deserialize(message, commandType)
                        ?? throw new InvalidOperationException($"Failed to deserialize command of type '{commandType.Name}'");

                    // Get the command processor from the service provider
                    var commandHandlerType = typeof(IServerCommandProcessor<>).MakeGenericType(commandType);
                    var commandHandler = serviceProvider.GetService(commandHandlerType) as IServerCommandProcessor
                        ?? throw new InvalidOperationException($"No command handler found for command type '{commandType.Name}'");

                    // Process the command using the command handler
                    await commandHandler.ProcessCommandAsync(command);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    // Log any exceptions that occur during command processing
                    logger.LogError(ex, "Error processing command");
                }
            }
        }

        private static IDictionary<string, Type> GetCommandTypes()
        {
            // Retrieve all types that implement the IClientCommand interface
            return AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(assembly => assembly.GetTypes())
                .Where(type =>
                    type.IsClass &&
                    !type.IsAbstract &&
                    type.GetInterface(nameof(IServerCommand)) != null &&
                    type.GetCustomAttribute<CommandNameAttribute>() != null
                )
                .ToDictionary(type => type.GetCustomAttribute<CommandNameAttribute>()!.Name, type => type);
        }
    }
}
