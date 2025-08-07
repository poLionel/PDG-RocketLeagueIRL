using RLIRL.Business.Models;

namespace RLIRL.Business.Abstractions
{
    public interface IGameService
    {
        GameData? CurrentGameData { get; }

        event EventHandler<GameData>? GameDataUpdated;
    }
}
