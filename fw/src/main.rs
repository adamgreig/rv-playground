#![no_std]
#![no_main]

// Must have some panic handler defined.
// This one just goes into an infinite loop on panic.
use panic_halt as _;

#[riscv_rt::entry]
fn main() -> ! {
    // Our custom hardware maps address 0x2000_0000 to the 32-bit GPO (general-purpose output)
    // register, of which the lowest bit will be connected to an LED. We'll just write down
    // the address and do volatile writes to it.
    let gpo = 0x2000_0000 as *mut u32;

    unsafe {
        loop {
            gpo.write_volatile(1);
            riscv::asm::delay(1_000_000);
            gpo.write_volatile(0);
            riscv::asm::delay(1_000_000);
        }
    }
}
