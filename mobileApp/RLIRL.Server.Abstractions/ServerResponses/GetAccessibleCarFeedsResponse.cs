using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    [CommandName("get_accessible_car_feeds")]
    public class GetAccessibleCarFeedsResponse : IServerResponse
    {
        [JsonPropertyName("status")]
        public string Status { get; set; } = "success";

        [JsonPropertyName("action")]
        public string Action { get; set; } = "get_accessible_car_feeds";

        [JsonPropertyName("accessible_feeds")]
        public int[] AccessibleFeeds { get; set; } = [];
    }
}