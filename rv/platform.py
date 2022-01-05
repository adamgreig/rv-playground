from amaranth.vendor.lattice_ecp5 import LatticeECP5Platform
from amaranth.build import Resource, Pins, Attrs, Clock


class ADCPlatform(LatticeECP5Platform):
    device = "LFE5U-45F"
    package = "BG256"
    speed = "6"
    default_clk = "clk20"
    lvcmos33 = Attrs(IO_TYPE="LVCMOS33")
    lvcmos25 = Attrs(IO_TYPE="LVCMOS25")
    lvcmos25od = Attrs(IO_TYPE="LVCMOS25", OPENDRAIN="ON")
    resources = [
        Resource("clk20", 0, Pins("P6", dir="i"), Clock(20e6), lvcmos25),
        Resource("led", 0, Pins("T4", dir="o"), lvcmos33),
        Resource("la", 0, Pins("A2 B3", dir="io"), lvcmos33),
    ]
    connectors = []
