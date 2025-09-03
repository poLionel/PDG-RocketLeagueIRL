using RLIRL.App.Helper;
using RLIRL.App.ViewModels;

namespace RLIRL.App.Views;

public partial class CameraViewerView : ContentView
{
    public CameraViewerView()
    {
        BindingContext = ServiceHelper.Get<CameraViewerViewModel>();
        InitializeComponent();
    }

    public CameraViewerViewModel ViewModel => (CameraViewerViewModel)BindingContext;
}