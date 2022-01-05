from amaranth import Elaboratable, Module, Signal, Memory, Repl
from minerva.core import Minerva


class Top(Elaboratable):
    def __init__(self, prom, imem=1024, dmem=1024):
        self.prom = prom
        self.gpo = Signal(32)

        self.imem_depth = imem
        self.dmem_depth = dmem

    def elaborate(self, platform):
        m = Module()

        imem = Memory(width=32, depth=self.imem_depth, init=self.prom)
        dmem = Memory(width=32, depth=self.dmem_depth)

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
