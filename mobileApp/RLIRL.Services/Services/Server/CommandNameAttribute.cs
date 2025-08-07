namespace RLIRL.Services.Services.Server
{
    [AttributeUsage(AttributeTargets.Class, Inherited = false)]
    internal class CommandNameAttribute : Attribute
    {
        public string Name { get; }
        public CommandNameAttribute(string name) => Name = name;
    }
}
