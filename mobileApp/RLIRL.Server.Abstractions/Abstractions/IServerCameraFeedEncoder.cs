namespace RLIRL.Server.Abstractions.Abstractions
{
    /// <summary>
    /// Interface for camera feed services
    /// </summary>
    public interface IServerCameraFeedEncoder
    {
        /// <summary>
        /// Gets the current camera feed as a stream (singleton MJPEG stream)
        /// </summary>
        /// <param name="cancellationToken">Cancellation token to cancel the operation</param>
        /// <returns>The camera feed stream</returns>
        Stream GetCurrentCameraFeed(CancellationToken cancellationToken = default);

        /// <summary>
        /// Sets the last frame that will be shown on the camera feed
        /// </summary>
        /// <param name="base64jpeg">Image to be added</param>
        /// <param name="timestamp">Timestamp of the image</param>
        void UpdateLastFrame(string base64jpeg, double timestamp);
    }
}
