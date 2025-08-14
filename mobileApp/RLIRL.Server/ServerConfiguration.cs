namespace RLIRL.Server
{
    public class ServerConfiguration
    {
        public string? Host { get; set; }
        public short Port { get; set; }
        public bool IsHostGateway { get; set; }
        public bool Secure { get; set; }
        public int MaxPacketSize { get; set; } = 1024 * 1024;
    }
}
