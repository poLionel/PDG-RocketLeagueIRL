using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ClientCommands
{
    [CommandName("select_car")]
    public class SelectCarCommand : IClientCommand
    {
        [JsonPropertyName("car")]
        public int Car { get; set; }
    }
}