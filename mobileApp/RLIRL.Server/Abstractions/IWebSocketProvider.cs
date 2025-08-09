using System.Net.WebSockets;

namespace RLIRL.Server.Abstractions
{
    internal interface IWebSocketProvider
    {
        /// <summary>
        /// Retrieves a WebSocket client for the server
        /// </summary>
        /// <param name="cancellationToken">Cancellation token to cancel the operation</param>
        /// <returns>A task that represents the asynchronous operation, containing the WebSocket client</returns>
        Task<ClientWebSocket> GetWebSocketClientAsync(CancellationToken cancellationToken);
    }
}