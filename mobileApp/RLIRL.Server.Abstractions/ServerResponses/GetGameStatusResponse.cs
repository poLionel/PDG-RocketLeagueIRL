using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    [CommandName("get_game_status")]
    public class GetGameStatusResponse : IServerResponse
    {
        [JsonPropertyName("game_status")]
        public GameStatusInfo GameStatus { get; set; } = new();
    }
}