namespace RLIRL.Server.Abstractions.Server
{
    /// <summary>
    /// Represents a command sent by the client to the server
    /// </summary>
    public interface IClientCommand
    {
        public string Action { get; set; }
    }
}
