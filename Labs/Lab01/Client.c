#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<unistd.h>
#include<arpa/inet.h>

#define PORT 8080
#define BUFFER_SIZE 1024

int main(){
    int sock;
    struct sockaddr_in server_address;
    char buffer[BUFFER_SIZE] = {0};
    const char *message = "Hello from Client!";

    //Socket creation
    sock = socket(AF_INET, SOCK_STREAM, 0);
    if(sock < 0){
        perror("Socket creation failed");
        exit(EXIT_FAILURE); 
    }

    //Server address setup
    server_address.sin_family = AF_INET;
    server_address.sin_port = htons(PORT);

    // Convert IPv4 and IPv6 addresses from text to binary form
    if(inet_pton(AF_INET, "127.0.0.1", &server_address.sin_addr) <= 0){
        perror("Invalid address/ Address not supported");
        exit(EXIT_FAILURE);
    }

    //Connect to server
    if(connect(sock, (struct sockaddr *)&server_address, sizeof(server_address)) < 0){
        perror("Connection failed");
        exit(EXIT_FAILURE); 
    }

    //Send data to server
    send(sock, message, strlen(message), 0);
    printf("Message sent to server: %s\n", message);

    //Receive response from server
    recv(sock, buffer, BUFFER_SIZE, 0);
    printf("Received from server: %s\n", buffer);

    //Close socket
    close(sock);

    return 0;
}