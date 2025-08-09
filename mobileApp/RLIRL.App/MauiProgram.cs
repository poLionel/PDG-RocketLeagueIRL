using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using RLIRL.Business;

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

            return builder.Build();
        }
    }
}
