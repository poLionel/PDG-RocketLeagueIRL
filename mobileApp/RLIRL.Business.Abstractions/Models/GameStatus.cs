using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.Business.Abstractions.Models
{
    public class GameStatus
    {
        // Red team
        public int RedTeamScore { get; set; }
        public int[] RedTeamCars { get; set; } = [];
        
        // Blue team
        public int BlueTeamScore { get; set; }
        public int[] BlueTeamCars { get; set; } = [];

        // Game State
        public int TimeRemaining { get; set; }
        public int ElapsedTime { get; set; }
        public GameState State { get; set; }
        public int MatchLengthSeconds { get; set; }
        public DateTime? StartDate { get; set; }
        public int TotalPausedTime { get; set; }
    }
}