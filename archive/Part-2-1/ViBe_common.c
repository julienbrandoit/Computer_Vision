#include <stdio.h>
#include <stdlib.h>
#include <tiffio.h>
#include <stdint.h>

#include "ViBe_common.h"

void load_TIFF(char *path, unsigned char ***VIDEO, int* W, int* H, int* FRAMES, int allocate)
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

    if  (allocate)
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

        if (allocate)
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

int is_background(int value, unsigned char* sample_tab)
{
    int c = V_min;
    for (int i = 0; i < N_sample; i++)
    {
        if (abs(value - sample_tab[i]) < RADIUS)
        {
            c--;

            if (c == 0)
            {
                return 1;
            }
        }
    }

    return 0;
}
