#include <stdio.h>
#include <sys/mman.h>
#include <fcntl.h>
#include <sys/syscall.h>
#include <linux/userfaultfd.h>

#define UFFDIO_API 0xc018aa3f
#define UFFDIO_REGISTER 0xc020aa00

int main()
{
        int uffd;
        struct uffdio_api uf_api;
        struct uffdio_register uf_register;

        uffd = syscall(__NR_userfaultfd, O_CLOEXEC | O_NONBLOCK);
        uf_api.api = UFFD_API;
        uf_api.features = 0;

        if (ioctl(uffd, UFFDIO_API, &uf_api) == -1)
        {
                perror("error with the uffdio_api");
                exit(-1);
        }

        char *addr = mmap(NULL, 0x1000, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, 0, 0);
        if (addr == NULL)
        {
                perror("mmap error");
                exit(-1);
        }

        uf_register.range.start = addr;
        uf_register.range.len = 0x1000;
        uf_register.mode = UFFDIO_REGISTER_MODE_MISSING;

        if (ioctl(uffd, UFFDIO_REGISTER, &uf_register) == -1)
        {
                perror("error registering page for userfaultfd");
                exit(-1);
        }

        puts("Successfully registered userfaultfd page.");

        return 0;
}