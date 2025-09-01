using RLIRL.App.Helper;
using RLIRL.App.ViewModels;

namespace RLIRL.App.Views;

public partial class GamePage : ContentPage
{
	double _joyRadius = 70; // Base radius
	double _knobRadius = 32; // Knob radius

    const int Step = 10; // Range to update the steering value
    const int IntervalMs = 80; // Interval to update the steering value

    int _lastSent = int.MinValue;
    DateTime _lastAt = DateTime.MinValue;
    CancellationTokenSource? _steerCts;

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
	}

    static int Quantize(double v, int step) => (int)Math.Clamp(step * Math.Round(v / step), -100, 100);

    void SendSteeringThrottled(int raw)
    {
        if (BindingContext is not GameViewModel vm) return;

        var v = Quantize(raw, Step);
        var now = DateTime.UtcNow;
        var elapsed = (now - _lastAt).TotalMilliseconds;

        void Emit(int val){
            _lastSent = val;
            _lastAt = DateTime.UtcNow;
            if (vm.SetSteeringCommand.CanExecute(val))
                vm.SetSteeringCommand.Execute(val);
        }

        if (_lastSent == v && elapsed < IntervalMs) return;

        if(elapsed > IntervalMs)
        {
            Emit(v);
        }
        else
        {
            _steerCts?.Cancel();
            _steerCts = new CancellationTokenSource();
            var delay = IntervalMs - (int)elapsed;
            _ = Task.Run(async () =>
            {
                try { await Task.Delay(delay, _steerCts.Token); }
                catch { return; }
                MainThread.BeginInvokeOnMainThread(() => Emit(v));
            });
        }
    }

    void OnJoystickPanUpdated(object? sender, PanUpdatedEventArgs e)
    {
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
                //ny = -ny;
                var steering = (int)(nx * 100.0);
                SendSteeringThrottled(steering);
                
                break;

            case GestureStatus.Completed:
            case GestureStatus.Canceled:
                // remet le knob au centre
                AbsoluteLayout.SetLayoutBounds(JoyKnob, new Rect(.5, .5, 64, 64));
                _steerCts?.Cancel();
                SendSteeringThrottled(0);
                break;
        }
    }

    void OnSpeedPanUpdated(object? sender, PanUpdatedEventArgs e)
    {
        if (BindingContext is not GameViewModel vm) return;

        if (e.StatusType == GestureStatus.Running)
        {
            // si on glisse vers le HAUT au-delà du seuil -> boost
            var dragUp = -e.TotalY; // haut = valeurs positives
            //vm.SetBoost(dragUp > BoostThreshold);
        }
        else if (e.StatusType is GestureStatus.Completed or GestureStatus.Canceled)
        {
            //vm.SetBoost(false);
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
