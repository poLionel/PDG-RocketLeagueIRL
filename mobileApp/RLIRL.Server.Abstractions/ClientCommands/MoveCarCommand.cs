using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ClientCommands
{
    [CommandName("move_car")]
    public class MoveCarCommand : IClientCommand
    {
        [JsonPropertyName("car")]
        public int Car { get; set; }

        [JsonPropertyName("direction")]
        public Directions Direction { get; set; }

        [JsonPropertyName("boost")]
        public bool Boost { get; set; }
    }
}
