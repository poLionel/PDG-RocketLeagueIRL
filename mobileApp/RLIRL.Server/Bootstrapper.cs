using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.Server;
using RLIRL.Server.Services;
using RLIRL.Server.Services.Server;
using RLIRL.Server.Services.ServerCommands;
using RLIRL.Server.Services.ServerCommandsProcessors;

namespace RLIRL.Server
{
    public static class Bootstrapper
    {
        public static IServiceCollection RegisterServer(this IServiceCollection services, IConfiguration configuration)
        {
            services.Configure<ServerConfiguration>(configuration.GetSection(nameof(ServerConfiguration)));

            services.AddSingleton<IClientCommandQueue, ClientCommandQueue>()
                .AddSingleton<IServerCommandProcessor<GameStatusServerCommand>, GameStatusCommandProcessor>()
                .AddSingleton<IWebSocketProvider, WebSocketProvider>()
                .AddHostedService<ServerCommandListener>()
                .AddHostedService<ServerCommandSender>();

            return services;
        }
    }
}
