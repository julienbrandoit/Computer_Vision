#include <stdio.h>
#include <stdlib.h>
#include <tiffio.h>

#include "ViBe_model.h"
#include "ViBe_common.h"
#include "timer.h"

int PHI = EARLY_PHI;

unsigned char get_random_neighbor(int i, int j, int w, int h, unsigned char* im)
{
    int x_min = -1;    int x_max = 1;    int y_min = -1;    int y_max = 1;
    if (i == 0)  {x_min = 0;}
    else if (i == w-1)    {x_max = 0;}
    if (j == 0)  {y_min = 0;}
    else if (j == h-1)    {y_max = 0;}
    int x_o = GETRAND(x_min, x_max);
    
    int y_o;
    if (x_o == 0)
        if (y_min == 0 || y_max == 0)
            y_o = y_min+y_max;
        else
            y_o = GETRAND(0,1) ? y_min : y_max;
    else
        y_o = GETRAND(y_min, y_max);

    return GETVALUE(i+x_o, j+y_o, im, w, h);
}

void init_construct(char* path,int* W, int* H, int* FRAMES, unsigned char ***VIDEO, unsigned char ***SAMPLES)
{
    load_TIFF(path, VIDEO, W, H, FRAMES, 1);
    
    *SAMPLES = (unsigned char**)malloc(*W * *H * sizeof(unsigned char*));
    if (*SAMPLES == NULL) {
        fprintf(stderr, "Erreur d'allocation mémoire pour samples\n");
        exit(1);
    }

    for(int i = 0; i < *W * *H; i++)
    {
        (*SAMPLES)[i] = (unsigned char*)malloc(N_sample * sizeof(unsigned char));
        if ((*SAMPLES)[i] == NULL) {
            fprintf(stderr, "Erreur d'allocation mémoire pour samples[%d]\n", i);
            exit(1);
        }
    }
}

void free_construct(int w, int h, int frames, unsigned char ***VIDEO, unsigned char ***SAMPLES)
{

    for (int i = 0; i < frames; i++)
    {
        free((*VIDEO)[i]);
    }  

    for (int i = 0; i < w*h; i++)
    {
        free((*SAMPLES)[i]);
    }

    free(*VIDEO);
    free(*SAMPLES);
}

void init_model(unsigned char* im, int w, int h, unsigned char **sample)
{
    for (int j = 0; j < h; j++)
        for (int i = 0; i < w; i++)
            for (int k = 0; k < N_sample; k++)
                (GETVALUE(i,j,sample,w,h))[k] = get_random_neighbor(i,j,w,h,im);
}

void update(unsigned char* im, unsigned char**SAMPLES, int w, int h)
{
    int phi = PHI;
    unsigned char **samples = SAMPLES;

    for (int j = 0; j < h; j++)
    {
        for (int i = 0; i < w; i++)
        {
            unsigned char p = (unsigned char) GETVALUE(i,j,im,w,h);
            unsigned char* sample = (unsigned char*) GETVALUE(i,j,samples,w,h);
            if (is_background(p,sample))
            {
                // Temporal update
                if (phi == 1 || GETRAND(1, phi) == 1)
                {
                    int update_sample = GETRAND(0, N_sample-1);
                    sample[update_sample] = p;
                }

                // Spacial diffusion
                if (phi == 1 || GETRAND(1, phi) == 1)
                {
                    int x_min = -1;    int x_max = 1;    int y_min = -1;    int y_max = 1;
                    if (i == 0)  {x_min = 0;}
                    else if (i == w-1)    {x_max = 0;}
                    if (j == 0)  {y_min = 0;}
                    else if (j == h-1)    {y_max = 0;}
                    int x_o = GETRAND(x_min, x_max);  
                    
                    int y_o;
                    if (x_o == 0)
                        if (y_min == 0 || y_max == 0)
                            y_o = y_min+y_max;
                        else
                            y_o = GETRAND(0,1) ? y_min : y_max;
                    else
                        y_o = GETRAND(y_min, y_max);

                    int update_sample = GETRAND(0, N_sample-1);
                    unsigned char* sample_n = (unsigned char*) GETVALUE(i+x_o,j+y_o,samples,w,h);
                    sample_n[update_sample] = p;
                }
            }
        }
    }
}

void export_background_model(char *path2, int W, int H, unsigned char **samples)
{
    FILE *file = fopen(path2, "wb");
    if (!file) {
        perror("Error opening file for writing");
        exit(1);
    }

    // Write width, height, and sample size to the file
    int N = N_sample;
    fwrite(&W, sizeof(int), 1, file);
    fwrite(&H, sizeof(int), 1, file);
    fwrite(&N, sizeof(int), 1, file);

    // Write the data
    for (int i = 0; i < W*H; i++) {
        fwrite(samples[i], sizeof(unsigned char), N_sample, file);
    }

    fclose(file);
}

void construct_background_model(char* path, char* path2)
{
    timer_reset();

    int W,H,FRAMES = 0;
    unsigned char **video, **samples;

    init_construct(path,&W, &H, &FRAMES, &video, &samples);
    printf("-- Construct background load: %ld\n", timer_get());

    init_model(video[0], W, H, samples);
    printf("-- Construct background init model: %ld\n", timer_get());

    for(int f = 0; f < FRAMES; f++)
    {
        if (f == INITFRAMES)
            PHI = LATE_PHI;
            
        update(video[f], samples, W, H);
    }
    printf("-- Construct background update : %ld\n", timer_get());

    export_background_model(path2, W, H, samples);
    printf("-- Construct background save the background model : %ld\n", timer_get());

    free_construct(W, H, FRAMES, &video, &samples);
    printf("-- ViBe free : %ld\n", timer_get());
}

void get_model(unsigned char ** video, unsigned char ** samples, int W, int H, int FRAMES)
{
    PHI = EARLY_PHI;
    init_model(video[0], W, H, samples);

    for(int f = 0; f < FRAMES; f++)
    {
        if (f == INITFRAMES)
            PHI = LATE_PHI;
            
        update(video[f], samples, W, H);
    }
}

int main2(int argc, char *argv[])
{
    if (argc != 3) {
        printf("Utilisation : %s <fichier_entree> <fichier_sortie_background_model>\n", argv[0]);
        return 1;
    }

    char *input_file = argv[1];   
    char *output_background = argv[2];

    construct_background_model(input_file, output_background);

    return 0;
}
