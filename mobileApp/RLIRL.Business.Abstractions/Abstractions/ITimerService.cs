
namespace RLIRL.Business.Services
{
    public interface ITimerService
    {
        TimeSpan TimeLeft { get; set; }

        event EventHandler<TimeSpan>? TimeLeftChanged;
    }
}