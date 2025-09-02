using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    public class TeamInfo
    {
        [JsonPropertyName("score")]
        public int Score { get; set; }

        [JsonPropertyName("cars")]
        public int[] Cars { get; set; } = [];
    }
}