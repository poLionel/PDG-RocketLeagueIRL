using AutoMapper;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server
{
    internal class MapperProfile : Profile
    {
        public MapperProfile()
        {
            _ = CreateMap<GameStatusCommand, GameStatus>();
        }
    }
}
