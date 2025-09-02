using RLIRL.Business.Abstractions.Models;

namespace RLIRL.Business.Abstractions.Abstractions
{
    public interface ICameraFeedService
    {
        /// <summary>
        /// Gets the available camera feeds
        /// </summary>
        IEnumerable<CameraFeed> CameraFeeds { get; }

        /// <summary>
        /// Gets the currently active camera feed (car ID)
        /// </summary>
        int? ActiveCameraFeed { get; }

        /// <summary>
        /// Event triggered when the available camera feed changes
        /// </summary>
        event EventHandler<IEnumerable<CameraFeed>>? CameraFeedsChanged;

        /// <summary>
        /// Event triggered when the active camera feed changes
        /// </summary>
        event EventHandler<int>? ActiveCameraFeedChanged;

        /// <summary>
        /// Updates the available camera feeds
        /// </summary>
        /// <param name="availableFeeds">Available feeds to set</param>
        void UpdateAvailableFeeds(IEnumerable<int> availableFeeds);

        /// <summary>
        /// Get the current active camera feed as a stream
        /// </summary>
        /// <returns></returns>
        Stream? GetActiveCameraFeed();

        /// <summary>
        /// Request refres camera feed data
        /// </summary>
        void Refresh();
    }
}
