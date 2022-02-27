#May 2021
#Executing functionality for neat ai to learn a game

import brutalist_bird
from boilerplate import neat_

@neat_.setup_and_run
def main(genomes, config):
    brutalist_bird.mainloop(genomes, config)

if __name__=="__main__":
    main("config-feedforward.txt")
