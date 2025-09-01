using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace RLIRL.App.Helper
{
    public interface IOrientationService
    {
        void Landscape();
        void Portrait();
        void Default();
    }
}
