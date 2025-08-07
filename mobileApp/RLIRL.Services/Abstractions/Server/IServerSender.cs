using Microsoft.Extensions.Hosting;

namespace RLIRL.Services.Abstractions.Server
{
    /// <summary>
    /// Interface for sending commands to the server
    /// </summary>
    public interface IServerSender : IHostedService
    {
        /// <summary>
        /// Sends a command to the server
        /// </summary>
        /// <param name="command">Command to send</param>
        void SendCommand(IServerCommand command);
    }
}
