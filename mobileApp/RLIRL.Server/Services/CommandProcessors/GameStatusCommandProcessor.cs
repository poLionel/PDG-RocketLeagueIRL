using AutoMapper;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GameStatusCommandProcessor(IGameService gameService, IMapper mapper) : ServerCommandProcessorBase<GameStatusCommand>
    {
        public override Task ProcessCommandAsync(GameStatusCommand command)
        {
            var gameStatus =  mapper.Map<GameStatus>(command);

            gameService.UpdateGameStatus(gameStatus);

            return Task.CompletedTask;
        }
    }
}
