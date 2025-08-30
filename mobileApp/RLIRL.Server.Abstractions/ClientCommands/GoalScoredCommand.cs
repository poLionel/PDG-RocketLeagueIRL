using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ClientCommands
{
    [CommandName("goal_scored")]
    public class GoalScoredCommand : IClientCommand
    {
        [JsonPropertyName("team")]
        public string Team { get; set; } = string.Empty;
    }
}