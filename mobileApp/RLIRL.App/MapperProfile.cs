using AutoMapper;
using MauiWifiManager.Abstractions;
using RLIRL.App.Models;
using RLIRL.App.Resources.Fonts;
using RLIRL.Business.Abstractions.Models;
using RLIRL.Server.Abstractions.ServerResponses;

namespace RLIRL.App
{
    internal class MapperProfile : Profile
    {
        public MapperProfile()
        {
            _ = CreateMap<NetworkData, NetworkListItem>()
                .ForMember(dest => dest.Ssid, opt => opt.MapFrom(src => src.Ssid ?? string.Empty))
                .ForMember(dest => dest.Icon, opt => opt.MapFrom(src => GetIconForSignalStrenght(src.SignalStrength)));

            _ = CreateMap<GameStatus, GameInfo>()
                .ForMember(dest => dest.BlueScore, opt => opt.MapFrom(src => src.BlueTeamScore))
                .ForMember(dest => dest.RedScore, opt => opt.MapFrom(src => src.RedTeamScore))
                .ForMember(dest => dest.MatchLengthSeconds, opt => opt.MapFrom(src => src.MatchLengthSeconds))
                .ForMember(dest => dest.StartTime, opt => opt.MapFrom(src => src.StartDate))
                .ForMember(dest => dest.State, opt => opt.MapFrom(src => src.State))
                .ForMember(dest => dest.StateMessage, opt => opt.MapFrom(src => GetStateMessage(src.State)));

        }

        private static string? GetIconForSignalStrenght(object? signalStrength) => signalStrength switch
        {

            (byte)1 => FluentUI.wifi_4_20_regular,
            (byte)2 => FluentUI.wifi_3_20_regular,
            (byte)3 => FluentUI.wifi_2_20_regular,
            (byte)4 => FluentUI.wifi_1_20_regular,
            _ => null
        };

        private static string GetStateMessage(GameState state) => state switch
        {
            GameState.Active => "Game in progress",
            GameState.Paused => "Game paused",
            GameState.Ended => "Game finished",
            GameState.NotStarted => "Game not started",
            _ => string.Empty
        };
    }
}
