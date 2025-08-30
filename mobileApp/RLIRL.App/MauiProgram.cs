using CommunityToolkit.Maui;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using RLIRL.App.Helper;
using RLIRL.App.Resources.Fonts;
using RLIRL.App.ViewModels;
using RLIRL.Business;
using RLIRL.Server;
using RLIRL.Server.Abstractions.Abstractions;

namespace RLIRL.App
{
    public static class MauiProgram
    {
        public static MauiApp CreateMauiApp()
        {
#if DEBUG
            var configuration = FileSystem.OpenAppPackageFileAsync($"appsettings.Development.json").Result
                ?? throw new InvalidOperationException("Configuration not found");
#else
            var configuration = FileSystem.OpenAppPackageFileAsync($"appsettings.json").Result
                ?? throw new InvalidOperationException("Configuration not found");
#endif
            var builder = MauiApp.CreateBuilder();
            builder
                .UseMauiApp<App>()
                .UseMauiCommunityToolkit()
                .ConfigureFonts(fonts =>
                {
                    fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
                    fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
                    fonts.AddFont("FluentSystemIcons-Regular.ttf", FluentUI.FontFamily);
                });

            builder.Configuration.AddJsonStream(configuration);

#if DEBUG
            builder.Logging.AddDebug();
#endif

#if ANDROID
            builder.Services.AddSingleton<IOrientationService, RLIRL.App.Platforms.Android.OrientationService>();
#endif

            builder.Services.RegisterBusiness(builder.Configuration);
            builder.Services.RegisterServer(builder.Configuration);
            builder.Services.AddAutoMapper(cfg => { }, typeof(MapperProfile));

            // ViewModels
            builder.Services.AddTransient<WifiConnectViewModel>();
            builder.Services.AddTransient<WifiSelectorViewModel>();
            builder.Services.AddTransient<MenuViewModel>();
            builder.Services.AddTransient<GameViewModel>();

            var app = builder.Build();

            // Start the server command sender and listener
            var commandListener = app.Services.GetRequiredService<IServerResponseListener>();
            commandListener.Start();

            var commandSender = app.Services.GetRequiredService<IServerCommandSender>();
            commandSender.Start();
            return app;
        }
    }
}
