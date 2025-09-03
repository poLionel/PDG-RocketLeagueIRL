namespace RLIRL.App.Helper
{
    /// <summary>
    /// Helper to resolve services from the .NET MAUI Dependency Injection container.
    /// Used when a page/view is created by shell (constructor without parameter) to obtain
    /// ViewModel.
    /// </summary>
    public static class ServiceHelper
    {
        /// <summary>
        /// Gets the application's service provider from the current MAUI context.
        /// </summary>
        public static IServiceProvider Services => Application.Current?.Handler?.MauiContext?.Services ??
            throw new InvalidOperationException("MAUI services not ready");

        /// <summary>
        /// Resolves a service of type <typeparamref name="T"/> from the DI container.
        /// Throws an exception if the service is not registered.
        /// </summary>
        /// <typeparam name="T">Service type to resolve.</typeparam>
        /// <returns>The resolved service instance.</returns>
        public static T Get<T>() where T : notnull => Services.GetRequiredService<T>();
    }
}
