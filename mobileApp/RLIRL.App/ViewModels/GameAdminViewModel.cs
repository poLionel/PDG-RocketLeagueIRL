using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using RLIRL.App.Models;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using System.Collections.ObjectModel;
using AutoMapper;

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
        private void StartGame()
        {
            gameService.StartGame();
        }

        [RelayCommand]
        private void PauseGame()
        {
            // TODO: Implement pause game logic
        }

        [RelayCommand]
        private void StopGame()
        {
            gameService.StopGame();
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
            if (e != null)
            {
                // Map the GameStatus to GameInfo
                var gameInfo = mapper.Map<GameInfo>(e);
                Game = gameInfo;

                // Update game status text
                GameStatus = DetermineGameStatusText(e);

                // Start or update timer if game is active
                UpdateGameTimer(e);
            }
            else
            {
                // Game status is null, reset to default
                Game = new GameInfo();
                GameStatus = "Game Stopped";
                StopGameTimer();
            }
        }

        private string DetermineGameStatusText(GameStatus gameStatus)
        {
            var now = DateTime.UtcNow;
            
            if (now < gameStatus.StartOn)
                return "Game Scheduled";
            else if (now >= gameStatus.StartOn && now < gameStatus.EndOn)
                return "Game In Progress";
            else
                return "Game Finished";
        }

        private void UpdateGameTimer(GameStatus gameStatus)
        {
            var now = DateTime.UtcNow;
            
            // Only start timer if game is in progress or scheduled to start soon
            if (now < gameStatus.EndOn)
            {
                StartGameTimer(gameStatus.StartOn, gameStatus.EndOn);
            }
            else
            {
                StopGameTimer();
            }
        }

        private void StartGameTimer(DateTime startTime, DateTime endTime)
        {
            // Stop existing timer if any
            StopGameTimer();

            // Start new timer that updates every second
            _gameTimer = new Timer((_) =>
            {
                var now = DateTime.UtcNow;
                
                if (now < startTime)
                {
                    // Game hasn't started yet - show countdown to start
                    var timeToStart = startTime - now;
                    Game.TimeLeft = $"-{timeToStart:mm\\:ss}";
                    Game.IsGameActive = false;
                }
                else if (now >= startTime && now < endTime)
                {
                    // Game is active - show time remaining
                    var timeLeft = endTime - now;
                    Game.TimeLeft = timeLeft.ToString(@"mm\:ss");
                    Game.IsGameActive = true;
                }
                else
                {
                    // Game has ended
                    Game.TimeLeft = "00:00";
                    Game.IsGameActive = false;
                    StopGameTimer();
                }
            }, null, TimeSpan.Zero, TimeSpan.FromSeconds(1));
        }

        private void StopGameTimer()
        {
            _gameTimer?.Dispose();
            _gameTimer = null;
        }

        public void Dispose()
        {
            gameService.GameStatusChanged -= OnGameStatusChanged;
            StopGameTimer();
        }
    }
}
