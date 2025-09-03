using Android.Content;
using Android.Net;
using RLIRL.Server.Abstractions.Abstractions;
using System.Net;
using Application = Android.App.Application;

namespace RLIRL.App.Platforms.Android
{
    internal class AndroidGatewayProvider : IGatewayProvider
    {
        public IPAddress? GetGateway()
        {
            try
            {
                // Get the ConnectivityManager from the system service
                var context = Platform.CurrentActivity ?? Application.Context;
                var connectivityManager = (ConnectivityManager?)context.GetSystemService(Context.ConnectivityService);

                if (connectivityManager == null)
                    return null;

                var network = connectivityManager.ActiveNetwork;
                if (network == null)
                    return null;

                var linkProperties = connectivityManager.GetLinkProperties(network);
                if (linkProperties == null)
                    return null;

                // Get the first gateway address
                var gateway = linkProperties.Routes
                    .FirstOrDefault(r => r.Gateway != null && r.Destination.PrefixLength == 0)?.Gateway;

                var address = gateway?.GetAddress();
                if (address == null) return null;
                return new IPAddress(address);
            }
            catch
            {
                return null;
            }
        }
    }
}