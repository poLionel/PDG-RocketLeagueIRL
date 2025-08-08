namespace RLIRL.Server.Abstractions
{
    public interface ICameraFeedService
    {
        Task<Stream?> GetCameraFeedAsync(string id);
    }
}
