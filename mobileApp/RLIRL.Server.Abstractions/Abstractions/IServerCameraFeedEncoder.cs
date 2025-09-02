namespace RLIRL.Server.Abstractions.Abstractions
{
    /// <summary>
    /// Interface for camera feed services
    /// </summary>
    public interface IServerCameraFeedEncoder
    {
        /// <summary>
        /// Gets the current camera feed as a stream
        /// </summary>
        /// <returns>The camera feed stream or null if not available</returns>
        Stream? GetCurrentCameraFeed();

        /// <summary>
        /// Sets the last frame that will be shown on the camera feed
        /// </summary>
        /// <param name="base64jpeg">Image to be added</param>
        /// <param name="timestamp">Timestamp of the image</param>
        void UpdateLastFrame(string base64jpeg, double timestamp);
    }
}
