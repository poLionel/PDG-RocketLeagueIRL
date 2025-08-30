using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    [CommandName("get_car_status")]
    public class GetCarStatusResponse : IServerResponse
    {
        [JsonPropertyName("status")]
        public string Status { get; set; } = "success";

        [JsonPropertyName("action")]
        public string Action { get; set; } = "get_car_status";

        [JsonPropertyName("car")]
        public int Car { get; set; }

        [JsonPropertyName("battery_level")]
        public int BatteryLevel { get; set; }

        [JsonPropertyName("move")]
        public string Move { get; set; } = string.Empty;

        [JsonPropertyName("x")]
        public int X { get; set; }

        [JsonPropertyName("boost")]
        public string Boost { get; set; } = "false";

        [JsonPropertyName("boost_value")]
        public int BoostValue { get; set; }
    }
}