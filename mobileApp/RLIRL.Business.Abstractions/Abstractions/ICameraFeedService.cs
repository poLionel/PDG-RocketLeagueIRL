using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.Business.Abstractions.Abstractions
{
    public interface ICameraFeedService
    {
        /// <summary>
        /// Gets the available camera feeds
        /// </summary>
        IEnumerable<CameraFeed> CameraFeeds { get; }

        /// <summary>
        /// Event triggered when the available camera feed changes
        /// </summary>
        event EventHandler<IEnumerable<CameraFeed>>? CameraFeedsChanged;

        /// <summary>
        /// Updates the available camera feeds
        /// </summary>
        /// <param name="availableFeeds">Available feeds to set</param>
        void UpdateAvailableFeeds(IEnumerable<CameraFeed> availableFeeds);

        /// <summary>
        /// Request refresh camera feed data
        /// </summary>
        void Refresh();
    }
}
