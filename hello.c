#include <cs50.h>
#include <stdio.h>

int main(void)
{
    string response = get_string("whats your name? ");
    printf("hello, %s\n", response);
}
