using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ClientCommands;

namespace RLIRL.Business.Services
{
    internal class CameraFeedService(IClientCommandQueue clientCommandQueue) : ICameraFeedService
    {
        public IEnumerable<CameraFeed> CameraFeeds { get; private set; } = [];

        public event EventHandler<IEnumerable<CameraFeed>>? CameraFeedsChanged;

        private IEnumerable<int> availableCameraFeeds= [];

        public void UpdateAvailableFeeds(IEnumerable<int> availableFeeds)
        {
            if (availableCameraFeeds != availableFeeds)
            {
                availableCameraFeeds = availableFeeds;
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
