// $ class rectangle
// $ init rectangle interface_init_rectangle

// $ class box
// $ init box interface_init_box

// $ define struct rectangle* -> void*
// $ define struct box* -> void*


struct rectangle {
    int length;
    int width;
};

struct box {
    int length;
    int width;
    int height;
};


// Creates a new rectangle structure
struct rectangle* interface_init_rectangle(int length, int width);

// Gets the area of a rectangle
int interface_get_area(struct rectangle* r);

// Gets a string description of a rectangle
char* interface_get_rect_description(struct rectangle* r);

// Clean up a rectangle structure.
void interface_clean_up_rectangle(struct rectangle* r);


// Creates a new box structure
struct box* interface_init_box(int length, int width, int height);

// Gets the volume of a box
int interface_get_volume(struct box* b);

// Gets a string description of a box
char* interface_get_box_description(struct box* b);

// Clean up a box structure.
void interface_clean_up_box(struct box* b);
