// $ wrapper increment_args * !interface_get_len !interface_concatenate
// $ wrapper double_rtn     * !interface_add

// Adds 2 integers
int interface_add(int x, int y);

// Finds the length of a string
int interface_get_len(char* string);

// Concatenates 2 strings
char* interface_concatenate(char* s1, char* s2);