namespace RLIRL.Server.Abstractions.Abstractions
{
    public interface IServerCommandSerializer
    {
        byte[] SerializeCommand(IClientCommand serverCommand);
    }
}