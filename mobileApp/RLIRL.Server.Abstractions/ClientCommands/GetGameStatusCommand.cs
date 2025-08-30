using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.Attributes;

namespace RLIRL.Server.Abstractions.ClientCommands
{
    [CommandName("get_game_status")]
    public class GetGameStatusCommand : IClientCommand
    {
        // No properties needed - this is just a request for game status
    }
}