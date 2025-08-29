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

        [ObservableProperty]
        public partial bool Loading { get; private set; }

        [RelayCommand]
        private async Task LoadNetworksAsync()
        {
            try
            {
                Loading = true;

                // Get the scanned and current networks
                var scanNetworks = await LoadScanNetworkAsync();

                // Map the results to the UI model
                WifiNetworks = mapper.Map<ObservableCollection<NetworkListItem>>(scanNetworks);

                // Refresh the current network
                await RefreshCurrentNetworkAsync();
            }
            finally
            {
                Loading = false;
            }
        }

        [RelayCommand]
        private async Task ConnectToNetworkAsync(NetworkListItem network)
        {
            if (network.Connected) return;

            // Try to connect without a password first
            if (await TryConnectToNetworkInternalAsync(network.Ssid, null)) return;

            // Show a modal dialog to get the password
            while (true)
            {
                string result = await Shell.Current.DisplayPromptAsync("Password required", "A password is required to connect to this wifi");
                if (result == null) return; // User cancelled

                // Try to connect with the provided password (loops until success or cancel)
                if (await TryConnectToNetworkInternalAsync(network.Ssid, result)) break;
            }

            // Refresh the current network
            await RefreshCurrentNetworkAsync();
        }

        [RelayCommand]
        private async Task NavigateToSettingsAsync()
        {
            await CrossWifiManager.Current.OpenWifiSetting();
        }

        private async Task<IEnumerable<NetworkData>> LoadScanNetworkAsync()
        {
            // Scan for wifi networks
            var response = await CrossWifiManager.Current.ScanWifiNetworks();
            ErrorMessage = response.ErrorCode == WifiErrorCodes.Success ? null : response.ErrorMessage;

            // Filter and sort networks
            return response.Data?
                .Where(n => !string.IsNullOrEmpty(n.Ssid))
                .DistinctBy(n => n.Ssid)
                .OrderByDescending(n => n.SignalStrength is byte strength ? strength : 0)
                .ThenBy(n => n.Ssid)
                .ToList() ?? [];
        }

        private async Task RefreshCurrentNetworkAsync()
        {
            var response = await CrossWifiManager.Current.GetNetworkInfo();
            if (response.ErrorCode != WifiErrorCodes.Success) return;

            // Select the current network if available
            foreach (var networks in WifiNetworks)
            {
                if (networks.Ssid != response.Data?.Ssid) continue;
                networks.Connected = true;
                break;
            }
        }
        private async Task<bool> TryConnectToNetworkInternalAsync(string ssid, string? password)
        {
            try
            {
                var response = await CrossWifiManager.Current.ConnectWifi(ssid, password ?? string.Empty);
                return response.ErrorCode == WifiErrorCodes.Success;
            }
            catch (ArgumentException)
            {
                // Network requires a password
                return false;
            }
        }
    }
}
