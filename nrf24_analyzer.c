#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <string.h>
#include <sys/stat.h>
#include <unistd.h>

#define PIPE "fifo"
//#define PIPE "13M_2402_crc8_bin"

#define BIN_BUFFER_SIZE 4096
#define PACKET_SIZE 40
#define BIN_PACKET_SIZE PACKET_SIZE*8

//#define CRC16_COUNT 3
//#define CRC16_INITVECTOR {0xFFFF, 0x0000, 0x1D0F}
#define CRC16_COUNT 1
#define CRC16_INITVECTOR {0xFFFF}

#define POLY16 0x1021            //Polynome for crc16
#define POLY8 0x7                //Polynome for crc8
#define MIN_CRC_BIT 120            //Minimal size of the bit string for crc counting
#define ONLY_CRC_TO 8            //Set to 8 if want to find for bit string multiple to 8

char ADDRESS[24] = {"\x01\x00\x01\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x01"}; //a20009
char PREAMBLE[2][9] = {{"\x01\x00\x01\x00\x01\x00\x01\x00\x01"}, {"\x00\x01\x00\x01\x00\x01\x00\x01\x00"}}; // 9 bits because of first bit of address
//char PREAMBLE[2][13] = {{"\x01\x01\x01\x01\x01\x00\x01\x00\x01\x00\x01\x00\x01"}, {"\x01\x01\x01\x01\x00\x01\x00\x01\x00\x01\x00\x01\x00"}}; // 9 bits because of first bit of address, additional 4 bits - its initialization of the chip
char bin_data[BIN_BUFFER_SIZE*2];
char buffer[BIN_BUFFER_SIZE];
unsigned char data[PACKET_SIZE];

char* address;
int address_len;
char address_flag = 0;

unsigned short good_crc16;
unsigned short bad_crc16;
unsigned char bad_crc8;

unsigned long count = 0;

char CRC8_FIND = 0;                //Set to 1 if want to find CRC8
char CRC16_FIND = 1;             //Set to 1 if want to find CRC16

unsigned char byte_from_8bit(char* d){
    return d[0]<<7 | d[1]<<6 | d[2]<<5 | d[3]<<4 | d[4]<<3| d[5]<<2 | d[6]<<1 | d[7];
}

char from_ascii(char ascii){
    if (ascii >= '0' && ascii <= '9'){
        return (ascii - 0x30);
    }else if (ascii >= 'a' && ascii <= 'f'){
        return (ascii - 87);
    }else if (ascii >= 'A' && ascii <= 'F'){
        return (ascii - 55);
    }
    return 0xFF;
}

char* bit_form_hex(char* s, int length){
    int i, tmp;
    char* res = calloc(sizeof(char), length * 4);
    printf("%s\n", s);
    for (i = 0; i < length ; i++){
        tmp = from_ascii(s[i]);
        res[4*i] = (tmp & 8) >>3;
        res[4*i+1] = (tmp & 4)>>2;
        res[4*i+2] = (tmp & 2)>>1;
        res[4*i+3] = tmp & 1;
    }
    return res;
}

void find_address(char* d){
    int i = 0;
    //if (!memcmp(&d[i], ADDRESS, sizeof(ADDRESS))){
    if (!memcmp(&d[i], address, address_len)){
        printf("<# %ld> <find_address> Packet = ", count++);
        for (i = 0; i < PACKET_SIZE; i++)
            printf("%02x", byte_from_8bit(&d[i*8]));
        printf("\n");
        for (i=0; i < BIN_PACKET_SIZE; i++){
            printf("%d", d[i]==0x00 ? 0 : 1);
        }
        printf("\n");
    }
}

void update_bad_crc16(char ch){
    unsigned short i, xor_flag;
    if (bad_crc16 >> 15 ^ ch){
        xor_flag = 1;
    }
    else{
        xor_flag = 0;
    }
    bad_crc16 = bad_crc16 << 1;
    if (xor_flag){
        bad_crc16 = bad_crc16 ^ POLY16;
    }
}

void update_bad_crc8(char ch){
    unsigned short i, xor_flag;
    if (bad_crc8 >> 7 ^ ch){
        xor_flag = 1;
    }
    else{
        xor_flag = 0;
    }
    bad_crc8 = bad_crc8 << 1;
    if (xor_flag){
        bad_crc8 = bad_crc8 ^ POLY8;
    }
}

void find_crc(char* d){
    int i, j;
    bad_crc16 = 0xffff;
    for (i = 0; i < BIN_PACKET_SIZE; i++){
        update_bad_crc16(d[i]);
        update_bad_crc8(d[i]);
        if (CRC16_FIND && (bad_crc16  != 0x0000) && (i >= MIN_CRC_BIT-1) && ((bad_crc16 >> 8) == byte_from_8bit(&d[i+1])) && ((bad_crc16 & 0x00ff) == byte_from_8bit(&d[i+1+8])) ){
            if (((i+1) % ONLY_CRC_TO) == 0){
                printf("<# %ld> <find_crc 16> Packet = ", count++);
                for (j = 0; j < ((i+1)>>3) + sizeof(bad_crc16); j++)
                    printf("%02x", byte_from_8bit(&d[j*8]));
                printf(" (CRC16 = %4x, Length = %d)\n", bad_crc16, ((i+1)>>3) );
            }
        }
        if (CRC8_FIND && (bad_crc8  != 0x00) && (i >= MIN_CRC_BIT-1) && (bad_crc8 == byte_from_8bit(&d[i+1])) ){
            if (((i+1) % ONLY_CRC_TO) == 0){
                printf("<# %ld> <find_crc 8> Packet = ", count++);
                for (j = 0; j < ((i+1)>>3) + sizeof(bad_crc8); j++)
                    printf("%02x", byte_from_8bit(&d[j*8]));
                printf(" (CRC8 = %2x, Length = %d)\n", bad_crc8, ((i+1)>>3) );
            }
        }
    }
}

void find_crc16ccit(unsigned char* data_p, int length){
    unsigned char x[CRC16_COUNT];
    unsigned short crc16ccit[CRC16_COUNT] = CRC16_INITVECTOR;
    unsigned char* data = data_p;
    int pos = 0;
    int i, j, k;

    for (i = 0; i < CRC16_COUNT; i++){
        pos = 0;
        data = data_p;
        while (pos++ < length-2){
            x[i] = crc16ccit[i] >> 8 ^ *data_p;
            x[i] ^= x[i]>>4;
            data_p++;
            crc16ccit[i] = (crc16ccit[i] << 8) ^ ((unsigned short)(x[i] << 12)) ^ ((unsigned short)(x[i] << 5)) ^ ((unsigned short)x[i]);
            if (((crc16ccit[i] & 0xff00)>>8 == data_p[0]) && ((crc16ccit[i] & 0xff) == data_p[1]) && (pos > 5) && (crc16ccit[i] !=0x0000)){
                printf("Address + data = ");
                k = 0;
                for (k=0; k < pos; k++){
                    printf("%02x", data[k]);
                }
                printf(" CRC = %02x%02x ( CRC16CCIT_%d = %04x Lenght = %d )\n", data_p[0], data_p[1], i, crc16ccit[i], pos);
            }
        }
    }
}

void make_packet(char* d){
    int i = 0;
    for (i = 0; i < PACKET_SIZE; i++){
        data[i] = byte_from_8bit(&d[i*8]);
    }
    find_crc16ccit(data, PACKET_SIZE);
}

void parse_buffer(char* d){
    int i = 0;
    for (i; i < BIN_BUFFER_SIZE - BIN_PACKET_SIZE; i++){
//        if ((!memcmp(&d[i], PREAMBLE[1], sizeof(PREAMBLE[1]))) || (!memcmp(&data[i], PREAMBLE[0], sizeof(PREAMBLE[0])))) {
        if (!memcmp(&d[i], PREAMBLE[1], sizeof(PREAMBLE[1]))){
            if (address_flag)
                find_address(&d[i+8]);
            find_crc(&d[i+8]);
            //make_packet(&d[i+8]);
        }
        if (!memcmp(&d[i], PREAMBLE[0], sizeof(PREAMBLE[0]))){
            if (address_flag)
                find_address(&d[i+8]);
            find_crc(&d[i+8]);
        }
    }
}

int main(int argc, char *argv[]){
    int s;
    char* str;

    if (argc < 2){
        address_flag = 0;
        CRC8_FIND = 0;
        CRC16_FIND = 1;
    } else {
        str = argv[1];
        address = bit_form_hex(str, strlen(str));
        address_len = strlen(str) << 2;
        address_flag = 1;
        CRC16_FIND = 1;
    }

    int file=open(PIPE, O_RDONLY);
    if (file==-1) {
        perror("open error");
        exit(-1);
    }

    while ((s = read(file, bin_data, sizeof(bin_data))) > 0){
        parse_buffer(bin_data);
    }

return 0;
}
