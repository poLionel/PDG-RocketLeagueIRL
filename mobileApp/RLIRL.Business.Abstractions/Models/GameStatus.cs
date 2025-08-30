namespace RLIRL.Business.Abstractions.Models
{
    public class GameStatus
    {
        // Game timing
        public DateTime StartOn { get; set; }
        public DateTime EndOn { get; set; }
        
        // Red team
        public int RedTeamScore { get; set; }
        public int[] RedTeamCars { get; set; } = [];
        
        // Blue team
        public int BlueTeamScore { get; set; }
        public int[] BlueTeamCars { get; set; } = [];
    }
}