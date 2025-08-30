using AutoMapper;
using MauiWifiManager.Abstractions;
using RLIRL.App.Models;
using RLIRL.App.Resources.Fonts;
using RLIRL.Business.Abstractions.Models;

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
                .ForMember(dest => dest.TimeLeft, opt => opt.MapFrom(src => CalculateTimeLeft(src.EndOn)))
                .ForMember(dest => dest.StartTime, opt => opt.MapFrom(src => src.StartOn))
                .ForMember(dest => dest.EndTime, opt => opt.MapFrom(src => src.EndOn))
                .ForMember(dest => dest.IsGameActive, opt => opt.MapFrom(src => IsGameCurrentlyActive(src.StartOn, src.EndOn)));
        }

        private static string? GetIconForSignalStrenght(object? signalStrength) => signalStrength switch
        {

            (byte)1 => FluentUI.wifi_4_20_regular,
            (byte)2 => FluentUI.wifi_3_20_regular,
            (byte)3 => FluentUI.wifi_2_20_regular,
            (byte)4 => FluentUI.wifi_1_20_regular,
            _ => null
        };

        private static string CalculateTimeLeft(DateTime endTime)
        {
            var timeLeft = endTime - DateTime.UtcNow;
            
            if (timeLeft <= TimeSpan.Zero)
                return "00:00";
                
            return timeLeft.ToString(@"mm\:ss");
        }

        private static bool IsGameCurrentlyActive(DateTime startTime, DateTime endTime)
        {
            var now = DateTime.UtcNow;
            return now >= startTime && now < endTime;
        }
    }
}
