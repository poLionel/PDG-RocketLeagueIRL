using AutoMapper;
using MauiWifiManager.Abstractions;
using RLIRL.App.Models;
using RLIRL.App.Resources.Fonts;

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

            (byte)1 => FluentUI.wifi_4_20_regular,
            (byte)2 => FluentUI.wifi_3_20_regular,
            (byte)3 => FluentUI.wifi_2_20_regular,
            (byte)4 => FluentUI.wifi_1_20_regular,
            _ => null
        };
    }
}
