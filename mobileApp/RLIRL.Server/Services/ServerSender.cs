using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Options;
using System.Net;
using System.Net.NetworkInformation;
using System.Net.Sockets;
using System.Net.WebSockets;

namespace RLIRL.Server.Services.Server
{
    internal class ServerSender(IOptions<ServerConfiguration> serverConfiguration) : IHostedService
    {
        public Task StartAsync(CancellationToken cancellationToken)
        {
            throw new NotImplementedException("ServerSender is not implemented yet. This is a placeholder for future functionality.");
        }

        public Task StopAsync(CancellationToken cancellationToken)
        {
            throw new NotImplementedException("ServerSender is not implemented yet. This is a placeholder for future functionality.");
        }

        private async Task<IPAddress?> GetServerIPAsync()
        {
            if (serverConfiguration.Value.IsHostGateway)
            {
                // Look for the first available gateway address
                var gatewayAddresses = NetworkInterface.GetAllNetworkInterfaces()
                    .Where(ni => ni.OperationalStatus == OperationalStatus.Up)
                    .SelectMany(ni => ni.GetIPProperties().GatewayAddresses);

                // Try to connect to each gateway address and return the first one that is available
                foreach (var gateway in gatewayAddresses)
                {
                    if (await IsServerAvailableAsync(gateway.Address, serverConfiguration.Value.Port))
                    {
                        return gateway.Address;
                    }
                }

                // If no gateway is available, return null
                return null;
            }
            else
            {
                // If not using gateway, return the configured host address
                if (string.IsNullOrEmpty(serverConfiguration.Value.Host)) return null;
                return IPAddress.Parse(serverConfiguration.Value.Host);
            }
        }

        private async Task<bool> IsServerAvailableAsync(IPAddress ipAddress, short port)
        {
            try
            {
                using var client = new TcpClient();
                await client.ConnectAsync(ipAddress, port);
                return true;
            }
            catch (SocketException)
            {
                return false;
            }
        }
    }
}
