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

        public void StartGame()
        {
            // If the game is running, do nothing
            if (IsGameCurrentlyActive()) return;

            // Send a request to start the game
            var startGameCommand = new StartGameCommand();
            clientCommandQueue.EnqueueCommand(startGameCommand);
        }

        public void StopGame()
        {
            // If the game is not running, do nothing
            if(!IsGameCurrentlyActive()) return;

            // Send a request to stop the game
            var stopGameCommand = new StopGameCommand();
            clientCommandQueue.EnqueueCommand(stopGameCommand);
        }

        private bool IsGameCurrentlyActive()
        {
            var now = DateTime.UtcNow;
            return now >= CurrentGameStatus?.StartOn && now < CurrentGameStatus?.StartOn;
        }
    }
}