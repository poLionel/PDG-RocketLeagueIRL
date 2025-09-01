using RLIRL.Server.Abstractions.Abstractions;
using System.Net;
using System.Net.NetworkInformation;

namespace RLIRL.Server.Services
{
    internal class GatewayProvider : IGatewayProvider
    {
        public IPAddress? GetGateway()
        {
            // Look for the first available gateway address
            var gatewayAddresses = NetworkInterface.GetAllNetworkInterfaces()
                .Where(ni => ni.OperationalStatus == OperationalStatus.Up)
                .SelectMany(ni => ni.GetIPProperties().GatewayAddresses);

            return gatewayAddresses.FirstOrDefault()?.Address;
        }
    }
}
