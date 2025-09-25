#include <cs50.h>
#include <stdio.h>

void print_row(int n, int m);

int main(void)
{
    int m;
    do
    {
        m = get_int("How many rows? ");
    }
    while (m < 1);

    for (int i = 0; i < m; i++)
    {
        print_row(i, m);
    }
}

// Prints a row, where n is the row index, and m is the number of rows
void print_row(int n, int m)
{
    for (int j = 0; j < m; j++)
    {
        if (j < m - n - 1)
        {
            printf(" ");
        }
        else
        {
            printf("#");
        }
    }
    printf("\n");
}
