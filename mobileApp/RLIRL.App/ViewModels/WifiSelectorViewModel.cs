using AutoMapper;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using MauiWifiManager;
using MauiWifiManager.Abstractions;
using RLIRL.App.Models;
using System.Collections.ObjectModel;

namespace RLIRL.App.ViewModels
{
    public partial class WifiSelectorViewModel(IMapper mapper) : ObservableObject
    {
        [ObservableProperty]
        public partial ObservableCollection<NetworkListItem> WifiNetworks { get; private set; }

        [ObservableProperty]
        public partial string? ErrorMessage { get; private set; }

        [RelayCommand]
        private async Task LoadNetworksAsync()
        {
            // Scan for wifi networks
            var response = await CrossWifiManager.Current.ScanWifiNetworks();
            ErrorMessage = response.ErrorCode == WifiErrorCodes.Success ? null : response.ErrorMessage;

            // Map the results to the UI model
            WifiNetworks = mapper.Map<ObservableCollection<NetworkListItem>>(response.Data ?? []);
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
