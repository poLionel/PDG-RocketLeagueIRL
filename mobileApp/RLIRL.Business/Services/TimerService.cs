using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.Business.Services
{
    public class TimerService : IDisposable, ITimerService
    {
        public TimeSpan TimeLeft { get; set; } = TimeSpan.Zero;

        public event EventHandler<TimeSpan>? TimeLeftChanged;

        // Timer state
        private IGameService _gameService;
        private Timer? _gameTimer;
        private static DateTime? _gameTimerStartTime;

        // State tracking
        private GameState _gameState = GameState.NotStarted;
        private DateTime? _gameStart;
        private int _gamePauseTime;
        private int _gameDuration;

        public TimerService(IGameService gameService)
        {
            _gameService = gameService;
            _gameService.GameStatusChanged += OnGameUpdated;
        }

        private void OnGameUpdated(object? sender, GameStatus? e)
        {
            // If we do not have data, stop the timer
            if (e == null)
            {
                StopGameTimer();
                return;
            }

            // Update the local variables
            _gameState = e.State;
            _gameStart = e.StartDate;
            _gamePauseTime = e.TotalPausedTime;
            _gameDuration = e.MatchLengthSeconds;

            // Either start, update or stop the timer depending on the state
            switch (_gameState)
            {
                case GameState.Active:
                case GameState.Paused:
                    StartOrUpdateGameTimer();
                    break;
                case GameState.NotStarted:
                case GameState.Ended:
                default:
                    StopGameTimer();
                    break;
            }
        }

        private void StartOrUpdateGameTimer()
        {
            // Update the timer immediately to avoid waiting for the first tick
            UpdateGameTimer();

            // Do not start the timer if there is no start time
            var gameStartTime = _gameStart;
            if (gameStartTime == null) return;

            // If the timer is already running and the game start time hasn't changed, do nothing
            if (_gameTimer != null && gameStartTime.Equals(_gameTimerStartTime)) return;
            _gameTimerStartTime = gameStartTime;

            // Calculate the precise delay to the next second boundary
            var offset = DateTime.UtcNow.Millisecond - gameStartTime.Value.Millisecond;
            var initialDelay = TimeSpan.FromMilliseconds(1000 - (offset % 1000));

            // Start timer with precise initial delay, then tick every second
            _gameTimer = new Timer(_ => UpdateGameTimer(), null, initialDelay, TimeSpan.FromSeconds(1));
        }

        private void UpdateGameTimer()
        {
            // Do not update when the game is paused
            if (_gameState == GameState.Paused) return;

            // Get the time left in the game or zero if the game is over
            var timeLeft = _gameStart?.AddSeconds(_gameDuration).AddSeconds(_gamePauseTime) - DateTime.UtcNow;
            if (timeLeft == null || timeLeft <= TimeSpan.Zero || _gameState == GameState.Ended)
                timeLeft = TimeSpan.Zero;

            TimeLeftChanged?.Invoke(this, timeLeft.Value);
        }

        private void StopGameTimer()
        {
            _gameTimer?.Dispose();
            _gameTimer = null;
            _gameTimerStartTime = null;

            TimeLeftChanged?.Invoke(this, TimeSpan.Zero);
        }

        public void Dispose()
        {
            StopGameTimer();
        }
    }
}
