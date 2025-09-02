namespace RLIRL.Server.Services
{
    internal class CameraFrame
    {
        public string? ImageData { get; set; }
        public double Timestamp { get; set; }
        public DateTime ReceivedAt { get; set; }
    }
}