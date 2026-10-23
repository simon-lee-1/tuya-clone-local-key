/*
 * SPDX-License-Identifier: MIT
 * Copyright (c) 2026 Simon Lee
 *
 * From the maintainer's Tuya extraction research, introduced 9 September 2026,
 * following the earlier memdump4.c prototype. See ../CREDITS.md for provenance
 * and the limits of the available source history.
 */
#define _XOPEN_SOURCE 700
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <inttypes.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define CHUNK_SIZE 65536U
#define MAX_SEARCH 4096U
#define MAX_CONTEXT 4096U
#define MAX_MAPPING (200ULL * 1024ULL * 1024ULL)

static void usage(FILE *stream, const char *program) {
    fprintf(stream,
            "Owner-authorised privileged process-memory scanner.\n"
            "Usage: %s PID SEARCH [--context N]\n"
            "Test only: %s --test-file PATH SEARCH [--context N]\n",
            program, program);
}

static int parse_size(const char *text, size_t maximum, size_t *value) {
    char *end = NULL;
    errno = 0;
    unsigned long parsed = strtoul(text, &end, 10);
    if (errno || !text[0] || !end || *end || parsed > maximum) return -1;
    *value = (size_t)parsed;
    return 0;
}

static int emit_match(const unsigned char *data, size_t length, size_t index,
                      size_t needle_len, size_t context, uint64_t base) {
    size_t start = index > context ? index - context : 0;
    size_t after = index + needle_len;
    size_t end = after + context < length ? after + context : length;
    printf("===MATCH=== address=0x%" PRIx64 " context=%zu\n", base + index, end - start);
    if (fwrite(data + start, 1, end - start, stdout) != end - start) return -1;
    fputc('\n', stdout);
    return 0;
}

static int scan_fd(int fd, uint64_t start, uint64_t end, const unsigned char *needle,
                   size_t needle_len, size_t context) {
    const size_t overlap = needle_len > 1 ? needle_len - 1 : 0;
    unsigned char *buffer = malloc(CHUNK_SIZE + overlap);
    if (!buffer) return -1;
    size_t carry = 0;
    uint64_t offset = start;
    int matches = 0;

    while (offset < end) {
        size_t wanted = CHUNK_SIZE;
        if (end - offset < wanted) wanted = (size_t)(end - offset);
        ssize_t got = pread(fd, buffer + carry, wanted, (off_t)offset);
        if (got < 0) {
            if (errno == EINTR) continue;
            offset += wanted;
            carry = 0;
            continue;
        }
        if (got == 0) break;
        size_t available = carry + (size_t)got;
        uint64_t base = offset - carry;
        for (size_t i = 0; i + needle_len <= available; ++i) {
            if (memcmp(buffer + i, needle, needle_len) == 0) {
                if (emit_match(buffer, available, i, needle_len, context, base) != 0) {
                    free(buffer);
                    return -1;
                }
                ++matches;
            }
        }
        carry = overlap < available ? overlap : available;
        if (carry) memmove(buffer, buffer + available - carry, carry);
        offset += (size_t)got;
    }
    free(buffer);
    return matches;
}

static int scan_test_file(const char *path, const unsigned char *needle, size_t needle_len,
                          size_t context) {
    int fd = open(path, O_RDONLY | O_CLOEXEC | O_NOFOLLOW);
    if (fd < 0) { perror("open test file"); return 1; }
    struct stat info;
    if (fstat(fd, &info) != 0 || !S_ISREG(info.st_mode)) {
        fprintf(stderr, "test path must be a regular file\n"); close(fd); return 1;
    }
    int result = scan_fd(fd, 0, (uint64_t)info.st_size, needle, needle_len, context);
    close(fd);
    return result < 0 ? 1 : 0;
}

static int scan_process(long pid, const unsigned char *needle, size_t needle_len, size_t context) {
    char maps_path[64], mem_path[64];
    snprintf(maps_path, sizeof(maps_path), "/proc/%ld/maps", pid);
    snprintf(mem_path, sizeof(mem_path), "/proc/%ld/mem", pid);
    FILE *maps = fopen(maps_path, "re");
    if (!maps) { perror("open maps"); return 1; }
    int mem = open(mem_path, O_RDONLY | O_CLOEXEC);
    if (mem < 0) { perror("open mem"); fclose(maps); return 1; }

    char line[1024];
    while (fgets(line, sizeof(line), maps)) {
        unsigned long long start = 0, end = 0;
        char perms[5] = {0};
        if (sscanf(line, "%llx-%llx %4s", &start, &end, perms) != 3) continue;
        if (perms[0] != 'r' || perms[3] != 'p' || end <= start || end - start > MAX_MAPPING) continue;
        fprintf(stderr, "scan mapping start=0x%llx length=%llu\n", start, end - start);
        if (scan_fd(mem, start, end, needle, needle_len, context) < 0) {
            fprintf(stderr, "scan failed for mapping start=0x%llx\n", start);
        }
    }
    close(mem);
    fclose(maps);
    return 0;
}

int main(int argc, char **argv) {
    if (argc == 2 && strcmp(argv[1], "--help") == 0) { usage(stdout, argv[0]); return 0; }
    if (argc < 3) { usage(stderr, argv[0]); return 2; }

    int test_mode = strcmp(argv[1], "--test-file") == 0;
    if ((test_mode && argc < 4) || (!test_mode && argc < 3)) { usage(stderr, argv[0]); return 2; }
    const char *target = test_mode ? argv[2] : argv[1];
    const char *search = test_mode ? argv[3] : argv[2];
    int option_index = test_mode ? 4 : 3;
    size_t context = 500;
    if (option_index < argc) {
        if (option_index + 2 != argc || strcmp(argv[option_index], "--context") != 0
            || parse_size(argv[option_index + 1], MAX_CONTEXT, &context) != 0) {
            usage(stderr, argv[0]); return 2;
        }
    }

    size_t needle_len = strlen(search);
    if (needle_len == 0 || needle_len > MAX_SEARCH) {
        fprintf(stderr, "search length must be 1..%u bytes\n", MAX_SEARCH); return 2;
    }
    if (test_mode) return scan_test_file(target, (const unsigned char *)search, needle_len, context);

    size_t pid_value = 0;
    if (parse_size(target, INT_MAX, &pid_value) != 0 || pid_value == 0) {
        fprintf(stderr, "PID must be numeric and positive\n"); return 2;
    }
    return scan_process((long)pid_value, (const unsigned char *)search, needle_len, context);
}
