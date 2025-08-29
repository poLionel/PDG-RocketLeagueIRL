using RLIRL.App.ViewModels;

namespace RLIRL.App.Views
{
    public partial class MainPage : ContentPage
    {
        public MainPage()
        {
            InitializeComponent();
            BindingContext = Application.Current?.Handler.MauiContext?.Services.GetRequiredService<WifiSelectorViewModel>();
        }
    }
}
