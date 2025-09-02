using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.Business.Services
{
    internal class CameraFeedService(IClientCommandQueue clientCommandQueue, IServerCameraFeedEncoder serverCameraFeedService) : ICameraFeedService
    {
        public IEnumerable<CameraFeed> CameraFeeds { get; private set; } = [];
        public int? ActiveCameraFeed { get; private set; }

        public event EventHandler<IEnumerable<CameraFeed>>? CameraFeedsChanged;

        public event EventHandler<int>? ActiveCameraFeedChanged;

        private IEnumerable<int> availableCameraFeeds = [];

        public void UpdateAvailableFeeds(IEnumerable<int> availableFeeds)
        {
            if (availableCameraFeeds != availableFeeds)
            {
                availableCameraFeeds = availableFeeds;
            }
        }

        public void UpdateActiveCameraFeed(int? feed)
        {
            if (ActiveCameraFeed != feed)
            {
                ActiveCameraFeed = feed;
            }

            CameraFeedsChanged?.Invoke(this, CameraFeeds);
        }

        public Stream? GetActiveCameraFeed()
        {
            return serverCameraFeedService.GetCurrentCameraFeed();
        }

        public void Refresh()
        {
            // Send a request to refresh the camera feeds
            var refreshCommand = new GetAccessibleCarFeedsCommand();
            clientCommandQueue.EnqueueCommand(refreshCommand);
        }
    }
}
