"""
HIDPP features class
"""

from .x0000 import X0000
from .x0001 import X0001
from .x0003 import X0003
from .x0005 import X0005
from .x00C2 import X00C2
from .x00D0 import X00D0
from .x18e9 import X18E9
from .x2202 import X2202
from .x8129 import X8129

from .x1000 import X1000
from .x1001 import X1001
from .x1004 import X1004
from .x1e00 import X1E00
from .x1e30 import X1E30
from .x2111 import X2111
from .x6100 import X6100
from .x1e02 import X1E02
from .x1602 import X1602
from .x1876 import X1876
from .x1890 import X1890
from .x1891 import X1891
from .x1e22 import X1E22
from .x8100 import X8100
from .x8128 import X8128
from .x3617_legacy import X3617
from .xF008 import XF008
from .x8081 import X8081
from .x920B import X920B
from .x1B08 import X1B08
from .x9205 import X9205
from .x9203 import X9203
from .x9201 import X9201
from .x9209 import X9209
from .x92d1 import X92D1

class Features:
    """
    hidpp features functions definition

    """

    def __init__(self, hidpp):
        self.x0000 = X0000(hidpp)
        self.x0001 = X0001(hidpp)
        self.x0003 = X0003(hidpp)
        self.x0005 = X0005(hidpp)
        self.x00C2 = X00C2(hidpp)
        self.x00D0 = X00D0(hidpp)
        self.x1000 = X1000(hidpp)
        self.x1001 = X1001(hidpp)
        self.x1004 = X1004(hidpp)
        self.x1602 = X1602(hidpp)
        self.x1876 = X1876(hidpp)
        self.x1890 = X1890(hidpp)
        self.x1891 = X1891(hidpp)
        self.x18E9 = X18E9(hidpp)
        self.x1E00 = X1E00(hidpp)
        self.x1E30 = X1E30(hidpp)
        self.x1E22 = X1E22(hidpp)
        self.x1E02 = X1E02(hidpp)
        self.x2111 = X2111(hidpp)
        self.x2202 = X2202(hidpp)
        self.x6100 = X6100(hidpp)
        self.x8100 = X8100(hidpp)
        self.x8129 = X8129(hidpp)
        self.x8128 = X8128(hidpp)
        self.x3617 = X3617(hidpp) # to be removed (new name is xF008)
        self.xf008 = XF008(hidpp)
        self.x8081 = X8081(hidpp)
        self.x920b = X920B(hidpp)
        self.x1b08 = X1B08(hidpp)
        self.x9205 = X9205(hidpp)
        self.x9201 = X9201(hidpp)
        self.x9203 = X9203(hidpp)
        self.x9209 = X9209(hidpp)
        self.x92D1 = X92D1(hidpp)
