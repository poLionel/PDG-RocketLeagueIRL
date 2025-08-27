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
        public partial string? errorMessage { get; private set; }

        [RelayCommand]
        private async Task LoadNetworksAsync()
        {
            var response = await CrossWifiManager.Current.ScanWifiNetworks();
            errorMessage = response.ErrorMessage;
            WifiNetworks = new(response.Data ?? []);

        }

        [RelayCommand]
        private async Task ConnectToNetworkAsync(NetworkData network)
        {
            if (network.Ssid == null) return;
            var response = await CrossWifiManager.Current.ConnectWifi(network.Ssid, string.Empty);
            errorMessage = response.ErrorMessage;
        }
    }
}
