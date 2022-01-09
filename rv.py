import sys
from amaranth import Elaboratable, Module, Signal, Memory, Repl
from amaranth.build import Resource, Pins, Attrs, Clock
from amaranth.vendor.lattice_ecp5 import LatticeECP5Platform
from minerva.core import Minerva


class Platform(LatticeECP5Platform):
    """
    A simple custom platform for my ECP5 PCB that has a 20MHz clock on
    pin P6 and an LED output on pin T4.

    For common boards you could use a platform from amaranth_boards instead.
    """
    device = "LFE5U-45F"
    package = "BG256"
    speed = "6"
    default_clk = "clk20"
    resources = [
        Resource("clk20", 0, Pins("P6", dir="i"), Clock(20e6), Attrs(IO_TYPE="LVCMOS25")),
        Resource("led", 0, Pins("T4", dir="o"), Attrs(IO_TYPE="LVCMOS33")),
    ]
    connectors = []


class Top(Elaboratable):
    """
    By convention 'Top' is the top-level module, which instantiates all other
    modules. In this case it contains all our logic and the only submodules
    are the Minerva CPU core and Amaranth memory ports.
    """
    def __init__(self, prom):
        # General purpose 32-bit output
        self.gpo = Signal(32)

        # Store parameters for use in elaborate
        self.prom = prom

    def elaborate(self, platform):
        """
        Construct the required logic. We instantiate some memories to connect
        to the CPU's instruction and data buses, preload the instruction
        memory with the firmware image we were constructed with, and wire
        the memories to the CPU.

        On the data base we only drive writes to data memory when the top
        nibble of the address ix 0x1, and we write to the GPO register if
        the top nibble is 0x2.
        """
        m = Module()

        # Instantiate memories for instructions and data.
        # Both are 32 bits by 1024 words (4KiB).
        # The instruction memory is read-only and inititalised to the firmware,
        # while the data memory is read-write and implicitly initialised to 0.
        imem = Memory(width=32, depth=1024, init=self.prom)
        dmem = Memory(width=32, depth=1024)

        imem_rp = m.submodules.imem_rp = imem.read_port()
        dmem_rp = m.submodules.dmem_rp = dmem.read_port(transparent=False)
        dmem_wp = m.submodules.dmem_wp = dmem.write_port(granularity=8)

        cpu = m.submodules.cpu = Minerva()

        dbus_sel = cpu.dbus.adr[-4:]
        with m.If((dbus_sel == 0x1) & cpu.dbus.we):
            # Write to data memory for addresses 0x1xxx_xxxx.
            m.d.comb += dmem_wp.en.eq(Repl(cpu.dbus.we, 4) & cpu.dbus.sel)
        with m.If((dbus_sel == 0x2) & cpu.dbus.we):
            # Write to GPO port for addresses 0x2xxx_xxxx.
            m.d.sync += self.gpo.eq(cpu.dbus.dat_w)

        # Wire instruction and data BRAMs to the CPU's Wishbone interfaces.
        m.d.comb += (
            imem_rp.addr.eq(cpu.ibus.adr),
            cpu.ibus.dat_r.eq(imem_rp.data),

            dmem_rp.addr.eq(cpu.dbus.adr),
            cpu.dbus.dat_r.eq(dmem_rp.data),

            dmem_wp.addr.eq(cpu.dbus.adr),
            dmem_wp.data.eq(cpu.dbus.dat_w),
        )

        m.d.sync += (
            # Acknowledge each request on the next cycle, by which time the
            # memory will have been read/written.
            cpu.ibus.ack.eq(cpu.ibus.cyc),
            cpu.dbus.ack.eq(cpu.dbus.cyc),
        )

        # If running on a real platform, connect the GPO to an LED.
        if platform is not None:
            led = platform.request("led")
            m.d.comb += led.o.eq(self.gpo[0])

        return m


def main():
    # Read firmware from file and pack into little-endian 32-bit words.
    fwb = open("fw/fw.bin", "rb").read()
    fw = []
    for i in range(len(fwb)//4):
        fw.append(int.from_bytes(fwb[i*4:(i+1)*4], "little"))

    # Instantiate top-level module with 4kB of address and data memory.
    top = Top(prom=fw)

    # If simulating, run the module for 1000 CPU cycles, writing the
    # simulation results to a VCD file we can view in gtkwave.
    if sys.argv[1] == "sim":
        def testbench():
            for step in range(1000):
                yield

        from amaranth.sim import Simulator
        sim = Simulator(top)
        sim.add_clock(1/20e6)
        sim.add_sync_process(testbench)
        with sim.write_vcd("rv.vcd"):
            sim.run()

    # If building, ask Amaranth to build using the default yosys/nextpnr
    # toolchain for ECP5, with some configuration options to speed up
    # loading the bitstream from QSPI flash.
    elif sys.argv[1] == "build":
        plat = Platform()
        plat.build(
            top, "rv", "build/",
            synth_opts=["-abc9"],
            ecppack_opts=["--freq", "62.0", "--spimode", "qspi", "--compress"],
            nextpnr_opts=["--timing-allow-fail"])

    else:
        print("Unknown operation. Specify either 'sim' or 'build'.")


if __name__ == "__main__":
    main()
