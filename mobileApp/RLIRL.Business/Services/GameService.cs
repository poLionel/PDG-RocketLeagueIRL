using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;

namespace RLIRL.Business.Services
{
    internal class GameService : IGameService
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
    }
}