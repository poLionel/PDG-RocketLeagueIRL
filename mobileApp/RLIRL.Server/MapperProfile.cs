using AutoMapper;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.ServerCommands;

namespace RLIRL.Server
{
    internal class MapperProfile : Profile
    {
        public MapperProfile()
        {
            _ = CreateMap<GetGameStatusResponse, GameStatus>()
                .ForMember(dest => dest.StartOn, opt => opt.MapFrom(src => src.GameStatus.StartOn))
                .ForMember(dest => dest.EndOn, opt => opt.MapFrom(src => src.GameStatus.EndOn))
                .ForMember(dest => dest.RedTeamScore, opt => opt.MapFrom(src => src.GameStatus.Teams.Red.Score))
                .ForMember(dest => dest.RedTeamCars, opt => opt.MapFrom(src => src.GameStatus.Teams.Red.Cars))
                .ForMember(dest => dest.BlueTeamScore, opt => opt.MapFrom(src => src.GameStatus.Teams.Blue.Score))
                .ForMember(dest => dest.BlueTeamCars, opt => opt.MapFrom(src => src.GameStatus.Teams.Blue.Cars));
        }
    }
}
