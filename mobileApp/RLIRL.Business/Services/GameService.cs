using RLIRL.Business.Abstractions;
using RLIRL.Business.Models;

namespace RLIRL.Business.Services
{
    internal class GameService : IGameService
    {
        public GameStatus? CurrentGameStatus { get; private set; }

        public event EventHandler<GameStatus?>? GameStatusChanged;
    }
}