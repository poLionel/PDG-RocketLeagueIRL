namespace RLIRL.Server.Abstractions.Attributes
{
    [AttributeUsage(AttributeTargets.Class, Inherited = false)]
    public class CommandNameAttribute : Attribute
    {
        public string Name { get; }
        public CommandNameAttribute(string name) => Name = name;
    }
}