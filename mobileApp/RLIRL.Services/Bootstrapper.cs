using Microsoft.Extensions.DependencyInjection;
using RLIRL.Services.Abstractions.Server;
using RLIRL.Services.Services.Server;
using RLIRL.Services.Services.Server.CommandProcessors;
using RLIRL.Services.Services.Server.ServerCommands;

namespace RLIRL.Services
{
    public static class Bootstrapper
    {
        public static IServiceCollection ConfigureServiceLayer(this IServiceCollection services)
        {
            services.AddSingleton<IClientCommandQueue, ClientCommandQueue>()
                .AddSingleton<IServerCommandProcessor<ExampleServerCommand>, ExampleClientCommandProcessor>()
                .AddHostedService<ServerListener>()
                .AddHostedService<ServerListener>();

            return services;
        }
    }
}
