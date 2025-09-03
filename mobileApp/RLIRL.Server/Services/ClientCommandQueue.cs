using RLIRL.Server.Abstractions.Abstractions;
using System.Threading.Channels;

internal class ClientCommandQueue : IClientCommandQueue
{
    private readonly Channel<IClientCommand> channel;

    public ClientCommandQueue()
    {
        channel = Channel.CreateUnbounded<IClientCommand>(
            new UnboundedChannelOptions
            {
                SingleReader = false,
                SingleWriter = false
            });
    }

    public void EnqueueCommand(IClientCommand command)
    {
        if (!channel.Writer.TryWrite(command))
        {
            throw new InvalidOperationException("Unable to enqueue command.");
        }
    }

    public async Task<IClientCommand> DequeueCommandAsync(CancellationToken cancellationToken = default)
    {
        return await channel.Reader.ReadAsync(cancellationToken);
    }
}
