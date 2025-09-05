using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    public class Teams
    {
        [JsonPropertyName("red")]
        public TeamInfo Red { get; set; } = new();

        [JsonPropertyName("blue")]
        public TeamInfo Blue { get; set; } = new();
    }
}