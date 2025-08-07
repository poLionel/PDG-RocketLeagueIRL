using Microsoft.Extensions.Hosting;

namespace RLIRL.Server.Abstractions.Server
{
    /// <summary>
    /// Interface for listening to commands from the server
    /// </summary>
    public interface IServerListener : IHostedService
    {
    }
}
