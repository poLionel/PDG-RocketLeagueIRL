using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerResponses
{
    public class CameraFeed
    {
        [JsonPropertyName("car_id")]
        public int CarId { get; set; }

        [JsonPropertyName("url")]
        public required string Url { get; set; }

        [JsonPropertyName("port")]
        public short Port { get; set; }
    }
}
