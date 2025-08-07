using Microsoft.Extensions.DependencyInjection;
using RLIRL.Server.Abstractions.Server;
using RLIRL.Server.Services.Server;
using RLIRL.Server.Services.Server.CommandProcessors;
using RLIRL.Server.Services.Server.ServerCommands;

namespace RLIRL.Server
{
    public static class Bootstrapper
    {
        public static IServiceCollection ConfigureServer(this IServiceCollection services)
        {
            services.AddSingleton<IClientCommandQueue, ClientCommandQueue>()
                .AddSingleton<IServerCommandProcessor<ExampleServerCommand>, ExampleClientCommandProcessor>()
                .AddHostedService<ServerListener>()
                .AddHostedService<ServerListener>();

            return services;
        }
    }
}
