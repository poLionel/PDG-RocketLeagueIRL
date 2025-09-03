using System.Globalization;

namespace RLIRL.App.Converters
{
    public class EqualToParameterConverter : IValueConverter, IMultiValueConverter
    {
        public object TrueValue { get; set; } = true;
        public object FalseValue { get; set; } = false;

        public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            if (value == null && parameter == null)
                return TrueValue;

            if (value == null || parameter == null)
                return FalseValue;

            return value.Equals(parameter) ? TrueValue : FalseValue;
        }

        public object? Convert(object?[] values, Type targetType, object? parameter, CultureInfo culture)
        {
            if (values == null || values.Length != 2)
                return FalseValue;

            var value1 = values[0];
            var value2 = values[1];

            if (value1 == null && value2 == null)
                return TrueValue;

            if (value1 == null || value2 == null)
                return FalseValue;

            return value1.Equals(value2) ? TrueValue : FalseValue;
        }

        public object? ConvertBack(object? value, Type targetType, object? parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }

        public object?[] ConvertBack(object? value, Type[] targetTypes, object? parameter, CultureInfo culture)
        {
            throw new NotImplementedException();
        }
    }
}