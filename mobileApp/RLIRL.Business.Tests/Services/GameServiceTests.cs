using RLIRL.Business.Abstractions.Models;
using RLIRL.Business.Services;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;
using RLIRL.Server.Abstractions.ServerResponses;
using Moq;
using Xunit;

namespace RLIRL.Business.Tests.Services
{
    public class GameServiceTests
    {
        private readonly Mock<IClientCommandQueue> _mockCommandQueue;
        private readonly GameService _service;

        public GameServiceTests()
        {
            _mockCommandQueue = new Mock<IClientCommandQueue>();
            _service = new GameService(_mockCommandQueue.Object);
        }

        [Fact]
        public void Constructor_SendsGetGameStatusCommand()
        {
            // Assert - Constructor should send initial refresh command
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<GetGameStatusCommand>()), 
                Times.Once);
        }

        [Fact]
        public void CurrentGameStatus_InitiallyNull()
        {
            // Assert
            Assert.Null(_service.CurrentGameStatus);
        }

        [Fact]
        public void UpdateGameStatus_WithNewStatus_UpdatesProperty()
        {
            // Arrange
            var gameStatus = new GameStatus
            {
                State = GameState.Active,
                StartDate = DateTime.UtcNow,
                RedTeamScore = 1,
                BlueTeamScore = 0,
                RedTeamCars = new[] { 1, 2 },
                BlueTeamCars = new[] { 3, 4 }
            };

            // Act
            _service.UpdateGameStatus(gameStatus);

            // Assert
            Assert.Same(gameStatus, _service.CurrentGameStatus);
        }

        [Fact]
        public void UpdateGameStatus_WithNewStatus_RaisesEvent()
        {
            // Arrange
            var gameStatus = new GameStatus
            {
                State = GameState.Paused,
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };
            GameStatus? eventArgs = null;
            _service.GameStatusChanged += (sender, args) => eventArgs = args;

            // Act
            _service.UpdateGameStatus(gameStatus);

            // Assert
            Assert.Same(gameStatus, eventArgs);
        }

        [Fact]
        public void UpdateGameStatus_WithSameStatus_DoesNotRaiseEvent()
        {
            // Arrange
            var gameStatus = new GameStatus
            {
                State = GameState.Ended,
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };
            _service.UpdateGameStatus(gameStatus);
            
            var eventRaised = false;
            _service.GameStatusChanged += (sender, args) => eventRaised = true;

            // Act
            _service.UpdateGameStatus(gameStatus);

            // Assert
            Assert.False(eventRaised);
        }

        [Fact]
        public void UpdateGameStatus_WithNull_UpdatesPropertyToNull()
        {
            // Arrange
            var gameStatus = new GameStatus 
            { 
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };
            _service.UpdateGameStatus(gameStatus); // Set to non-null first

            // Act
            _service.UpdateGameStatus(null);

            // Assert
            Assert.Null(_service.CurrentGameStatus);
        }

        [Fact]
        public void Refresh_EnqueuesGetGameStatusCommand()
        {
            // Act
            _service.Refresh();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<GetGameStatusCommand>()), 
                Times.AtLeast(2)); // Once in constructor, once in Refresh
        }

        [Fact]
        public void StartGame_EnqueuesStartGameCommand()
        {
            // Act
            _service.StartGame();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<StartGameCommand>()), 
                Times.Once);
        }

        [Fact]
        public void StopGame_EnqueuesStopGameCommand()
        {
            // Act
            _service.StopGame();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<StopGameCommand>()), 
                Times.Once);
        }

        [Fact]
        public void ResumeGame_EnqueuesResumeGameCommand()
        {
            // Act
            _service.ResumeGame();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<ResumeGameCommand>()), 
                Times.Once);
        }

        [Fact]
        public void EndGame_EnqueuesEndGameCommand()
        {
            // Act
            _service.EndGame();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<EndGameCommand>()), 
                Times.Once);
        }

        [Fact]
        public void ScoreGoal_WithRedTeam_EnqueuesGoalScoredCommand()
        {
            // Arrange
            var team = "red";

            // Act
            _service.ScoreGoal(team);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<GoalScoredCommand>(cmd => cmd.Team == team)), 
                Times.Once);
        }

        [Fact]
        public void ScoreGoal_WithBlueTeam_EnqueuesGoalScoredCommand()
        {
            // Arrange
            var team = "blue";

            // Act
            _service.ScoreGoal(team);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<GoalScoredCommand>(cmd => cmd.Team == team)), 
                Times.Once);
        }

        [Fact]
        public void ScoreGoal_WithEmptyTeam_EnqueuesGoalScoredCommand()
        {
            // Arrange
            var team = "";

            // Act
            _service.ScoreGoal(team);

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.Is<GoalScoredCommand>(cmd => cmd.Team == team)), 
                Times.Once);
        }

        [Fact]
        public void UndoGoal_EnqueuesUndoGoalCommand()
        {
            // Act
            _service.UndoGoal();

            // Assert
            _mockCommandQueue.Verify(
                x => x.EnqueueCommand(It.IsAny<UndoGoalCommand>()), 
                Times.Once);
        }

        [Fact]
        public void GameStatusChanged_EventHandlerSignature_IsCorrect()
        {
            // Arrange
            var handlerCalled = false;
            var gameStatus = new GameStatus 
            { 
                RedTeamCars = Array.Empty<int>(),
                BlueTeamCars = Array.Empty<int>()
            };
            
            EventHandler<GameStatus?>? handler = (sender, args) =>
            {
                Assert.Same(_service, sender);
                Assert.Same(gameStatus, args);
                handlerCalled = true;
            };

            _service.GameStatusChanged += handler;

            // Act
            _service.UpdateGameStatus(gameStatus);

            // Assert
            Assert.True(handlerCalled);
        }

        [Fact]
        public void MultipleCommandCalls_EnqueueMultipleCommands()
        {
            // Act
            _service.StartGame();
            _service.ScoreGoal("red");
            _service.ScoreGoal("blue");
            _service.UndoGoal();
            _service.EndGame();

            // Assert
            _mockCommandQueue.Verify(x => x.EnqueueCommand(It.IsAny<StartGameCommand>()), Times.Once);
            _mockCommandQueue.Verify(x => x.EnqueueCommand(It.Is<GoalScoredCommand>(cmd => cmd.Team == "red")), Times.Once);
            _mockCommandQueue.Verify(x => x.EnqueueCommand(It.Is<GoalScoredCommand>(cmd => cmd.Team == "blue")), Times.Once);
            _mockCommandQueue.Verify(x => x.EnqueueCommand(It.IsAny<UndoGoalCommand>()), Times.Once);
            _mockCommandQueue.Verify(x => x.EnqueueCommand(It.IsAny<EndGameCommand>()), Times.Once);
        }

        [Fact]
        public void UpdateGameStatus_WithDifferentGameStates_UpdatesCorrectly()
        {
            // Arrange & Act & Assert
            var states = new[] { GameState.NotStarted, GameState.Active, GameState.Paused, GameState.Ended };
            
            foreach (var state in states)
            {
                var gameStatus = new GameStatus 
                { 
                    State = state,
                    RedTeamCars = Array.Empty<int>(),
                    BlueTeamCars = Array.Empty<int>()
                };
                
                _service.UpdateGameStatus(gameStatus);
                Assert.Equal(state, _service.CurrentGameStatus?.State);
            }
        }
    }
}