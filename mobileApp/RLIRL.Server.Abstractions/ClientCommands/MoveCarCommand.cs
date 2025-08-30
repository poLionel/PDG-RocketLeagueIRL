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

        [JsonPropertyName("move")]
        public Direction Direction { get; set; }

        [JsonPropertyName("x")]
        public int Steering { get; set; }

        [JsonPropertyName("boost")]
        public string Boost { get; set; } = "false";
    }
}