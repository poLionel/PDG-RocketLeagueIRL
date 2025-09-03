namespace RLIRL.Server.Abstractions.Abstractions
{
    /// <summary>
    /// Interface for camera feed services
    /// </summary>
    public interface IServerCameraFeedService
    {
        /// <summary>
        /// Gets the camera feed stream for a specific car
        /// </summary>
        /// <param name="carId"></param>
        /// <returns></returns>
        Stream GetCameraFeed(int carId);
    }
}
