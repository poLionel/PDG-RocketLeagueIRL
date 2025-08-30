using AutoMapper;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.ServerCommands;
using RLIRL.Server.Services.CommandProcessors;

namespace RLIRL.Server
{
    internal class MapperProfile : Profile
    {
        public MapperProfile()
        {
            _ = CreateMap<GetGameStatusResponse, GameStatus>();
        }
    }
}
