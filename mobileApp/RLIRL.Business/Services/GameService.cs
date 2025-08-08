using RLIRL.Business.Abstractions;
using RLIRL.Business.Models;

namespace RLIRL.Business.Services
{
    internal class GameService : IGameService
    {
        public GameData? CurrentGameData => throw new NotImplementedException();

        public event EventHandler<GameData>? GameDataUpdated;
    }
}
