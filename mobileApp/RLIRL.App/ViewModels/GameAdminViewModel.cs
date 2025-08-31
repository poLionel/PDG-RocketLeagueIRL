using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.App.Models;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using System.Collections.ObjectModel;
using AutoMapper;
using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.App.ViewModels
{
    public partial class GameAdminViewModel(IGameService gameService, IMapper mapper) : ObservableObject, IDisposable
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

        private Timer? _gameTimer;
        static DateTime? _gameTimerStartTime;

        public void Initialize()
        {
            RefreshGameStatus();
            RefreshCameraFeeds();
            RefreshCars();

            gameService.GameStatusChanged += OnGameStatusChanged;
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
        private void EndGame()
        {
            gameService.EndGame();
        }

        [RelayCommand]
        private void ScoreGoal(string team)
        {
            // TODO: Implement goal scoring logic for the specified team
        }

        [RelayCommand]
        private void UndoLastGoal()
        {
            // TODO: Implement undo last goal logic
        }

        [RelayCommand]
        private void RefreshCameraFeeds()
        {
            // TODO: Implement refresh camera feeds logic
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

                // Update the timer
                StartOrUpdateGameTimer();
            }
            else
            {
                // Game status is null, reset to default
                Game = new GameInfo();
                GameStatus = "Game Stopped";
                StopGameTimer();
            }
        }

        private void StartOrUpdateGameTimer()
        {
            // Do not start the timer if there is no start time
            var gameStartTime = Game.StartTime;
            if (gameStartTime == null) return;

            // If the timer is already running and the game start time hasn't changed, do nothing
            if (_gameTimer != null && gameStartTime.Equals(_gameTimerStartTime)) return;
            _gameTimerStartTime = gameStartTime;

            // Calculate the precise delay to the next second boundary
            var offset = DateTime.UtcNow.Millisecond - gameStartTime.Value.Millisecond;
            var initialDelay = TimeSpan.FromMilliseconds(1000 - (offset % 1000));

            // Update the timer immediately to avoid waiting for the first tick
            UpdateGameTimer();

            // Start timer with precise initial delay, then tick every second
            _gameTimer = new Timer(_ => UpdateGameTimer(), null, initialDelay, TimeSpan.FromSeconds(1));
        }

        private void UpdateGameTimer()
        {
            // Get the time left in the game or zero if the game is over
            var timeLeft = Game.StartTime?.AddSeconds(Game.MatchLengthSeconds) - DateTime.UtcNow;
            if(timeLeft <= TimeSpan.Zero)
                timeLeft = TimeSpan.Zero;
            
            Game.TimeLeft = $"{timeLeft:mm\\:ss}";
        }

        private void StopGameTimer()
        {
            _gameTimer?.Dispose();
            _gameTimer = null;
            _gameTimerStartTime = null;
        }

        public void Dispose()
        {
            gameService.GameStatusChanged -= OnGameStatusChanged;
            StopGameTimer();
        }
    }
}
