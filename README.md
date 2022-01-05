# RISC-V Playground

```
cd fw; cargo objcopy --release -- -O binary fw.bin; cd ..
poetry run python -m rv sim
poetry run python -m rv build
ecpdap program build/rv.bit --freq 20000
```
