from amaranth import Elaboratable, Module, Signal, Memory, Repl
from minerva.core import Minerva


class ADCTop(Elaboratable):
    def __init__(self, prom, imem=4096, dmem=4096):
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

        dmem_we = Signal(4)
        dbus_sel = cpu.dbus.adr[-4:]
        with m.If(dbus_sel == 0x1):
            m.d.comb += dmem_we.eq(Repl(cpu.dbus.we, 4) & cpu.dbus.sel)
        with m.Else():
            m.d.comb += dmem_we.eq(0)
        with m.If((dbus_sel == 0x2) & cpu.dbus.we):
            m.d.sync += self.gpo.eq(cpu.dbus.dat_w)

        m.d.comb += (
            imem_rp.addr.eq(cpu.ibus.adr),
            cpu.ibus.dat_r.eq(imem_rp.data),

            dmem_rp.addr.eq(cpu.dbus.adr),
            cpu.dbus.dat_r.eq(dmem_rp.data),

            dmem_wp.addr.eq(cpu.dbus.adr),
            dmem_wp.data.eq(cpu.dbus.dat_w),
            dmem_wp.en.eq(dmem_we),
        )

        m.d.sync += (
            cpu.ibus.ack.eq(cpu.ibus.cyc),
            cpu.dbus.ack.eq(cpu.dbus.cyc),
        )

        if platform is not None:
            led = platform.request("led")
            m.d.comb += led.o.eq(self.gpo[0])

        return m
