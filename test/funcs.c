#include <stdlib.h>
#include <string.h>


char* str_rtn = NULL;


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
    char* rtn = realloc(str_rtn, strlen(s1) + strlen(s2) + 1);
    strcpy(rtn, s1);
    strcat(rtn, s2);
    return rtn;
}

__attribute__((destructor))
void destructor(void)
{
    free(str_rtn);
}
