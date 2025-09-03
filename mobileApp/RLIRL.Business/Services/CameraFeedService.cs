using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;
using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.Business.Services
{
    internal class CameraFeedService(IClientCommandQueue clientCommandQueue) : ICameraFeedService
    {
        public IEnumerable<CameraFeed> CameraFeeds { get; private set; } = [];

        public event EventHandler<IEnumerable<CameraFeed>>? CameraFeedsChanged;

        public void UpdateAvailableFeeds(IEnumerable<CameraFeed> availableFeeds)
        {
            if (CameraFeeds != availableFeeds)
            {
                CameraFeeds = availableFeeds;
                CameraFeedsChanged?.Invoke(this, CameraFeeds);
            }
        }

        public void Refresh()
        {
            // Send a request to refresh the camera feeds
            var refreshCommand = new GetAccessibleCarFeedsCommand();
            clientCommandQueue.EnqueueCommand(refreshCommand);
        }
    }
}
