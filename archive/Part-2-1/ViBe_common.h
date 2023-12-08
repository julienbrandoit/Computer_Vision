#ifndef VIBE_COMMON
#define VIBE_COMMON

#define INDEX2D(i,j, w, h) ((j)*(w) + (i))
#define GETVALUE(i,j, tab, w, h) ((tab)[INDEX2D((i),(j), (w), (h))])
#define SETVALUE(i,j, tab, w, h, value) ((tab)[INDEX2D((i),(j), (w), (h))] = (value))

#define GETRAND(min, max) ((rand() % ((max) - (min) + 1)) + (min))

#define N_sample 10
#define RADIUS 20
#define V_min 3
#define INITFRAMES 100
#define LATE_PHI 16
#define EARLY_PHI 1

/**
   \brief Get the values of a tiff file
   \param path the path to the tiff file
   \param VIDEO a pointer to the matrix that will contain pixel values
   \param W a pointer to the variable that will contain the width of the video
   \param H a pointer to the variable that will contain the height of the video
   \param FRAMES a pointer to the variable that will contain the number of frame of the video
   \param allocate a boolean value, if allocate != 0 then VIDEO is malloc else it is not
   */
void load_TIFF(char *path, unsigned char ***VIDEO, int* W, int* H, int* FRAMES, int allocate);

/**
   \brief Save a matrix of values as a tiff file
   \param path the path to the tiff file
   \param MASK the matrix to write
   \param W a pointer to the variable that will contain the width of the video
   \param H a pointer to the variable that will contain the height of the video
   \param FRAMES a pointer to the variable that will contain the number of frame of the video
   */
void save_TIFF(char *path, unsigned char **MASK, int W, int H, int FRAMES);

/**
   \brief Determine if a pixel is part of the background
   \param value the value of the pixel
   \param samples the samples corresponding to the pixel
   \return an integer: 1 if is part of the background else 0
   */
int is_background(int value, unsigned char* samples);

#endif