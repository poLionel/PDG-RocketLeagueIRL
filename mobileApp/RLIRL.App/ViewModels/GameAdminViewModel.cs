using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.App.Models;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using System.Collections.ObjectModel;

namespace RLIRL.App.ViewModels
{
    public partial class GameAdminViewModel(IGameService gameService) : ObservableObject, IDisposable
    {
        [ObservableProperty]
        public partial string GameStatus { get; set; } = "Game Stopped";

        [ObservableProperty]
        public partial GameInfo Game { get; set; } = new();

        [ObservableProperty]
        public partial ObservableCollection<PlayerCameraFeedInfo> PlayerCameraFeeds { get; set; } = new();

        [ObservableProperty]
        public partial ObservableCollection<CarInfo> Cars { get; set; } = new();

        [ObservableProperty]
        public partial bool IsLoading { get; set; }

        public async Task InitializeAsync()
        {
            await RefreshGameStatusAsync();
            await RefreshCameraFeedsAsync();
            await RefreshCarsAsync();

            gameService.GameStatusChanged += OnGameStatusChanged;
        }

        [RelayCommand]
        private async Task RefreshGameStatusAsync()
        {
            // TODO: Implement refresh game status logic
            await Task.CompletedTask;
        }

        [RelayCommand]
        private async Task StartGameAsync()
        {
            // TODO: Implement start game logic
            await Task.CompletedTask;
        }

        [RelayCommand]
        private async Task PauseGameAsync()
        {
            // TODO: Implement pause game logic
            await Task.CompletedTask;
        }

        [RelayCommand]
        private async Task StopGameAsync()
        {
            // TODO: Implement stop game logic
            await Task.CompletedTask;
        }

        [RelayCommand]
        private async Task ScoreGoalAsync(string team)
        {
            // TODO: Implement goal scoring logic for the specified team
            await Task.CompletedTask;
        }

        [RelayCommand]
        private async Task UndoLastGoalAsync()
        {
            // TODO: Implement undo last goal logic
            await Task.CompletedTask;
        }

        [RelayCommand]
        private async Task RefreshCameraFeedsAsync()
        {
            // TODO: Implement refresh camera feeds logic
            await Task.CompletedTask;
        }

        [RelayCommand]
        private async Task SelectPlayerCameraAsync(PlayerCameraFeedInfo cameraFeed)
        {
            // TODO: Implement select player camera logic
            await Task.CompletedTask;
        }

        [RelayCommand]
        private async Task RefreshCarsAsync()
        {
            // TODO: Implement refresh cars logic
            await Task.CompletedTask;
        }

        [RelayCommand]
        private async Task ToggleCarAssignmentAsync(CarInfo car)
        {
            // TODO: Implement toggle car assignment logic
            await Task.CompletedTask;
        }

        private void OnGameStatusChanged(object? sender, GameStatus? e)
        {

        }

        public void Dispose()
        {
            gameService.GameStatusChanged -= OnGameStatusChanged;
        }
    }
}
