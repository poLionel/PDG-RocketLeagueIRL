using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using RLIRL.Server.Abstractions.Server;
using RLIRL.Server.Services.Server;
using RLIRL.Server.Services.Server.CommandProcessors;
using RLIRL.Server.Services.Server.ServerCommands;

namespace RLIRL.Server
{
    public static class Bootstrapper
    {
        public static IServiceCollection RegisterServer(this IServiceCollection services, IConfiguration configuration)
        {
            services.Configure<ServerConfiguration>(configuration.GetSection(nameof(ServerConfiguration)));

            services.AddSingleton<IClientCommandQueue, ClientCommandQueue>()
                .AddSingleton<IServerCommandProcessor<ExampleServerCommand>, ExampleClientCommandProcessor>()
                .AddHostedService<ServerListener>()
                .AddHostedService<ServerSender>();

            return services;
        }
    }
}
