using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    [CommandName("goal_scored")]
    public class GoalScoredResponse : IServerResponse
    {
        [JsonPropertyName("status")]
        public string Status { get; set; } = "success";

        [JsonPropertyName("action")]
        public string Action { get; set; } = "goal_scored";

        [JsonPropertyName("message")]
        public string Message { get; set; } = string.Empty;
    }
}