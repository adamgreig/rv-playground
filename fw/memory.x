MEMORY {
    RAM     : ORIGIN = 0x10000000, LENGTH = 4K
    FLASH   : ORIGIN = 0x00000000, LENGTH = 4K
}

REGION_ALIAS("REGION_TEXT", FLASH);
REGION_ALIAS("REGION_RODATA", FLASH);
REGION_ALIAS("REGION_DATA", RAM);
REGION_ALIAS("REGION_BSS", RAM);
REGION_ALIAS("REGION_HEAP", RAM);
REGION_ALIAS("REGION_STACK", RAM);
