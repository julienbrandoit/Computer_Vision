.SILENT:

all: main

NAME = ViBe
FOLDER = bin
FILES = ViBe_segmentation.c ViBe_common.c ViBe_model.c timer.c

LDFLAGS = -ltiff -O3 -Wall -Wextra -Werror -fopenmp

main:
	gcc -o $(FOLDER)/$(NAME) $(FILES) $(LDFLAGS)

clean:
	rm -f $(FOLDER)/$(NAME)

run:
	OMP_NESTED=TRUE ./$(FOLDER)/$(NAME) in out $(args)

custom:
	OMP_NESTED=TRUE ./$(FOLDER)/$(NAME) $(args)
		

.PHONY: all