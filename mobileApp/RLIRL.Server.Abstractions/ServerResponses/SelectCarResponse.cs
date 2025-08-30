using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    [CommandName("select_car")]
    public class SelectCarResponse : IServerResponse
    {
        [JsonPropertyName("car")]
        public int Car { get; set; }
    }
}