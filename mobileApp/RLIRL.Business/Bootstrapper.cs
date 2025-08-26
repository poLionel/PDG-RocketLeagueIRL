using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using RLIRL.Business.Abstractions;
using RLIRL.Business.Services;

namespace RLIRL.Business
{
    public static class Bootstrapper
    {
        public static IServiceCollection RegisterBusiness(this IServiceCollection services, IConfiguration configuration)
        {
            services.AddSingleton<IGameService, GameService>();

            return services;
        }
    }
}
