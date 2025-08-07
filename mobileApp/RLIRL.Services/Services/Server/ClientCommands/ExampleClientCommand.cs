using RLIRL.Services.Abstractions.Server;

namespace RLIRL.Services.Services.Server.ClientCommands
{
    [Serializable, CommandName("ExampleServerCommand")]
    public class ExampleClientCommand : IClientCommand
    {
    }
}
