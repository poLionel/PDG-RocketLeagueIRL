using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    [CommandName("get_accessible_car_feeds")]
    public class GetAccessibleCarFeedsResponse : IServerResponse
    {
        [JsonPropertyName("accessible_feeds")]
        public int[] AccessibleFeeds { get; set; } = [];
    }
}