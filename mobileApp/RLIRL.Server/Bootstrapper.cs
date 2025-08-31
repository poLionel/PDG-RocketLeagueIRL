using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using RLIRL.Server.Abstractions.Abstractions;
using RLIRL.Server.Abstractions.ServerCommands;
using RLIRL.Server.Services;
using RLIRL.Server.Services.CommandProcessors;

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
                .AddSingleton<IServerResponseListener, ServerResponseListener>()
                .AddSingleton<IServerCommandSender, ServerCommandSender>()
                .AddSingleton<IServerConnectionStatusService, ServerConnectionStatusService>()
                .AddAutoMapper(cfg => { }, typeof(MapperProfile));

            services.RegisterResponseProcessors();

            return services;
        }

        private static IServiceCollection RegisterResponseProcessors(this IServiceCollection services)
        {
            services.AddSingleton<IServerResponseProcessor<FreeCarResponse>, FreeCarResponseProcessor>()
                .AddSingleton<IServerResponseProcessor<GetAccessibleCarFeedsResponse>, GetAccessibleCarFeedsResponseProcessor>()
                .AddSingleton<IServerResponseProcessor<GetCarStatusResponse>, GetCarStatusResponseProcessor>()
                .AddSingleton<IServerResponseProcessor<GetCarVideoFeedResponse>, GetCarVideoFeedResponseProcessor>()
                .AddSingleton<IServerResponseProcessor<GetFreeCarsResponse>, GetFreeCarsResponseProcessor>()
                .AddSingleton<IServerResponseProcessor<GetGameStatusResponse>, GetGameStatusResponseProcessor>()
                .AddSingleton<IServerResponseProcessor<GoalScoredResponse>, GoalScoredResponseProcessor>()
                .AddSingleton<IServerResponseProcessor<MoveCarResponse>, MoveCarResponseProcessor>()
                .AddSingleton<IServerResponseProcessor<SelectCarResponse>, SelectCarResponseProcessor>()
                .AddSingleton<IServerResponseProcessor<StartGameResponse>, StartGameResponseProcessor>()
                .AddSingleton<IServerResponseProcessor<StopGameResponse>, StopGameResponseProcessor>();

            return services;
        }
    }
}
