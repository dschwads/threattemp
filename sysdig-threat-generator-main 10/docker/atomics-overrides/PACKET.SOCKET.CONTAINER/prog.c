#include <stdio.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <net/ethernet.h>

int main()
{
    int s = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL));
    if (s < 0)
    {
        perror("socket");
        return 1;
    }

    shutdown(s, SHUT_RDWR);

    return 0;
}
