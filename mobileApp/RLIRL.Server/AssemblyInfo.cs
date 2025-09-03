using System.Runtime.CompilerServices;

// Make internal members visible to the test project
[assembly:InternalsVisibleTo("RLIRL.Server.Tests")]

// Make internal members visible to Moq's dynamic proxy generation
[assembly:InternalsVisibleTo("DynamicProxyGenAssembly2")]