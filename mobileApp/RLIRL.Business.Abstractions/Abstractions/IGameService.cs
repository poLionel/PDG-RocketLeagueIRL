using RLIRL.Business.Abstractions.Models;

namespace RLIRL.Business.Abstractions.Abstractions
{
    /// <summary>
    /// Interface for managing game status
    /// </summary>
    public interface IGameService
    {
        /// <summary>
        /// Gets the current game status
        /// </summary>
        GameStatus? CurrentGameStatus { get; }

        /// <summary>
        /// Event triggered when the game status changes
        /// </summary>
        event EventHandler<GameStatus?>? GameStatusChanged;

        /// <summary>
        /// Updates the game status
        /// </summary>
        /// <param name="status">Status to set</param>
        void UpdateGameStatus(GameStatus? status);
    }
}

