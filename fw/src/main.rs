#![no_std]
#![no_main]

use panic_halt as _;

fn delay(n: usize) {
    for _ in 0..n {
        unsafe { core::ptr::read_volatile(0 as *const u32) };
    }
}

#[riscv_rt::entry]
fn main() -> ! {
    let gpo = 0x2000_0000 as *mut u32;
    loop {
        unsafe { gpo.write_volatile(1) };
        delay(1_000_000);
        unsafe { gpo.write_volatile(0) };
        delay(1_000_000);
    }
}
