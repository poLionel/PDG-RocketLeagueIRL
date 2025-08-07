namespace RLIRL.Server.Abstractions.Server
{
    public interface IClientCommandQueue
    {
        void EnqueueCommand(IClientCommand command);
        IClientCommand DequeueCommand();
    }
}
