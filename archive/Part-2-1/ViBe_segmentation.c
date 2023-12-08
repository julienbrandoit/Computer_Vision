#include <stdio.h>
#include <stdlib.h>
#include <tiffio.h>
#include <string.h>

#include <omp.h>
#include <semaphore.h>

#include "ViBe_common.h"
#include "ViBe_model.h"
#include "timer.h"

sem_t video_available;
sem_t buffer_available;

int nb_thread;

/**
   \brief print an error message and exit
   \param message the message to print */
static void handle_error(char *message)
{
    fprintf(stderr, "%s\n", message);
    exit(EXIT_FAILURE);
}

void create_matrix(unsigned char ***MATRIX, int row, int col, char *name)
{
    unsigned char **TAB = (unsigned char **)malloc(row * sizeof(unsigned char *));
    if (!TAB)
    {
        fprintf(stderr, "Erreur d'allocation mémoire pour %s\n", name);
        exit(1);
    }

    for (int i = 0; i < row; i++)
    {
        TAB[i] = (unsigned char *)malloc(col * sizeof(unsigned char));
        if (!TAB[i])
        {
            fprintf(stderr, "Erreur d'allocation mémoire pour mask[%d]\n", i);
            exit(1);
        }
    }

    *MATRIX = TAB;
}

void init_segmentation(char *path, int *W, int *H, int *FRAMES, unsigned char ***VIDEO, unsigned char ***MASK, unsigned char ***SAMPLES, unsigned char ***BUFFER, unsigned char ***BUFFER_SAMPLES)
{
    load_TIFF(path, VIDEO, W, H, FRAMES, 1);

    create_matrix(MASK, *FRAMES, (*W) * (*H), "mask");
    create_matrix(SAMPLES, (*W) * (*H), N_sample, "samples");

    if (BUFFER)
        create_matrix(BUFFER, *FRAMES, (*W) * (*H), "buffer");
    if (BUFFER_SAMPLES)
        create_matrix(BUFFER_SAMPLES, (*W) * (*H), N_sample, "buffer_samples");
}

void free_matrix(unsigned char **matrix, int size)
{
    for (int i = 0; i < size; i++)
        free(matrix[i]);

    free(matrix);
}

void free_segmentation(int w, int h, int frames, unsigned char **VIDEO, unsigned char **MASK, unsigned char **SAMPLES, unsigned char **BUFFER, unsigned char **BUFFER_SAMPLES)
{

    free_matrix(MASK, frames);
    free_matrix(VIDEO, frames);
    if (BUFFER)
        free_matrix(BUFFER, frames);

    free_matrix(SAMPLES, w*h);
    if (BUFFER_SAMPLES)
        free_matrix(BUFFER_SAMPLES, w*h);
}

/**
   \brief Determine wich pixels belong to the background
   \param im the frame
   \param SAMPLES A matrix of samples for each pixel
   \param w the width of the frame
   \param h the height og the frame
   \param MASK the output matrix
   */
void segmentation(unsigned char *im, unsigned char **SAMPLES, int w, int h, unsigned char **MASK)
{
    for (int j = 0; j < h; j++)
    {
        for (int i = 0; i < w; i++)
        {
            unsigned char p = (unsigned char)GETVALUE(i, j, im, w, h);
            unsigned char *sample = (unsigned char *)GETVALUE(i, j, SAMPLES, w, h);
            if (is_background(p, sample))
                SETVALUE(i, j, *MASK, w, h, 0);
            else
                SETVALUE(i, j, *MASK, w, h, 255);
        }
    }
}

/**
   \brief Allow to format a string to get a path
   \param path the output path
   \param length the max length of path
   \param folder the path to the folder where are the videos
   \param seq the sequence number of the video (seq-part.tif)
   \param part the part number of the video (seq-part.tif)
   */
void get_path(char *path[], int length, char *folder, int seq, int part)
{
    (void)snprintf(*path, length, "%s/%hu-%hu.tif", folder, (unsigned short)seq, (unsigned short)(part + 1));
}

/**
   \brief Update the value of seq and part to take the value of the next video
   \param seq the sequence number of the video
   \param part the part number of the video

   */
void update_seq_part(int *seq, int *part)
{
    *part = (*part + 1) % 3;

    if (*part == 0)
    {
        *seq += 1;
    }
}

void swap(unsigned char ***array1, unsigned char ***array2)
{
    unsigned char **tmp = *array1;
    *array1 = *array2;
    *array2 = tmp;
}

/**
   \brief Compute the BGS for each videos. This function work with parallelization
   \param path1 the folder in wich the videos are located
   \param path2 the folder in which the masks should go
   \param seq_start the initial sequence number
   \param nb_video the number of video
   */
void segmentation_process_parrallel(char *path1, char *path2, int seq_start, int nb_video)
{
    timer_reset();

    int length1 = strlen(path1) + 10;
    char *full_path1 = (char *)malloc(length1 * sizeof(char));
    int length2 = strlen(path2) + 10;
    char *full_path2 = (char *)malloc(length2 * sizeof(char));

    int seq1 = seq_start, part1 = 0;
    int seq2 = seq_start, part2 = 0;
    int W, H, FRAMES = 0;
    unsigned char **video, **samples, **mask, **buffer, **buffer_sample;

    get_path(&full_path1, length1, path1, seq1, part1);
    update_seq_part(&seq1, &part1);

    init_segmentation(full_path1, &W, &H, &FRAMES, &buffer, &mask, &samples, &video, &buffer_sample);

    get_model(buffer, buffer_sample, W, H, FRAMES);
    printf("-- Create model for sequence %d : %ld ms\n", seq1, timer_get());

    sem_post(&video_available);

    #pragma omp parallel num_threads(2)
    {
        if (omp_get_thread_num() == 0)
        {
            int input_video = 1;
            while (input_video < nb_video)
            {
                sem_wait(&buffer_available);

                get_path(&full_path1, length1, path1, seq1, part1);
                load_TIFF(full_path1, &buffer, NULL, NULL, NULL, 0);

                if (part1 == 0)
                {
                    get_model(buffer, buffer_sample, W, H, FRAMES);
                    printf("-- Create model for sequence %d : %ld ms\n", seq1, timer_get());
                }
                update_seq_part(&seq1, &part1);

                sem_post(&video_available);
                input_video += 1;
            }
        }

        else
        {
            int output_video = 0;
            while (output_video < nb_video)
            {
                sem_wait(&video_available);

                swap(&video, &buffer);
                if(part2 == 0)
                    swap(&samples, &buffer_sample);

                sem_post(&buffer_available);

                #pragma omp parallel for num_threads(nb_thread)
                for (int f = 0; f < FRAMES; f++)
                {
                    segmentation(video[f], samples, W, H, &mask[f]);
                }

                get_path(&full_path2, length2, path2, seq2, part2);
                save_TIFF(full_path2, mask, W, H, FRAMES);

                output_video += 1;
                long time = timer_get();
                printf("Segmentation video %d-%d : %ld ms | %lf fps\n", seq2, part2+1, time, 100.0/(double)time*1000.0);
                update_seq_part(&seq2, &part2);
            }
        }
    }

    free(full_path1);
    free(full_path2);
    free_segmentation(W, H, FRAMES, video, mask, samples, buffer, buffer_sample);

    printf("-- End of the programme\n");
}

/**
   \brief Compute the BGS for each videos. This function is sequential
   \param path1 the folder in wich the videos are located
   \param path2 the folder in which the masks should go
   \param seq_start the initial sequence number
   \param nb_video the number of video
   */
void segmentation_process_seq(char *path1, char *path2, int seq_start, int nb_video)
{
    timer_reset();

    int length1 = strlen(path1) + 10;
    char *full_path1 = (char *)malloc(length1 * sizeof(char));
    int length2 = strlen(path2) + 10;
    char *full_path2 = (char *)malloc(length2 * sizeof(char));

    int seq = seq_start, part = 0;
    int W, H, FRAMES = 0;
    unsigned char **video, **samples, **mask;

    get_path(&full_path1, length1, path1, seq, part);

    init_segmentation(full_path1, &W, &H, &FRAMES, &video, &mask, &samples, NULL, NULL);
    get_model(video, samples, W, H, FRAMES);
    printf("-- Create model for sequence %d : %ld ms\n", seq+1, timer_get());


    for (int i = 0; i < nb_video; i++)
    {
        for (int f = 0; f < FRAMES; f++)
        {
            segmentation(video[f], samples, W, H, &mask[f]);
        }

        long time = timer_get();
        printf("Segmentation video %d-%d : %ld ms | %lf fps\n", seq, part+1, time, 100.0/(double)time*1000.0);
        
        get_path(&full_path2, length2, path2, seq, part);
        update_seq_part(&seq, &part);

        save_TIFF(full_path2, mask, W, H, FRAMES);
        if (i < nb_video-1)
        {
            get_path(&full_path1, length1, path1, seq, part);
            load_TIFF(full_path1, &video, NULL, NULL, NULL, 0);

            if (part == 0)
                {
                    get_model(video, samples, W, H, FRAMES);
                    printf("-- Create model for sequence %d : %ld ms\n", seq, timer_get());
                }
        }
    }

    free(full_path1);
    free(full_path2);
    free_segmentation(W, H, FRAMES, video, mask, samples, NULL, NULL);

    printf("-- End of the programme\n");
}

int main(int argc, char *argv[])
{
    nb_thread = 1;
    if (argc < 5 || argc > 6)
    {
        printf("Utilisation : %s <input_folder> <output_folder> <seq_start> <nb_video> [nb_thread]\n", argv[0]);
        return 1;
    }

    if (argc == 6)
    {
        nb_thread = atoi(argv[5]);

        if (sem_init(&video_available, 0, 0))
            handle_error("Error initializing semaphore");

        if (sem_init(&buffer_available, 0, 0))
            handle_error("Error initializing semaphore");
    }

    char *input_file = argv[1];
    char *output_file = argv[2];
    int seq_start = atoi(argv[3]);
    int nb_video = atoi(argv[4]);

    if (nb_thread > 1)
        segmentation_process_parrallel(input_file, output_file, seq_start, nb_video);
    else
        segmentation_process_seq(input_file, output_file, seq_start, nb_video);


    sem_destroy(&video_available);
    sem_destroy(&buffer_available);
    return 0;
}
