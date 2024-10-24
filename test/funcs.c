#include <stdlib.h>
#include <string.h>


char* str_rtn = NULL;


int add(int x, int y)
{
    return x + y;
}

int get_len(char* string)
{
    int len;
    for (len = 0; string[len]; len++);
    return len;
}

char* concatenate(char* s1, char* s2)
{
    str_rtn = realloc(str_rtn, strlen(s1) + strlen(s2) + 1);
    strcpy(str_rtn, s1);
    strcat(str_rtn, s2);
    return str_rtn;
}

__attribute__((destructor))
void destructor(void)
{
    free(str_rtn);
    // It's important to set the global to NULL after we free it.
    // This is because we call the destructor manually (in ctypes mode)
    // when we try to unload the library, and then the OS calls it again
    // when it's actually trying to unload the .so when the process
    // exits. If we don't set it to NULL, then it will be double freed.
    str_rtn = NULL;
}
