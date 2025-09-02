using RLIRL.Server.Abstractions.Abstractions;
using System.Text.Json.Serialization;

namespace RLIRL.Server.Abstractions.ServerResponses
{
    public class VideoFrameResponse : IServerResponse
    {
        [JsonPropertyName("car")]
        public int CarId { get; set; }

        [JsonPropertyName("video_frame")]
        public required string Base64Jpeg { get; set; }

        [JsonPropertyName("timestamp")]
        public double Timestamp { get; set; }
    }
}
