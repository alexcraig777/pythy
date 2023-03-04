#include <stdlib.h>
#include <string.h>


int interface_add(int x, int y)
{
    return x + y;
}

int interface_get_len(char* string)
{
    int len;
    for (len = 0; string[len]; len++);
    return len;
}

char* interface_concatenate(char* s1, char* s2)
{
    char* rtn = malloc(strlen(s1) + strlen(s2) + 1);
    strcpy(rtn, s1);
    strcat(rtn, s2);
    return rtn;
}

void interface_free_ptr(char* ptr)
{
    free(ptr);
}
