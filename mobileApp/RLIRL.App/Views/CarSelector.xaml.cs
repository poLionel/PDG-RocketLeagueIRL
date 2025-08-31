using RLIRL.App.ViewModels;
using RLIRL.App.Helper;

namespace RLIRL.App.Views;

public partial class CarSelector : ContentView
{
    public CarSelector()
    {
        InitializeComponent();
        BindingContext = ServiceHelper.Get<CarSelectorViewModel>(); ;
    }
}