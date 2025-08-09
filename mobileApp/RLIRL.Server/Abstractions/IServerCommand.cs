namespace RLIRL.Server.Abstractions.Server
{
    /// <summary>
    /// Represents a command sent by the server to the client
    /// </summary>
    public interface IServerCommand
    {
        public string Action { get; set; }
    }
}
