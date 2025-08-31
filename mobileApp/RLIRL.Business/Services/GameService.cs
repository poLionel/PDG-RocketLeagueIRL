using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;
using RLIRL.Server.Abstractions.ServerCommands;
using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.Business.Services
{
    internal class GameService(IClientCommandQueue clientCommandQueue) : IGameService
    {
        public GameStatus? CurrentGameStatus { get; private set; }

        public event EventHandler<GameStatus?>? GameStatusChanged;

        public void UpdateGameStatus(GameStatus? status)
        {
            if (CurrentGameStatus != status)
            {
                CurrentGameStatus = status;
                GameStatusChanged?.Invoke(this, status);
            }
        }

        public void Refresh()
        {
            // Send a request to refresh the game status
            var refreshCommand = new GetGameStatusCommand();
            clientCommandQueue.EnqueueCommand(refreshCommand);

            // Send a test event to simulate receiving a response
            CurrentGameStatus = new GameStatus
            {
                RedTeamScore = 3,
                RedTeamCars = [1, 2, 3],
                BlueTeamScore = 2,
                BlueTeamCars = [4, 5, 6],
                TimeRemaining = 120,
                ElapsedTime = 180,
                State = GameState.Active,
                MatchLengthSeconds = 300,
                StartDate = DateTime.UtcNow.AddSeconds(-180),
                TotalPausedTime = 0,
            };
            GameStatusChanged?.Invoke(this, CurrentGameStatus);
        }

        public void StartGame()
        {
            // Send a request to start the game
            var startGameCommand = new StartGameCommand();
            clientCommandQueue.EnqueueCommand(startGameCommand);
        }

        public void StopGame()
        {
            // Send a request to stop the game
            var stopGameCommand = new StopGameCommand();
            clientCommandQueue.EnqueueCommand(stopGameCommand);
        }

        public void ResumeGame()
        {
            // Send a request to resume the game
            var resumeGameCommand = new ResumeGameCommand();
            clientCommandQueue.EnqueueCommand(resumeGameCommand);
        }

        public void EndGame()
        {
            // Send a request to end the game
            var endGameCommand = new EndGameCommand();
            clientCommandQueue.EnqueueCommand(endGameCommand);
        }
    }
}