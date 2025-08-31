using RLIRL.Server.Abstractions.ServerResponses;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    public class GameStatusInfo
    {
        [JsonPropertyName("teams")]
        public Teams Teams { get; set; } = new();

        [JsonPropertyName("time_remaining")]
        public int TimeRemaining { get; set; }

        [JsonPropertyName("elapsed_time")]
        public int ElapsedTime { get; set; }

        [JsonPropertyName("state")]
        public GameState State { get; set; }

        [JsonPropertyName("match_length_seconds")]
        public int MatchLengthSeconds { get; set; }

        [JsonPropertyName("start_date")]
        public DateTime? StartDate { get; set; }

        [JsonPropertyName("total_paused_time")]
        public int TotalPausedTime { get; set; }
    }
}