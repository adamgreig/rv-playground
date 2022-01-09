#![no_std]
#![no_main]

// Must have some panic handler defined.
// This one just goes into an infinite loop on panic.
use panic_halt as _;

// Simple delay function that delays for some multiple of n clock cycles.
fn delay(n: usize) {
    for _ in 0..n {
        // There's no "nop" in the risc-v crate, so just do a dummy volatile
        // memory read instead, which the compile may not elide.
        unsafe { core::ptr::read_volatile(0 as *const u32) };
    }
}

#[riscv_rt::entry]
fn main() -> ! {
    // Our custom hardware maps address 0x2000_0000 to the 32-bit GPO (general-purpose output)
    // register, of which the lowest bit will be connected to an LED. We'll just write down
    // the address and do volatile writes to it.
    let gpo = 0x2000_0000 as *mut u32;

    loop {
        unsafe { gpo.write_volatile(1) };
        delay(1_000_000);
        unsafe { gpo.write_volatile(0) };
        delay(1_000_000);
    }
}
