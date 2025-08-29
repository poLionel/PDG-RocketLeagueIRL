using Android.Content.PM;
using RLIRL.App.Helper;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RLIRL.App;

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
