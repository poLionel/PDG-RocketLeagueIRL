using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ClientCommands
{
    /// <summary>
    /// Represents a client command used to control a car's movement.
    /// </summary>
    [CommandName("move_car")]
    public class MoveCarCommand : IClientCommand
    {
        [JsonPropertyName("car")]
        public int Car { get; set; }

        [JsonPropertyName("move")]
        public Directions Direction { get; set; }

        [JsonPropertyName("boost")]
        public bool Boost { get; set; }

        [JsonPropertyName("x")]
        public int SteeringValue { get; set; }
    }
}
