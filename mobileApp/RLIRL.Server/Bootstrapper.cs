using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Services;

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
                .AddSingleton<IServerCommandSender, ServerCommandSender>()
                .AddSingleton<IServerConnectionStatusService, ServerConnectionStatusService>()
                .AddAutoMapper(cfg => { }, typeof(MapperProfile));

            return services;
        }
    }
}
