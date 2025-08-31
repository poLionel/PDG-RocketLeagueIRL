using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

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

        public void ScoreGoal(string team)
        {
            // Send a request to score a goal
            var scoreGoalCommand = new GoalScoredCommand()
            {
                Team = team
            };
            clientCommandQueue.EnqueueCommand(scoreGoalCommand);
        }
    }
}