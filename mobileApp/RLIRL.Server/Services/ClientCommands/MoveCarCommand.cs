using RLIRL.Server.Abstractions.Server;
using RLIRL.Server.Services.Server;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Services.ClientCommands
{
    [CommandName("move_car")]
    internal class MoveCarCommand : IClientCommand
    {
        [JsonPropertyName("car")]
        public int Car { get; set; }

        [JsonPropertyName("direction")]
        public Directions Direction { get; set; }

        [JsonPropertyName("boost")]
        public bool Boost { get; set; }
    }
}
