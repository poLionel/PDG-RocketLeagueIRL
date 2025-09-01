using AutoMapper;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.App.Models;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Business.Services;
using RLIRL.Server.Abstractions.ServerResponses;
using System.Collections.ObjectModel;

namespace RLIRL.App.ViewModels
{
    public partial class GameAdminViewModel(
        IGameService gameService,
        ICameraFeedService cameraFeedService,
        ITimerService timerService,
        IMapper mapper) : ObservableObject, IDisposable
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
        public partial string TimeLeft { get; set; } = "00:00";

        [ObservableProperty]
        public partial bool IsLoading { get; set; }

        [ObservableProperty]
        public partial bool CanStartGame { get; set; }

        [ObservableProperty]
        public partial bool CanStopGame { get; set; }

        [ObservableProperty]
        public partial bool CanEndGame { get; set; }

        [ObservableProperty]
        public partial bool CanScoreGoal { get; set; }

        [ObservableProperty]
        public partial bool CanResumeGame { get; set; }

        [ObservableProperty]
        public partial bool IsResumeShown { get; set; }

        public void Initialize()
        {
            gameService.GameStatusChanged += OnGameStatusChanged;
            cameraFeedService.CameraFeedsChanged += CameraFeedsChanged;
            timerService.TimeLeftChanged += TimeLeftChanged;

            RefreshCameraFeeds();
            RefreshCars();
        }

        [RelayCommand]
        private void RefreshGameStatus()
        {
            gameService.Refresh();
        }

        [RelayCommand]
        private void StartGame()
        {
            gameService.StartGame();
        }

        [RelayCommand]
        private void StopGame()
        {
            gameService.StopGame();
        }

        [RelayCommand]
        private void ResumeGame()
        {
            gameService.ResumeGame();
        }

        [RelayCommand]
        private void EndGame()
        {
            gameService.EndGame();
        }

        [RelayCommand]
        private void ScoreGoal(string team)
        {
            gameService.ScoreGoal(team);
        }

        [RelayCommand]
        private void UndoGoal()
        {
            gameService.UndoGoal();
        }

        [RelayCommand]
        private void UndoLastGoal()
        {
            // TODO: Implement undo last goal logic
        }

        [RelayCommand]
        private void RefreshCameraFeeds()
        {
            cameraFeedService.Refresh();
        }

        [RelayCommand]
        private void SelectPlayerCamera(PlayerCameraFeedInfo cameraFeed)
        {
            // TODO: Implement select player camera logic
        }

        [RelayCommand]
        private void RefreshCars()
        {
            // TODO: Implement refresh cars logic
        }

        [RelayCommand]
        private void ToggleCarAssignment(CarInfo car)
        {
            // TODO: Implement toggle car assignment logic
        }

        private void OnGameStatusChanged(object? sender, GameStatus? e)
        {
            if (e != null)
            {
                // Map the GameStatus to GameInfo
                Game = mapper.Map<GameInfo>(e);

                // Update the button states
                CanStartGame = e.State == GameState.Ended || e.State == GameState.NotStarted;
                CanStopGame = e.State == GameState.Active;
                CanEndGame = e.State == GameState.Active || e.State == GameState.Paused;
                CanScoreGoal = e.State == GameState.Active || e.State == GameState.Paused;
                CanResumeGame = e.State == GameState.Paused;
                IsResumeShown = e.State == GameState.Paused;
            }
            else
            {
                // Game status is null, reset to default
                Game = new GameInfo();
                GameStatus = "Game Stopped";
            }
        }

        private void CameraFeedsChanged(object? sender, IEnumerable<CameraFeed>? e)
        {
            // TODO: Handle null case if needed
        }

        private void TimeLeftChanged(object? sender, TimeSpan timeLeft)
        {
            TimeLeft = timeLeft.ToString(@"mm\:ss");
        }

        public void Dispose()
        {
            gameService.GameStatusChanged -= OnGameStatusChanged;
            cameraFeedService.CameraFeedsChanged -= CameraFeedsChanged;
            timerService.TimeLeftChanged -= TimeLeftChanged;
        }
    }
}
