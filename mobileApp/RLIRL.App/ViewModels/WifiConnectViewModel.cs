using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.Server.Abstractions.Abstractions;

namespace RLIRL.App.ViewModels
{
    public partial class WifiConnectViewModel(IServerConnectionStatusService serverConnectionStatusService) : ObservableObject
    {
        [ObservableProperty]
        public partial bool ServerConnected { get; private set; }

        [ObservableProperty]
        public partial bool ConnectionFailed { get; private set; }

        [RelayCommand]
        public async Task CheckServerConnectionAsync(bool silent)
        {
            // If not silent, reset the error message
            if (silent) return;
            ConnectionFailed = true;

            ServerConnected = await serverConnectionStatusService.IsServerConnectedAsync();

            // Redirect to menu page if the server is connected
            if (ServerConnected)
            {
                await Shell.Current.GoToAsync("//menu");
                return;
            }

            // If not silent, show an error message
            if (silent) return;
            ConnectionFailed = true;
        }
    }
}
