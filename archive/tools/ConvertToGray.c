#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include <time.h>
#include <sys/time.h>
#include <tiffio.h>

#include "../pipeline/C_files/ViBe_common.h"

void free_TIFF(int frames, unsigned char **VIDEO)
{
    for (int i = 0; i < frames; i++)
    {
        free(VIDEO[i]);
    }

    free(VIDEO);
}

int main(int argc, char *argv[])
{
    if (argc != 4)
    {
        printf("Utilisation : %s <path> <#input_start> <#input_end>\n", argv[0]);
        return 1;
    }

    timer_reset();
    int start = atoi(argv[2]), end = atoi(argv[3]);
    char *fullpath = (char *)malloc(32 * sizeof(char));
    unsigned short counter = 0;

    for (unsigned short i = (unsigned short)start; i <= end; counter = (counter + 1) % 3)
    {
        int W, H, FRAMES;
        unsigned char **video;

        sprintf(fullpath, "%s/%hu-%hu.tif", argv[1], i, counter + 1);
        printf("%s\n", fullpath);

        load_TIFF(fullpath, &video, &W, &H, &FRAMES);

        save_TIFF(fullpath, video, W, H, FRAMES);
        printf("-- Save %s : %ld\n", fullpath, timer_get());

        free_TIFF(FRAMES, video);

        if (counter == 2)
            i++;
    }

    free(fullpath);
    return 0;
}