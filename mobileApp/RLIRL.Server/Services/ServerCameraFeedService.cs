using RLIRL.Server.Abstractions.Abstractions;

namespace RLIRL.Server.Services
{
    internal class ServerCameraFeedService : IServerCameraFeedService
    {
        public Task<Stream?> GetCameraFeedAsync(string id)
        {
            throw new NotImplementedException();
        }
    }
}
