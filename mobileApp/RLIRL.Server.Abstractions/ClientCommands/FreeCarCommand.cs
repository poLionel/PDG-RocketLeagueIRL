using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ClientCommands
{
    [CommandName("free_car")]
    public class FreeCarCommand : IClientCommand
    {
        [JsonPropertyName("car")]
        public int Car { get; set; }
    }
}