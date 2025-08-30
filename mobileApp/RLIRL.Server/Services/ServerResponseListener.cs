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
    internal class ServerResponseListener(
        IWebSocketProvider webSocketProvider,
        IOptions<ServerConfiguration> serverConfiguration,
        IServiceProvider serviceProvider,
        ILogger<ServerResponseListener> logger) : IServerResponseListener
    {
        private const int CONNEXION_POOLING_DELAY_MS = 1000;

        private Task runningTask = Task.CompletedTask;

        private CancellationTokenSource? tokenSource;

        private readonly Lock serviceLock = new();

        private readonly IDictionary<string, Type> responseTypes = GetresponseTypes();

        public void Start()
        {
            lock (serviceLock)
            {
                // Start the response processing task if it is not already running
                if (runningTask.IsCompleted)
                {
                    tokenSource = new();
                    var token = tokenSource.Token;
                    runningTask = ProcessResponsesAsync(token);

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

        private async Task ProcessResponsesAsync(CancellationToken cancellationToken)
        {
            // Allocate the buffer for receiving messages
            var buffer = new byte[serverConfiguration.Value.MaxPacketSize];

            // Pool web socket clients to handle responses so if the web socket is closed, we can reconnect
            while (!cancellationToken.IsCancellationRequested)
            {
                try
                {
                    using var webSocket = await webSocketProvider.GetWebSocketClientAsync(cancellationToken);
                    await ProcessResponsesAsync(webSocket, buffer, cancellationToken);
                }
                catch
                {
                    // Before retrying, wait for a short period
                    await Task.Delay(CONNEXION_POOLING_DELAY_MS, cancellationToken);
                }
            }
        }

        private async Task ProcessResponsesAsync(ClientWebSocket webSocket, byte[] buffer, CancellationToken cancellationToken)
        {
            // Ensure the WebSocket is connected before processing responses
            while (webSocket.State == WebSocketState.Open)
            {
                try
                {
                    // Clear the buffer before receiving a new message
                    Array.Clear(buffer, 0, buffer.Length);

                    // Listen for incoming responses from the WebSocket server
                    var result = await webSocket.ReceiveAsync(new ArraySegment<byte>(buffer), cancellationToken);
                    if (result.MessageType == WebSocketMessageType.Close)
                    {
                        // Handle WebSocket close message
                        await webSocket.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", cancellationToken);
                        break;
                    }

                    // Retrieve the message and its response action
                    var message = System.Text.Encoding.UTF8.GetString(buffer, 0, result.Count);
                    var responseAction = JsonNode.Parse(message)?["action"]?.GetValue<string>();
                    if (string.IsNullOrEmpty(responseAction)) throw new InvalidOperationException("Received response with no action type");
                    if (!responseTypes.TryGetValue(responseAction, out var responseType))
                        throw new InvalidOperationException($"No response type found for action '{responseAction}'");

                    // Deserialize the response message into the appropriate response object
                    var response = JsonSerializer.Deserialize(message, responseType)
                        ?? throw new InvalidOperationException($"Failed to deserialize response of type '{responseType.Name}'");

                    // Get the response processor from the service provider
                    var responseHandlerType = typeof(IServerResponseProcessor<>).MakeGenericType(responseType);
                    var responseHandler = serviceProvider.GetService(responseHandlerType) as IServerResponseProcessor
                        ?? throw new InvalidOperationException($"No response handler found for response type '{responseType.Name}'");

                    // Process the response using the response handler
                    await responseHandler.ProcessResponseAsync(response);
                }
                catch (OperationCanceledException)
                {
                    break;
                }
                catch (Exception ex)
                {
                    // Log any exceptions that occur during response processing
                    logger.LogError(ex, "Error processing response");
                }
            }
        }

        private static IDictionary<string, Type> GetresponseTypes()
        {
            // Retrieve all types that implement the IServerResponse interface
            return AppDomain.CurrentDomain.GetAssemblies()
                .SelectMany(assembly => assembly.GetTypes())
                .Where(type =>
                    type.IsClass &&
                    !type.IsAbstract &&
                    type.GetInterface(nameof(IServerResponse)) != null &&
                    type.GetCustomAttribute<CommandNameAttribute>() != null
                )
                .ToDictionary(type => type.GetCustomAttribute<CommandNameAttribute>()!.Name, type => type);
        }
    }
}
