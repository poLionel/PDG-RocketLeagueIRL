namespace RLIRL.Business.Abstractions.Models
{
    public class CameraFeed
    {
        public int CarId { get; set; }
        public string Base64Jpeg { get; set; } = string.Empty;
    }
}
