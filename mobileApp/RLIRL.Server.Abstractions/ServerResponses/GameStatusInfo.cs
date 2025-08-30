using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    public class GameStatusInfo
    {
        [JsonPropertyName("teams")]
        public Teams Teams { get; set; } = new();

        [JsonPropertyName("start_on")]
        public DateTime StartOn { get; set; }

        [JsonPropertyName("end_on")]
        public DateTime EndOn { get; set; }
    }
}