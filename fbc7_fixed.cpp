// FBC7 FIXED ENCODER — Bug-1 corrected
// Change: store old_i BEFORE advancing, so head[h] = old_i (correct LZ77)
// Also: encode category sequences (1 byte/category) OR raw bytes

#include <iostream>
#include <vector>
#include <stdint.h>
#include <string.h>
#include <fstream>

#define WINDOW_SIZE 65536
#define HASH_SIZE   32768

struct FBC7_Fixed {
    int32_t head[HASH_SIZE];
    int32_t chain[WINDOW_SIZE];
    int depth;

    FBC7_Fixed(int d) : depth(d) {
        memset(head,  -1, sizeof(head));
        memset(chain, -1, sizeof(chain));
    }

    void compress(const uint8_t* in, size_t size, uint8_t* out, size_t& out_size) {
        size_t op = 0;
        for (size_t i = 0; i + 8 < size; ) {
            uint32_t h = ((in[i] << 16) | (in[i+1] << 8) | in[i+2]) * 0x1e35a7bd;
            h = (h ^ (h >> 15)) & (HASH_SIZE - 1);

            int best_len = 0;
            int32_t best_dist = -1;
            int32_t prev = head[h];
            int count = 0;
            while (prev != -1 && (int)(i - prev) < WINDOW_SIZE && count < depth) {
                int len = 0;
                while (len < 64 && (i + len) < size && in[prev + len] == in[i + len]) len++;
                if (len > best_len) { best_len = len; best_dist = i - prev; }
                prev = chain[prev & (WINDOW_SIZE - 1)];
                count++;
            }

            size_t old_i = i;                         // ← BUG-1 FIX: save position BEFORE advance
            if (best_len >= 4) {
                out[op++] = 0x80 | (best_len & 0x7F);
                *(uint16_t*)(out + op) = (uint16_t)best_dist;
                op += 2;
                i += best_len;
            } else {
                out[op++] = in[i++];
            }
            chain[old_i & (WINDOW_SIZE - 1)] = head[h]; // ← use old_i
            head[h] = old_i;                             // ← use old_i
        }
        out_size = op;
    }
};

// Decoder (paired with fixed encoder)
struct FBC7_Decoder {
    void decompress(const uint8_t* in, size_t in_size, uint8_t* out, size_t& out_size) {
        size_t ip = 0, op = 0;
        while (ip < in_size) {
            uint8_t b = in[ip];
            if (b & 0x80) {
                if (ip + 2 >= in_size) break;
                int len  = b & 0x7F;
                int dist = *(uint16_t*)(in + ip + 1);
                ip += 3;
                if (dist == 0 || (int)op < dist) break;
                for (int k = 0; k < len; k++)
                    out[op] = out[op - dist], op++;
            } else {
                out[op++] = in[ip++];
            }
        }
        out_size = op;
    }
};

int main(int argc, char* argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Usage: fbc7_fixed <depth> <infile> <outfile> [--decode]\n");
        return 1;
    }
    int depth = atoi(argv[1]);
    bool decode = (argc >= 5 && std::string(argv[4]) == "--decode");

    FILE* f = fopen(argv[2], "rb");
    fseek(f, 0, SEEK_END); size_t sz = ftell(f); fseek(f, 0, SEEK_SET);
    uint8_t* in_buf = (uint8_t*)malloc(sz);
    fread(in_buf, 1, sz, f); fclose(f);

    uint8_t* out_buf = (uint8_t*)malloc(sz * 3);
    size_t out_size = 0;

    if (!decode) {
        FBC7_Fixed enc(depth);
        enc.compress(in_buf, sz, out_buf, out_size);
    } else {
        FBC7_Decoder dec;
        dec.decompress(in_buf, sz, out_buf, out_size);
    }

    FILE* g = fopen(argv[3], "wb");
    fwrite(out_buf, 1, out_size, g); fclose(g);
    fprintf(stderr, "in=%zu out=%zu ratio=%.3fx\n", sz, out_size,
            (out_size > 0) ? (double)sz/out_size : 0.0);
    free(in_buf); free(out_buf);
    return 0;
}
