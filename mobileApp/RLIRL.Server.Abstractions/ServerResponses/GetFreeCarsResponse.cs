using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    [CommandName("get_free_cars")]
    public class GetFreeCarsResponse : IServerResponse
    {
        [JsonPropertyName("status")]
        public string Status { get; set; } = "success";

        [JsonPropertyName("action")]
        public string Action { get; set; } = "get_free_cars";

        [JsonPropertyName("free_cars")]
        public int[] FreeCars { get; set; } = [];
    }
}