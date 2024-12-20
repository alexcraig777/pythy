#include "classes_basic.h"

#include <stdio.h>
#include <stdlib.h>


#define DESCRIPTION_LENGTH 128


char* str_rtn = NULL;


struct rectangle* init_rectangle(int length, int width)
{
    struct rectangle* r = malloc(sizeof(*r));
    r->length = length;
    r->width = width;
    return r;
}

int get_area(struct rectangle* r)
{
    return r->length * r->width;
}

char* get_rect_description(struct rectangle* r)
{
    if (str_rtn == NULL) {
        str_rtn = malloc(DESCRIPTION_LENGTH);
    }
    snprintf(str_rtn, DESCRIPTION_LENGTH,
             "This is a %dx%d rectangle!", r->length, r->width);
    return str_rtn;
}

void clean_up_rectangle(struct rectangle* r)
{
    free(r);
}


struct box* init_box(int length, int width, int height)
{
    struct box* b = malloc(sizeof(*b));
    b->length = length;
    b->width = width;
    b->height = height;
    return b;
}

int get_volume(struct box* b)
{
    return b->length * b->width * b->height;
}

char* get_box_description(struct box* b)
{
    if (str_rtn == NULL) {
        str_rtn = malloc(DESCRIPTION_LENGTH);
    }
    snprintf(str_rtn, DESCRIPTION_LENGTH,
             "This is a %dx%dx%d box!",
             b->length, b->width, b->height);
    return str_rtn;
}

void clean_up_box(struct box* b)
{
    free(b);
}


__attribute__((destructor)) void destructor(void)
{
    free(str_rtn);
    str_rtn = NULL;
}
