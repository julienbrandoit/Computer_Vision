import generate_model.BGS_model
import pipeline

import param

if __name__ == "__main__":
        
    s, n = 1, 1
    generate_model.BGS_model.generate_model(s,n)
    tmp = pipeline.start(s, n)

    exit()
