using RLIRL.Business.Models;

namespace RLIRL.Business.Abstractions
{
    /// <summary>
    /// Interface for managing game data and state
    /// </summary>
    public interface IGameService
    {
        /// <summary>
        /// Gets the current game data
        /// </summary>
        GameData? CurrentGameData { get; }

        /// <summary>
        /// Event triggered when the game data is updated
        /// </summary>
        event EventHandler<GameData>? GameDataUpdated;
    }
}
