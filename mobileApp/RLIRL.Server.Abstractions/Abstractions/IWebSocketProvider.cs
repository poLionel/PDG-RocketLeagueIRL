using System.Net.WebSockets;

namespace RLIRL.Server.Abstractions.Abstractions
{
    public interface IWebSocketProvider
    {
        /// <summary>
        /// Retrieves a WebSocket client for the server
        /// </summary>
        /// <param name="cancellationToken">Cancellation token to cancel the operation</param>
        /// <exception cref="WebSocketException">Thrown if unable to connect to the WebSocket server</exception>
        /// <returns>A task that represents the asynchronous operation, containing the WebSocket client</returns>
        Task<ClientWebSocket> GetWebSocketClientAsync(CancellationToken cancellationToken);
    }
}