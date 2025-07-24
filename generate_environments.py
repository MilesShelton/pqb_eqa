from construct_environments_from_csv import main as construct_environments
from add_teleport_commandblocks import main as add_teleport_commandblocks

# clone template save file, add environments from qea_for_environment_generation.csv
construct_environments()

# go into those environments, add teleport commandblocks
#   output is saves/env_with_teleports, usable Minecraft savefile
add_teleport_commandblocks()