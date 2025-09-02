using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class VideoFrameResponseProcessor(IServerCameraFeedEncoder cameraFeedService) : ServerResponseProcessorBase<VideoFrameResponse>
    {
        public override Task ProcessResponseAsync(VideoFrameResponse response)
        {
            if (response?.Base64Jpeg != null)
            {
                // Update the camera feed service with the new frame
                cameraFeedService.UpdateLastFrame(response.Base64Jpeg, response.Timestamp);
            }

            return Task.CompletedTask;
        }
    }
}