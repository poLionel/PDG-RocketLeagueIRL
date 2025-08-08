using RLIRL.Server.Abstractions.Server;

namespace RLIRL.Server.Services.Server.ClientCommands
{
    [Serializable, CommandName("ExampleServerCommand")]
    public class ExampleClientCommand : IClientCommand
    {
    }
}
