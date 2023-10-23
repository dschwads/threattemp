#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/socket.h>

// ./kmsd <hostname> <port>

int main(int argc, char **argv)
{
    int s, fd;
    struct sockaddr_in serv;
    struct hostent *host_entry;

    if (argc != 3) exit(1);

    host_entry = gethostbyname(argv[1]);
    if (host_entry == NULL)
    {
        perror("gethostbyname");
        exit(1);
    }

    s = socket(AF_INET, SOCK_STREAM, 0);
    if (s < 0)
    {
        perror("socket");
        exit(1);
    }

    serv.sin_family = AF_INET;
    serv.sin_port = htons(atoi(argv[2]));
    serv.sin_addr = *((struct in_addr *)host_entry->h_addr);

    fd = connect(s, (struct sockaddr *)&serv, sizeof(serv));
    if (fd < 0)
    {
        perror("connect");
        close(s);
        exit(1);
    }

    close(fd);
    close(s);

    return 0;
}