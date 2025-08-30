namespace RLIRL.Server.Abstractions.Abstractions
{
    public interface IServerConnectionStatusService
    {
        Task<bool> IsServerConnectedAsync(CancellationToken cancellationToken = default);
    }
}
