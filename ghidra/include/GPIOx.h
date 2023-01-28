typedef struct GPIOx GPIOx, *PGPIOx;

struct reg_pack_2b {

    int _0:2;
    int _1:2;
    int _2:2;
    int _3:2;
    int _4:2;
    int _5:2;
    int _6:2;
    int _7:2;
    int _8:2;
    int _9:2;
    int _10:2;
    int _11:2;
    int _12:2;
    int _13:2;
    int _14:2;
    int _15:2;
};

struct reg_pack_1b {

    int _0:1;
    int _1:1;
    int _2:1;
    int _3:1;
    int _4:1;
    int _5:1;
    int _6:1;
    int _7:1;
    int _8:1;
    int _9:1;
    int _10:1;
    int _11:1;
    int _12:1;
    int _13:1;
    int _14:1;
    int _15:1;
    int _reserved:16;
};

struct reg_halfpack_1b {

    short _0:1;
    short _1:1;
    short _2:1;
    short _3:1;
    short _4:1;
    short _5:1;
    short _6:1;
    short _7:1;
    short _8:1;
    short _9:1;
    short _10:1;
    short _11:1;
    short _12:1;
    short _13:1;
    short _14:1;
    short _15:1;
};

struct reg_fullpack_1b {
    struct reg_halfpack_1b BS;
    struct reg_halfpack_1b BR;
};

struct GPIOx {
    struct reg_pack_2b MODER;
    struct reg_pack_1b OTYPER;
    struct reg_pack_2b OSPEEDR;
    struct reg_pack_2b PUPDR;
    struct reg_pack_1b IDR;
    struct reg_pack_1b ODR;
    struct reg_fullpack_1b BSRR;
};

