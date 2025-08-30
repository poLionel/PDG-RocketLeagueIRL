using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;

namespace RLIRL.Server.Abstractions.ServerCommands
{
    [CommandName("get_car_video_feed")]
    public class GetCarVideoFeedResponse : IServerResponse
    {
        public byte[] JpegData { get; set; } = [];
    }
}