# RISC-V Playground

Currently this repository has a really bare-bones example of instantiating
the Minerva RISC-V soft-core CPU on an ECP5 FPGA and running a very simple
Rust firmware on it.

The interesting files are:

* [`main.rs`](fw/src/main.rs): the Rust firmware
* [`rv.py`](rv.py): the Amaranth gateware description

The Rust firmware must be built first:

```
cd fw
cargo objcopy --release -- -O binary fw.bin
cd ..
```

Then you can simulate the CPU's operation:

```
poetry run python -m rv sim
```

Use `gtkwave` to view the `rv.vcd` file and check out the various signals,
such as the program counter, the memory read address, or the value of the
GPO (general-purpose output) register that the Rust firmware updates.

Finally to build for actual hardware and program:

```
poetry run python -m rv build
ecpdap program build/rv.bit --freq 20000
```

For your own hardware you'll probably need to change pins in the `Platform`
class at the top of `rv.py` to match your own hardware.
