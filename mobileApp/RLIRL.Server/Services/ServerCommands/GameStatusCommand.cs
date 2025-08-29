using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Services.Server;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Services.ServerCommands
{
    [CommandName("get_game_status")]
    public class GameStatusCommand : IServerCommand
    {
        [JsonPropertyName("car")]
        public int Car { get; set; }
    }
}
