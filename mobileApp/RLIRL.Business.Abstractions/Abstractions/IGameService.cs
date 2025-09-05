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

        /// <summary>
        /// Request refres game data
        /// </summary>
        void Refresh();

        /// <summary>
        /// Requests to start the game
        /// </summary>
        void StartGame();

        /// <summary>
        /// Requests to stop the game
        /// </summary>
        void StopGame();

        /// <summary>
        /// Request to resume the game
        /// </summary>
        void ResumeGame();

        /// <summary>
        /// Request to end the game
        /// </summary>
        void EndGame();

        /// <summary>
        /// Request to score a goal
        /// </summary>
        /// <param name="team">Team that scored the goal</param>
        void ScoreGoal(string team);

        /// <summary>
        /// Request to undo the last scored goal
        /// </summary>
        void UndoGoal();
    }
}

