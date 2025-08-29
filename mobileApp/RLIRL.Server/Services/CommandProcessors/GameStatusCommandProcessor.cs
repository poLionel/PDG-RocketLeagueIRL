using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Services.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GameStatusCommandProcessor(IGameService gameService) : ServerCommandProcessorBase<GameStatusCommand>
    {
        public override Task ProcessCommandAsync(GameStatusCommand command)
        {
            var newGameStatus = new GameStatus()
            {
                // data
            };

            gameService.UpdateGameStatus(newGameStatus);

            return Task.CompletedTask;
        }
    }
}
