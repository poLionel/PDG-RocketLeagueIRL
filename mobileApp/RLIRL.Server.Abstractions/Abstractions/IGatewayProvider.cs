using System.Net;

namespace RLIRL.Server.Abstractions.Abstractions
{
    public interface IGatewayProvider
    {
        IPAddress? GetGateway();
    }
}
