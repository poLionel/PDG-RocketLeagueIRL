using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    [CommandName("stop_game")]
    public class StopGameResponse : IServerResponse
    {
        [JsonPropertyName("status")]
        public string Status { get; set; } = "success";

        [JsonPropertyName("action")]
        public string Action { get; set; } = "stop_game";

        [JsonPropertyName("message")]
        public string Message { get; set; } = string.Empty;
    }
}