using CommunityToolkit.Maui;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using RLIRL.App.ViewModels;
using RLIRL.Business;
using RLIRL.Server;
using RLIRL.Server.Abstractions;

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
                });

            builder.Configuration.AddJsonStream(configuration);

#if DEBUG
            builder.Logging.AddDebug();
#endif

            builder.Services.RegisterBusiness(builder.Configuration);
            builder.Services.RegisterServer(builder.Configuration);

            // Register the view view models
            builder.Services.AddTransient<WifiSelectorViewModel>();

            var app = builder.Build();

            // Start the server command sender and listener
            var commandListener = app.Services.GetRequiredService<IServerCommandListener>();
            commandListener.Start();

            var commandSender = app.Services.GetRequiredService<IServerCommandSender>();
            commandSender.Start();
            return app;
        }
    }
}
