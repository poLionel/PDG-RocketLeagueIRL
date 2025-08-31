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
                // Team properties
                .ForMember(dest => dest.RedTeamScore, opt => opt.MapFrom(src => src.GameStatus.Teams.Red.Score))
                .ForMember(dest => dest.RedTeamCars, opt => opt.MapFrom(src => src.GameStatus.Teams.Red.Cars))
                .ForMember(dest => dest.BlueTeamScore, opt => opt.MapFrom(src => src.GameStatus.Teams.Blue.Score))
                .ForMember(dest => dest.BlueTeamCars, opt => opt.MapFrom(src => src.GameStatus.Teams.Blue.Cars))
                // New game status properties
                .ForMember(dest => dest.TimeRemaining, opt => opt.MapFrom(src => src.GameStatus.TimeRemaining))
                .ForMember(dest => dest.ElapsedTime, opt => opt.MapFrom(src => src.GameStatus.ElapsedTime))
                .ForMember(dest => dest.State, opt => opt.MapFrom(src => src.GameStatus.State))
                .ForMember(dest => dest.MatchLengthSeconds, opt => opt.MapFrom(src => src.GameStatus.MatchLengthSeconds))
                .ForMember(dest => dest.StartDate, opt => opt.MapFrom(src => src.GameStatus.StartDate))
                .ForMember(dest => dest.TotalPausedTime, opt => opt.MapFrom(src => src.GameStatus.TotalPausedTime));
        }
    }
}
