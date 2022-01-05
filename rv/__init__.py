import sys
from .top import ADCTop
from .platform import ADCPlatform


def main():
    fwb = open("fw/fw.bin", "rb").read()
    fw = []
    for i in range(len(fwb)//4):
        fw.append(int.from_bytes(fwb[i*4:(i+1)*4], "little"))

    top = ADCTop(prom=fw, imem=1024, dmem=1024)

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
    elif sys.argv[1] == "build":
        plat = ADCPlatform()
        plat.build(
            top, "rv", "build/",
            synth_opts=["-abc9"],
            ecppack_opts=["--freq", "62.0", "--spimode", "qspi", "--compress"],
            nextpnr_opts=["--timing-allow-fail"])
    else:
        print("Unknown operation. Specify either 'sim' or 'build'.")
