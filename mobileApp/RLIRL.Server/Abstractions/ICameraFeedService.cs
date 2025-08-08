namespace RLIRL.Server.Abstractions
{
    /// <summary>
    /// Interface for camera feed services
    /// </summary>
    public interface ICameraFeedService
    {
        /// <summary>
        /// Retrieves the camera feed stream for a given camera ID
        /// </summary>
        /// <param name="id">The unique identifier for the camera</param>
        /// <returns>A task that represents the asynchronous operation, containing the camera feed stream or null if not available</returns>
        Task<Stream?> GetCameraFeedAsync(string id);
    }
}
