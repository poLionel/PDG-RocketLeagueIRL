using AutoMapper;
using MauiWifiManager.Abstractions;
using RLIRL.App.Models;

namespace RLIRL.App
{
    internal class MapperProfile : Profile
    {
        public MapperProfile()
        {
            _ = CreateMap<NetworkData, NetworkListItem>()
                .ForMember(dest => dest.Ssid, opt => opt.MapFrom(src => src.Ssid ?? string.Empty))
                .ForMember(dest => dest.Icon, opt => opt.MapFrom(src => GetIconForSignalStrenght(src.SignalStrength)));
        }

        private static string? GetIconForSignalStrenght(object? signalStrength) => signalStrength switch
        {
            (byte)1 => Fonts.FluentUI.wifi_4_20_regular,
            (byte)2 => Fonts.FluentUI.wifi_3_20_regular,
            (byte)3 => Fonts.FluentUI.wifi_2_20_regular,
            (byte)4 => Fonts.FluentUI.wifi_1_20_regular,
            _ => null
        };
    }
}
