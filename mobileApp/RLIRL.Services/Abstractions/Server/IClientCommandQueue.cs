namespace RLIRL.Services.Abstractions.Server
{
    public interface IClientCommandQueue
    {
        void EnqueueCommand(IClientCommand command);
        IClientCommand DequeueCommand();
    }
}
