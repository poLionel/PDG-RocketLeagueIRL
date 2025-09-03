using RLIRL.App.Helper;
using RLIRL.App.Models;
using RLIRL.App.ViewModels;

namespace RLIRL.App.Views;

public partial class GameAdminPage : ContentPage
{
    public GameAdminPage()
    {
        BindingContext = ServiceHelper.Get<GameAdminViewModel>();
        InitializeComponent();
    }

    protected override void OnAppearing()
    {
        base.OnAppearing();

        if (BindingContext is not GameAdminViewModel viewModel) return;

        viewModel.Initialize();
    }

    private void FeedCollectionViewSelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (BindingContext is not GameAdminViewModel viewModel) return;

        var selectedId = e.CurrentSelection.FirstOrDefault() as CameraFeedItem;

        if (viewModel.SelectCameraFeedCommand.CanExecute(selectedId))
        {
            viewModel.SelectCameraFeedCommand.Execute(selectedId);
        }
    }
}