using RLIRL.App.Helper;
using RLIRL.App.ViewModels;

namespace RLIRL.App.Views;

public partial class GamePage : ContentPage
{
	double _joyRadius; // Base radius
	double _knobRadius = 32; // Knob radius

	// seuil pour activer le boost quand on tire le bouton Speed vers le haut
	const double BoostThreshold = 40; // pixels

    private readonly IOrientationService _orientation;

	public GamePage()
	{
		InitializeComponent();
		BindingContext = ServiceHelper.Services.GetService<GameViewModel>();

#if ANDROID
        _orientation = ServiceHelper.Get<IOrientationService>();
#endif

        // Calculate radius
        _joyRadius = 70;
	}

    void OnJoystickPanUpdated(object? sender, PanUpdatedEventArgs e)
    {
        if (BindingContext is not GameViewModel vm) return;

        switch (e.StatusType)
        {
            case GestureStatus.Started:
                // rien
                break;

            case GestureStatus.Running:
                // position du knob par rapport au centre (en pixels)
                var dx = e.TotalX;
                var dy = e.TotalY;

                // limite à l'intérieur du cercle
                var len = Math.Sqrt(dx * dx + dy * dy);
                var max = _joyRadius - _knobRadius; // marge pour rester dedans

                if (len > max && len > 0)
                {
                    var scale = max / len;
                    dx *= scale;
                    dy *= scale;
                }

                // place visuellement le knob
                AbsoluteLayout.SetLayoutBounds(JoyKnob, new Rect(0.5 + dx / (2 * _joyRadius), 0.5 + dy / (2 * _joyRadius), 64, 64));

                // vecteur normalisé (-1..1)
                var nx = (dx / max);
                var ny = (dy / max);

                // Inverser Y (haut = négatif en pixels, mais on veut +1 vers l'avant ?)
                ny = -ny;

                //vm.SetJoystick(nx, ny); // envoie/stocke l'input
                break;

            case GestureStatus.Completed:
            case GestureStatus.Canceled:
                // remet le knob au centre
                AbsoluteLayout.SetLayoutBounds(JoyKnob, new Rect(.5, .5, 64, 64));
                //vm.SetJoystick(0, 0);
                break;
        }

    }

    protected override void OnAppearing()
    {
        base.OnAppearing();

#if ANDROID
        _orientation?.Landscape();
#endif
    }

    protected override void OnDisappearing()
    {
#if ANDROID
        _orientation?.Default();
#endif
        base.OnDisappearing();
    }
}
