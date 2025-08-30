using AutoMapper;
using RLIRL.Business.Abstractions.Abstractions;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server.Services.CommandProcessors
{
    internal class GetGameStatusResponseProcessor(IGameService gameService, IMapper mapper) : ServerResponseProcessorBase<GetGameStatusResponse>
    {
        public override Task ProcessResponseAsync(GetGameStatusResponse response)
        {
            var gameStatus = mapper.Map<GameStatus>(response);

            gameService.UpdateGameStatus(gameStatus);

            return Task.CompletedTask;
        }
    }
}
