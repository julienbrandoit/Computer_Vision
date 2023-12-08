#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#include <tiffio.h>

#define INDEX2D(i,j, w, h) ((j)*(w) + (i))
#define GETVALUE(i,j, tab, w, h) ((tab)[INDEX2D((i),(j), (w), (h))])

void load_TIFF(char *path, unsigned char ***VIDEO, int* W, int* H, int* FRAMES)
{
    int w, h, frames;

	TIFFSetWarningHandler(0);
    TIFF* tiff = TIFFOpen(path, "r");

    if (tiff == NULL) {
        fprintf(stderr, "Impossible d'ouvrir le fichier tiff\n");
        exit(1);
    }

    TIFFGetField(tiff, TIFFTAG_IMAGEWIDTH, &w);
    TIFFGetField(tiff, TIFFTAG_IMAGELENGTH, &h);

    frames = TIFFNumberOfDirectories(tiff);

    //printf("WIDTH : %d ; HEIGHT : %d ; NUMBER OF FRAMES : %d\n", w, h, frames);

    *VIDEO = (unsigned char**)malloc(frames * sizeof(unsigned char*));
    uint32_t* raster = (uint32_t*) _TIFFmalloc(w * h * sizeof(uint32_t));
    
    if (raster == NULL || *VIDEO == NULL)
    {
        fprintf(stderr, "Erreur d'allocation mémoire pour raster ou video\n");
        exit(1);
    }

    for (int f = 0; f < frames; f++)
    {
        TIFFSetDirectory(tiff, f);

        (*VIDEO)[f] = (unsigned char*) malloc(w * h * sizeof(unsigned char));

        if ((*VIDEO)[f] == NULL)
        {
            fprintf(stderr, "Erreur d'allocation mémoire pour VIDEO[%d]\n", f);
            exit(1);
        }

        if (TIFFReadRGBAImage(tiff, w, h, raster, 0)) {
            for(int i = 0; i < w * h; i++)
            {
                (*VIDEO)[f][i] = TIFFGetR(raster[i]);
            }
        } 
        else
        {
            fprintf(stderr, "Impossible de lire %d frame de la video\n", f);
            exit(1);
        }
    }
    _TIFFfree(raster);
    TIFFClose(tiff);

    if (W) {*W = w;}
    if (H) {*H = h;}
    if (FRAMES) {*FRAMES = frames;}
    
}

void save_TIFF(char *path, unsigned char **MASK, int W, int H, int frames)
{
    TIFF *tiff = TIFFOpen(path, "w");
    if (tiff == NULL)
    {
        fprintf(stderr, "Erreur pour ecrire le mask\n");
        exit(1);
    }

    unsigned char *row = (unsigned char *)malloc(W * sizeof(unsigned char));

    for (int f = 0; f < frames; f++)
    {
        TIFFSetDirectory(tiff, f);

        TIFFSetField(tiff, TIFFTAG_IMAGEWIDTH, W);
        TIFFSetField(tiff, TIFFTAG_IMAGELENGTH, H);
        TIFFSetField(tiff, TIFFTAG_SAMPLESPERPIXEL, 1);
        TIFFSetField(tiff, TIFFTAG_BITSPERSAMPLE, 8);
        TIFFSetField(tiff, TIFFTAG_ORIENTATION, ORIENTATION_TOPLEFT);
        TIFFSetField(tiff, TIFFTAG_PLANARCONFIG, PLANARCONFIG_CONTIG);

        for (int j = 0; j < H; j++)
        {
            int j_o = H - j - 1;
            for (int i = 0; i < W; i++)
            {
                row[i] = (unsigned char)GETVALUE(i, j_o, MASK[f], W, H);
            }

            TIFFWriteScanline(tiff, row, j, 0);
        }

        if (f != frames - 1)
        {
            TIFFWriteDirectory(tiff);
        }
    }

    free(row);

    TIFFClose(tiff);
}

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
    if (argc != 2)
    {
        printf("Utilisation : %s <path>\n", argv[0]);
        return 1;
    }

    int length = strlen(argv[1]) + 16;
    int start = 1, end = 14;
    char *fullpath = (char *)malloc(length * sizeof(char));
    unsigned short counter = 0;

    for (unsigned short i = (unsigned short)start; i <= end; counter = (counter + 1) % 3)
    {
        int W, H, FRAMES;
        unsigned char **video;

        snprintf(fullpath, length, "%s/%hu-%hu.tif", argv[1], i, counter + 1);
        printf("%s\n", fullpath);

        load_TIFF(fullpath, &video, &W, &H, &FRAMES);

        save_TIFF(fullpath, video, W, H, FRAMES);
        printf("-- Update %s\n", fullpath);

        free_TIFF(FRAMES, video);

        if (counter == 2)
            i++;
    }

    free(fullpath);
    return 0;
}