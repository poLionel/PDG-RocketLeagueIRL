using Microsoft.Extensions.DependencyInjection;
using RLIRL.Business.Abstractions;
using RLIRL.Business.Services;
using RLIRL.Server;

namespace RLIRL.Business
{
    public static class Bootstrapper
    {
        public static IServiceCollection ConfigureBusiness(this IServiceCollection services)
        {
            services.AddSingleton<IGameService, GameService>();

            services.ConfigureServer();

            return services;
        }
    }
}
