using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    public class GameStatusInfo
    {
        [JsonPropertyName("teams")]
        public Teams Teams { get; set; } = new();

        [JsonPropertyName("time_remaining")]
        public int TimeRemaining { get; set; }
    }
}