#include <arpa/inet.h>
#include <sys/wait.h>
#include <sys/resource.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <linux/termios.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <string.h>
#include <fcntl.h>
#include <ctype.h>
#include <netdb.h>
#include <sys/prctl.h>
#include <libgen.h>
#include <sys/time.h>
#include <time.h>
#include <linux/types.h>
#include <linux/if_ether.h>
#include <linux/filter.h>
#include <errno.h>
#include <strings.h>

int main( int argc, char* argv[]) {
struct sock_fprog filter;
struct sock_filter bpf_code[] = {
                { 0x28, 0, 0, 0x0000000c },
                { 0x15, 0, 27, 0x00000800 },
                { 0x30, 0, 0, 0x00000017 },
                { 0x15, 0, 5, 0x00000011 },
                { 0x28, 0, 0, 0x00000014 },
                { 0x45, 23, 0, 0x00001fff },
                { 0xb1, 0, 0, 0x0000000e },
                { 0x48, 0, 0, 0x00000016 },
                { 0x15, 19, 20, 0x00007255 },
                { 0x15, 0, 7, 0x00000001 },
                { 0x28, 0, 0, 0x00000014 },
                { 0x45, 17, 0, 0x00001fff },
                { 0xb1, 0, 0, 0x0000000e },
                { 0x48, 0, 0, 0x00000016 },
                { 0x15, 0, 14, 0x00007255 },
                { 0x50, 0, 0, 0x0000000e },
                { 0x15, 11, 12, 0x00000008 },
                { 0x15, 0, 11, 0x00000006 },
                { 0x28, 0, 0, 0x00000014 },
                { 0x45, 9, 0, 0x00001fff },
                { 0xb1, 0, 0, 0x0000000e },
                { 0x50, 0, 0, 0x0000001a },
                { 0x54, 0, 0, 0x000000f0 },
                { 0x74, 0, 0, 0x00000002 },
                { 0xc, 0, 0, 0x00000000 },
                { 0x7, 0, 0, 0x00000000 },
                { 0x48, 0, 0, 0x0000000e },
                { 0x15, 0, 1, 0x00005293 },
                { 0x6, 0, 0, 0x0000ffff },
                { 0x6, 0, 0, 0x00000000 },
        };

        filter.len = sizeof(bpf_code)/sizeof(bpf_code[0]);
        filter.filter = bpf_code;
int sock;
sock = socket(PF_PACKET, SOCK_RAW, htons(ETH_P_IP));
setsockopt(sock, SOL_SOCKET, SO_ATTACH_FILTER, &filter, sizeof(filter));


}
