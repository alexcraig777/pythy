// $ class rectangle
// $ init rectangle init_rectangle

// $ class box
// $ init box init_box

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
struct rectangle* init_rectangle(int length, int width);

// Gets the area of a rectangle
int get_area(struct rectangle* rectangle);

// Gets a string description of a rectangle
char* get_rect_description(struct rectangle* rectangle);

// Clean up a rectangle structure.
void clean_up_rectangle(struct rectangle* rectangle);


// Creates a new box structure
struct box* init_box(int length, int width, int height);

// Gets the volume of a box
int get_volume(struct box* box);

// Gets a string description of a box
char* get_box_description(struct box* box);

// Clean up a box structure.
void clean_up_box(struct box* box);
