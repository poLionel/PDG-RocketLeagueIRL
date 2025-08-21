using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using RLIRL.Server.Abstractions;
using RLIRL.Server.Abstractions.Server;
using RLIRL.Server.Services;
using RLIRL.Server.Services.Server;

namespace RLIRL.Server
{
    public static class Bootstrapper
    {
        public static IServiceCollection RegisterServer(this IServiceCollection services, IConfiguration configuration)
        {
            services.Configure<ServerConfiguration>(configuration.GetSection(nameof(ServerConfiguration)));

            services.AddSingleton<IClientCommandQueue, ClientCommandQueue>()
                .AddTransient<IServerCommandSerializer, ServerCommandSerializer>()
                .AddSingleton<IWebSocketProvider, WebSocketProvider>()
                .AddSingleton<IServerCommandListener, ServerCommandListener>()
                .AddSingleton<IServerCommandSender, ServerCommandSender>();

            return services;
        }
    }
}
