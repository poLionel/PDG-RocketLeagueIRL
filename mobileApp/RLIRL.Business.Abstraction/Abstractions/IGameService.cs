using RLIRL.Business.Models;

namespace RLIRL.Business.Abstractions
{
    /// <summary>
    /// Interface for managing game status and state
    /// </summary>
    public interface IGameService
    {
        /// <summary>
        /// Gets the current game status
        /// </summary>
        GameStatus? CurrentGameStatus { get; }

        /// <summary>
        /// Event triggered when the game status is updated
        /// </summary>
        event EventHandler<GameStatus?>? GameStatusChanged;
    }
}