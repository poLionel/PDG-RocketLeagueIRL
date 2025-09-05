using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ClientCommands
{
    [CommandName("get_car_status")]
    public class GetCarStatusCommand : IClientCommand
    {
        [JsonPropertyName("car")]
        public int Car { get; set; }
    }
}