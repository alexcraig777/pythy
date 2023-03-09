#include "classes_basic.h"

#include <stdio.h>
#include <stdlib.h>


#define DESCRIPTION_LENGTH 128

struct rectangle* interface_init_rectangle(int length, int width)
{
    struct rectangle* r = malloc(sizeof(*r));
    r->length = length;
    r->width = width;
    return r;
}

int interface_get_area(struct rectangle* r)
{
    return r->length * r->width;
}

char* interface_get_rect_description(struct rectangle* r)
{
    char* rtn = malloc(DESCRIPTION_LENGTH);
    snprintf(rtn, DESCRIPTION_LENGTH,
             "This is a %dx%d rectangle!", r->length, r->width);
    return rtn;
}

void interface_clean_up_rectangle(struct rectangle* r)
{
    free(r);
}


struct box* interface_init_box(int length, int width, int height)
{
    struct box* b = malloc(sizeof(*b));
    b->length = length;
    b->width = width;
    b->height = height;
    return b;
}

int interface_get_volume(struct box* b)
{
    return b->length * b->width * b->height;
}

char* interface_get_box_description(struct box* b)
{
    char* rtn = malloc(DESCRIPTION_LENGTH);
    snprintf(rtn, DESCRIPTION_LENGTH,
             "This is a %dx%dx%d box!",
             b->length, b->width, b->height);
    return rtn;
}

void interface_clean_up_box(struct box* b)
{
    free(b);
}
