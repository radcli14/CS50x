#include <cs50.h>
#include <stdio.h>

int request_owed(void);
int calculate_coins(int owed);

int main(void)
{
    int owed = request_owed();
    int coins = calculate_coins(owed);
    printf("%i\n", coins);
}

// Prompty the user for the amount of cash that is owed, in pennies
int request_owed(void)
{
    int owed;
    do
    {
        owed = get_int("How much? ");
    }
    while (owed < 0);
    return owed;
}

// Calculate many coins of US denomination are required to provide change
int calculate_coins(int owed)
{
    int coins = 0;
    while (owed > 0)
    {
        if (owed >= 25)
        {
            owed -= 25;
        }
        else if (owed >= 10)
        {
            owed -= 10;
        }
        else if (owed >= 5)
        {
            owed -= 5;
        }
        else if (owed >= 1)
        {
            owed -= 1;
        }
        else
        {
            break;
        }
        coins += 1;
    }
    return coins;
}
