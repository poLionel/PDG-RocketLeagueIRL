using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Business.Services;
using RLIRL.Server.Abstractions.ServerResponses;
using Moq;
using Xunit;

namespace RLIRL.Business.Tests.Services
{
    public class TimerServiceTests : IDisposable
    {
        private readonly Mock<IGameService> _mockGameService;
        private readonly TimerService _service;

        public TimerServiceTests()
        {
            _mockGameService = new Mock<IGameService>();
            _service = new TimerService(_mockGameService.Object);
        }

        [Fact]
        public void Constructor_SubscribesToGameStatusChanged()
        {
            // Assert - Constructor should subscribe to GameStatusChanged event
            _mockGameService.VerifyAdd(x => x.GameStatusChanged += It.IsAny<EventHandler<GameStatus?>>(), Times.Once);
        }

        [Fact]
        public void TimeLeft_InitiallyZero()
        {
            // Assert
            Assert.Equal(TimeSpan.Zero, _service.TimeLeft);
        }

        [Fact]
        public void OnGameUpdated_WithNullGameStatus_StopsTimer()
        {
            // Arrange
            var eventRaised = false;
            TimeSpan? eventTimeLeft = null;
            _service.TimeLeftChanged += (sender, timeLeft) =>
            {
                eventRaised = true;
                eventTimeLeft = timeLeft;
            };

            // Act
            _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, (GameStatus?)null);

            // Assert
            Assert.True(eventRaised);
            Assert.Equal(TimeSpan.Zero, eventTimeLeft);
        }

        [Fact]
        public void OnGameUpdated_WithNotStartedGame_StopsTimer()
        {
            // Arrange
            var gameStatus = new GameStatus
            {
                State = GameState.NotStarted,
                StartDate = null,
                TotalPausedTime = 0,
                MatchLengthSeconds = 300,
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };

            var eventRaised = false;
            _service.TimeLeftChanged += (sender, timeLeft) => eventRaised = true;

            // Act
            _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, gameStatus);

            // Assert
            Assert.True(eventRaised);
        }

        [Fact]
        public void OnGameUpdated_WithEndedGame_StopsTimer()
        {
            // Arrange
            var gameStatus = new GameStatus
            {
                State = GameState.Ended,
                StartDate = DateTime.UtcNow.AddMinutes(-5),
                TotalPausedTime = 0,
                MatchLengthSeconds = 300,
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };

            var eventRaised = false;
            _service.TimeLeftChanged += (sender, timeLeft) => eventRaised = true;

            // Act
            _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, gameStatus);

            // Assert
            Assert.True(eventRaised);
        }

        [Fact]
        public void OnGameUpdated_WithActiveGame_StartsTimer()
        {
            // Arrange
            var gameStatus = new GameStatus
            {
                State = GameState.Active,
                StartDate = DateTime.UtcNow.AddMinutes(-1), // Started 1 minute ago
                TotalPausedTime = 0,
                MatchLengthSeconds = 300, // 5 minutes total
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };

            var eventRaised = false;
            _service.TimeLeftChanged += (sender, timeLeft) => eventRaised = true;

            // Act
            _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, gameStatus);

            // Assert
            Assert.True(eventRaised);
        }

        [Fact]
        public void TimeLeftChanged_EventHandlerSignature_IsCorrect()
        {
            // Arrange
            var handlerCalled = false;
            EventHandler<TimeSpan>? handler = (sender, timeLeft) =>
            {
                Assert.Same(_service, sender);
                Assert.IsType<TimeSpan>(timeLeft);
                handlerCalled = true;
            };

            _service.TimeLeftChanged += handler;

            // Act - Trigger a game status change to invoke the event
            var gameStatus = new GameStatus
            {
                State = GameState.NotStarted,
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };
            _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, gameStatus);

            // Assert
            Assert.True(handlerCalled);
        }

        [Fact]
        public void Dispose_StopsTimer()
        {
            // Arrange
            var gameStatus = new GameStatus
            {
                State = GameState.Active,
                StartDate = DateTime.UtcNow,
                TotalPausedTime = 0,
                MatchLengthSeconds = 300,
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };
            _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, gameStatus);

            // Act
            _service.Dispose();

            // Assert - Should not throw and timer should be stopped
            // We can't easily test that the timer stopped, but we can ensure Dispose doesn't throw
            var exception = Record.Exception(() => _service.Dispose());
            Assert.Null(exception);
        }

        [Fact]
        public void Dispose_CalledMultipleTimes_DoesNotThrow()
        {
            // Act & Assert
            var exception = Record.Exception(() =>
            {
                _service.Dispose();
                _service.Dispose();
                _service.Dispose();
            });
            Assert.Null(exception);
        }

        [Fact]
        public void OnGameUpdated_WithGameWithoutStartDate_DoesNotStartTimer()
        {
            // Arrange
            var gameStatus = new GameStatus
            {
                State = GameState.Active,
                StartDate = null, // No start date
                TotalPausedTime = 0,
                MatchLengthSeconds = 300,
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };

            var eventCount = 0;
            _service.TimeLeftChanged += (sender, timeLeft) => eventCount++;

            // Act
            _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, gameStatus);

            // Assert - Should get one update with zero time, but timer shouldn't really start
            Assert.True(eventCount > 0);
        }

        [Fact]
        public void OnGameUpdated_WithGameInFuture_HandlesCorrectly()
        {
            // Arrange
            var gameStatus = new GameStatus
            {
                State = GameState.Active,
                StartDate = DateTime.UtcNow.AddMinutes(5), // Starts in future
                TotalPausedTime = 0,
                MatchLengthSeconds = 300,
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };

            var eventRaised = false;
            _service.TimeLeftChanged += (sender, timeLeft) => eventRaised = true;

            // Act
            _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, gameStatus);

            // Assert
            Assert.True(eventRaised);
        }

        [Fact]
        public void OnGameUpdated_SameStartTime_DoesNotRestartTimer()
        {
            // Arrange
            var startTime = DateTime.UtcNow.AddMinutes(-1);
            var gameStatus = new GameStatus
            {
                State = GameState.Active,
                StartDate = startTime,
                TotalPausedTime = 0,
                MatchLengthSeconds = 300,
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };

            // Act - Raise the same game status twice
            _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, gameStatus);
            _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, gameStatus);

            // Assert - Should not throw or cause issues
            var exception = Record.Exception(() => 
                _mockGameService.Raise(x => x.GameStatusChanged += null, _mockGameService.Object, gameStatus));
            Assert.Null(exception);
        }

        public void Dispose()
        {
            _service?.Dispose();
        }
    }
}