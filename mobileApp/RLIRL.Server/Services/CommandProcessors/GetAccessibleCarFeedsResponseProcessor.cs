using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GetAccessibleCarFeedsResponseProcessor(ICameraFeedService cameraFeedService) : ServerResponseProcessorBase<GetAccessibleCarFeedsResponse>
    {
        public override Task ProcessResponseAsync(GetAccessibleCarFeedsResponse response)
        {
            // Update the camera feed service with the new accessible feeds
            cameraFeedService.UpdateAvailableFeeds(response.AccessibleFeeds);
            return Task.CompletedTask;
        }
    }
}