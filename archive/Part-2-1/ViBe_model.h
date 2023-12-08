#ifndef VIBE_MODEL
#define VIBE_MODEL

/**
   \brief compute the background model of a video
   \param video the video from wich you want the background model
   \param SAMPLES return matrix that contains the samples for each pixels
   \param W the width of the frame
   \param H the height og the frame
   \param FRAMES the number of frame in the vide
   */
void get_model(unsigned char **video, unsigned char **samples, int W, int H, int FRAMES);

#endif