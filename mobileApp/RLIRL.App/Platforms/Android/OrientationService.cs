using Android.Content.PM;
using RLIRL.App.Helper;

namespace RLIRL.App.Platforms.Android;

public class OrientationService : IOrientationService
{
    public void Default() => Set(ScreenOrientation.Unspecified);

    public void Landscape() => Set(ScreenOrientation.Landscape);

    public void Portrait() => Set(ScreenOrientation.Portrait);

    void Set(ScreenOrientation o)
    {
        var a = Platform.CurrentActivity;
        if (a != null) a.RequestedOrientation = o;
    }
}
