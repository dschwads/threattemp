#include <sys/ptrace.h>

int main()
{
    ptrace(PTRACE_TRACEME, 0, 0, 0);

    return 0;
}