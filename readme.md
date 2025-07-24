# PQB EQA: A Dataset for verifying visual data utilization in EQA models

<p align="center">
Miles Shelton, Nate Wingerd, Kritim K. Rijal, Ayush Garg,
Adelina Gutic, Brett Barnes, Catherine Finegan-Dollak
</p>

<br><br><br>
This is the repository for the dataset and dataset generator used in the paper "Grounded, or a Good Guesser? A Per-Question Balanced Dataset to Separate Blind from Grounded Models for Embodied Question Answering" 

This tool can be used to build environments in Minecraft from a collection of prebuilt corners dynamically. Currently it is capable of generating 891 unique environments.

## Bibtex
```bibtex
@inproceedings{shelton2025grounded,
    title={Grounded, or a Good Guesser? A Per-Question Balanced Dataset to Separate Blind from Grounded Models for Embodied Question Answering},
    author={Miles Shelton AND Nate Wingerd AND Kritim K. Rijal AND Ayush Garg AND Adelina Gutic AND Brett Barnes AND Catherine Finegan-Dollak},
  booktitle={The 63rd Annual Meeting of the Association for Computational Linguistics},
    year={2025},
    url={https://openreview.net/forum?id=RWLUZDFbiF}
}
```

## Just download the dataset

(link to the dataset folder)

## Building your own environments

### requirements:
- Python 3.11.9
- A Minecraft account (to access the save folder after generation)

### Input csv file:
To make your own environments using any of the biomes and structures we created, you'll need first make a csv file that shows what environments you would like and name the file ```qea_for_environment_generation.csv``` We attached a sample to show the formatting. 

We have many environment biomes/types, the full list of them is as follows: beach, cave, circus, city, desert, jungle, mansion, nether, plains, snow, and town. These are then split into 4 corners (nw, ne, sw, se), each with 3 variants. A valid environment has a biome, followed by nw#\_ne#\_sw#\_se# where # is any number 1-3. An example of this is "town nw3\_ne2\_sw1\_se1"

```qea_for_environment_generation.csv``` needs a header row, followed by rows containing one environment as described above.

## Running the environment generator

Once you have a valid ```qea_for_environment_generation.csv``` file, run ```generate_environments.py```. After this is done, the saves folder in this project will have a new folder titled "qea_environment" This is a valid Minecraft 1.16.5 save folder, and can be copied into the saves folder in Minecraft.