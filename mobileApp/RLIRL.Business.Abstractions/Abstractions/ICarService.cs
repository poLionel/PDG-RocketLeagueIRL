namespace RLIRL.Business.Abstractions.Abstractions
{
    public interface ICarService
    {
        int? CurrentCar { get; set; }
        IEnumerable<int> FreeCars { get; set; }

        event EventHandler<int?>? CurrentCarChanged;

        event EventHandler<IEnumerable<int>>? FreeCarsChanged;

        void UpdateCurrentCar(int? currentCar);
        void UpdateFreeCars(IEnumerable<int> freeCars);

        void ReleaseCar();
        void SelectCar(int carId);
    }
}