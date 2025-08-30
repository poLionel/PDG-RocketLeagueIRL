using AutoMapper;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GetGameStatusResponseProcessor(IGameService gameService, IMapper mapper) : ServerResponseProcessorBase<GetGameStatusResponse>
    {
        public override Task ProcessCommandAsync(GetGameStatusResponse command)
        {
            var gameStatus = mapper.Map<GameStatus>(command);

            gameService.UpdateGameStatus(gameStatus);

            return Task.CompletedTask;
        }
    }
}
