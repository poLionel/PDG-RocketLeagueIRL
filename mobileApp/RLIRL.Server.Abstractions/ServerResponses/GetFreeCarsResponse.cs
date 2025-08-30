using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    [CommandName("get_free_cars")]
    public class GetFreeCarsResponse : IServerResponse
    {
        [JsonPropertyName("free_cars")]
        public int[] FreeCars { get; set; } = [];
    }
}