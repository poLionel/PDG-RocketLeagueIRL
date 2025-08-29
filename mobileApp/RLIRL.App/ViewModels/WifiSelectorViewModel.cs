using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MauiWifiManager;
using MauiWifiManager.Abstractions;
using System.Collections.ObjectModel;

namespace RLIRL.App.ViewModels
{
    internal partial class WifiSelectorViewModel : ObservableObject
    {
        [ObservableProperty]
        public partial ObservableCollection<NetworkData> WifiNetworks { get; private set; }

        [ObservableProperty]
        public partial string? ErrorMessage { get; private set; }

        [RelayCommand]
        private async Task LoadNetworksAsync()
        {
            // Scan for wifi networks
            var response = await CrossWifiManager.Current.ScanWifiNetworks();
            ErrorMessage = response.ErrorCode == WifiErrorCodes.Success ? null : response.ErrorMessage;
            WifiNetworks = new(response.Data ?? []);
        }

        [RelayCommand]
        private async Task ConnectToNetworkAsync(NetworkData network)
        {
            // Try to connect to the selected network (assuming open network for simplicity)
            if (network.Ssid == null) return;
            var response = await CrossWifiManager.Current.ConnectWifi(network.Ssid, string.Empty);
            ErrorMessage = response.ErrorCode == WifiErrorCodes.Success ? null : response.ErrorMessage;
        }
    }
}
