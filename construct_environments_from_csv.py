import os
import sys
import subprocess
import csv

# if user doesn't have the correct packages installed, install

requirements = [ # [import name, pip source]
    ["amulet","amulet-core"],
    ["nbt","nbt"],
    ["tqdm","tqdm"],
    ["json","json"]
]

for requirement in requirements:
    try:
        __import__(requirement[0])
    except:
        subprocess.check_call([sys.executable, "-m", "pip", "install", requirement[1]])

import json

if os.path.exists("minecraftinstance.json"):
    # update minecraftinstance.json to have the correct world file path (curseforge issue)

    with open("minecraftinstance.json","r") as instance:
        minecraft_info = json.loads(instance.read())
        print(os.path.abspath(""))
        minecraft_info["installPath"] = str(os.path.abspath(""))+"\\"

    with open("minecraftinstance.json","w") as instance:
        instance.write(json.dumps(minecraft_info))

# from pyanvil import world as py_a_world
from random import randint
from tqdm import tqdm
from duplicate_save_file import setup_new_environment
import nbt

import amulet
from amulet_nbt import StringTag
game_version = ("java",(1,16,5))

from location_parser import get_region_and_chunk_from_pos

structure_folder = "aqua_structures"

y = 4 # world grass height (4 for superflat)
num_variants = 3 # number of variants per corner
corners = ["nw","ne","sw","se"]

# pip install dependencies if missing

def update_block(world,pos,block_info):
    """
    block = amulet.Block(
        "minecraft", block_type, {"facing": StringTag("south")}
    )
    """
    block_split = block_info.split("[")
    material = block_split[0].replace("minecraft:","")
    properties = {}
    if len(block_split) > 1:
        for property in block_split[1][:-1].split(","):
            property_name = property.split("=")[0]
            property_value = property.split("=")[1].replace("\"","")
            properties[property_name] = StringTag(property_value)
    
    block = amulet.Block("minecraft", material,properties)

    try:
        world.set_version_block(
            pos[0],
            pos[1],
            pos[2],
            "minecraft:overworld",
            game_version,
            block
        )
    except:
        print("uhoh") # uhoh

    

def get_size(name,variant=1): # gets full size of environment
    full_size = [0,0]
    for corner in corners:
        full_structure_name = name+"_"+corner+"_"+str(variant)+".txt"
        structure_lines = []
        with open(structure_folder+"/"+full_structure_name,"r") as structure_file:
            structure_lines = structure_file.read().splitlines()

        size = structure_lines[0].split() # size of the corner
        size = (int(size[0]),int(size[1]),int(size[2]))

        full_size[0] += size[0]/2
        full_size[1] += size[2]/2 # size has x,y,z  while full_size has x,z

    return [int(full_size[0]),int(full_size[1])]


def build_environment(world,name,env_corners,location):
    offset_x = 0
    offset_z = 0

    variants = ""

    for given_corner in env_corners:
        corner = given_corner[:-1]
        variant = eval(given_corner[-1])

        variants += corner +" "+str(variant)+" "

        full_structure_name = name+"_"+corner+"_"+str(variant)+".txt"

        structure_lines = []
        with open(structure_folder+"/"+full_structure_name,"r") as structure_file:
            structure_lines = structure_file.read().splitlines()

        size = structure_lines[0].split()
        size = (int(size[0]),int(size[1]),int(size[2]))

        for block_line in structure_lines[1::]: # place all blocks from (x y z block)
            split_info = block_line.split()
            rel_pos = (int(split_info[0]),int(split_info[1]),int(split_info[2]))
            material = split_info[3]

            pos = (location[0]+offset_x+rel_pos[0],location[1]+rel_pos[1],location[2]+offset_z+rel_pos[2])
            update_block(world,pos,material)

        if corner == "nw" or corner == "sw": # update corner position
            offset_x += size[0]
        else:
            offset_x = 0
            offset_z += size[2]

    return variants

wall_coords_material = "yellow_terracotta"
wall_coords = []
with open(structure_folder+"/signs.txt","r") as signs_file:
    wall_coords_lines = signs_file.read().splitlines()
    for line in wall_coords_lines[1::]:
        str_coords = line.split(" ")[:-1]
        wall_coords.append([int(str_coords[0]),int(str_coords[1]),int(str_coords[2])])


border_mat = "stone_bricks"
border_thickness = 2 # doesn't scale correctly to other values
border_height = 50

    
def build_env_walls(world,pos,size,mat,height):
    for y in range(0,height):
        for x in range(-1,size[0]):
            for z in range(-1,size[1],size[1]): # negative = N, positive = S
                if z == -1: # don't overwrite previous env's S marker
                    for d in range(0,2):
                        update_block(world,(pos[0]+x,pos[1]+y,pos[2]+z+d),mat)
                else:
                    for d in range(-1,2):
                        update_block(world,(pos[0]+x,pos[1]+y,pos[2]+z+d),mat)
        for x in range(-1,size[0],size[0]): # negative = W, positive = E
            for z in range(0,size[1]): 
                for d in range(-1,2):
                    update_block(world,(pos[0]+x+d,pos[1]+y,pos[2]+z),mat)
    for block_location in wall_coords: # engrave walls
        update_block(world,(block_location[0]+pos[0],block_location[1]+pos[1]+10,block_location[2]+pos[2]),wall_coords_material)

# placeholder bounds for worldedit macro
lower_worldedit_bounds = (9999999,9999999,9999999)
upper_worldedit_bounds = (-9999999,-9999999,-9999999)

default_animals = ["sheep","cow","pig","chicken"]
custom_spawn_dict = {} # dictionary for specific environments that have spawn restrictions / custom spawn location

# get information about environments with limited mobs
with open("env_specific_mobs.txt","r") as animal_specs:
    for line in animal_specs.read().split("\n"):
        info = line.split()
        spawn_pos = " ".join(info[-3::])
        allowed_animals = []
        if len(info) > 4: # if there's specific animals for the env
            allowed_animals = info[1].split("|")
        custom_spawn_dict[info[0]] = [spawn_pos,allowed_animals]

command_block_list = []
qea_envs = []
qea_locations = []

# create command blocks, placeholder redstone blocks, and document locations for animal spawns
def add_animal_spawns(world,env,env_mobs,command_block_template,x,y,z):
    global command_block_list
    global lower_worldedit_bounds
    global upper_worldedit_bounds

    animals_added = []

    for i, mob in enumerate(env_mobs):
        update_block(world,(x+i,y+1,z),activation_redstone_block_placeholder) # placeholder above it for redstone
        update_block(world,(x+i,y+2,z),cleanup_redstone_block_placeholder) # placeholder above that for cleanup redstone

        lower_worldedit_bounds = (min(lower_worldedit_bounds[0],x+i),min(lower_worldedit_bounds[1],y),min(lower_worldedit_bounds[2],z))
        upper_worldedit_bounds = (max(upper_worldedit_bounds[0],x+i),max(upper_worldedit_bounds[1],y+3),max(upper_worldedit_bounds[2],z))
        
        # /summon sheep ~ ~ ~ {ActiveEffects:[{Id:11b,Amplifier:5b,Duration:2000,Ambient:1}]}
        chosen_animal = mob
        spawn_location = "~ ~-1 ~"

        nbt_tags = ["ActiveEffects:[{Id:11b,Amplifier:5b,Duration:2000,Ambient:1}]"] # give every animal resistence so they don't die!

        if env in custom_spawn_dict: # modified spawn location, maybe limited animal selection
            spawn_location = custom_spawn_dict[env][0]

            nbt_start_i = chosen_animal.find("{")
            if nbt_start_i != -1: # has nbt tag(s)
                for tag in chosen_animal[nbt_start_i+1:-1].split(","): # go through each specified nbt tag
                    nbt_tags.append(tag)
                chosen_animal = chosen_animal[:nbt_start_i] # update animal to not include nbt

        if chosen_animal == "sheep" and len(nbt_tags) < 2: # random color if sheep and not specified color
            nbt_tags.append("Color:"+str(randint(0,15))) 

        if len(nbt_tags) > 1: # if the animal has tags beyond resistence (for spawning), then document the tags
            animals_added.append(chosen_animal+"{"+",".join(nbt_tags[1::])+"}")
        else:
            animals_added.append(chosen_animal)

        summon_cmd = "/summon "+chosen_animal+" "+spawn_location+" {"+",".join(nbt_tags)+"}"
        fill_cmd = "/fill ~ ~ ~ ~ ~-3 ~ air" # 
        command_block_list.append([str(x+i),str(y),str(z),summon_cmd])
        command_block_list.append([str(x+i),str(y+3),str(z),fill_cmd]) # clean spawned blocks

        command_block_template[1].nbt["Command"] = StringTag(summon_cmd) # update command of command block for spawning
        world.set_version_block(x+i,y,z,"minecraft:overworld",game_version,command_block_template[0],command_block_template[1])
        command_block_template[1].nbt["Command"] = StringTag(fill_cmd) # update command of command block for cleanup
        world.set_version_block(x+i,y+3,z,"minecraft:overworld",game_version,command_block_template[0],command_block_template[1])

    return " ".join(animals_added)



def build_command_blocks(world_folder,cb_list): # world_folder is a path, cb_list is a list of (x,y,z,command)
    for cb in tqdm(cb_list):
        #region = world.get_region(0,0) # todo: add for multiple regions
        #chunk = region.get_chunk(0,0)
        region_pos, chunk_pos = get_region_and_chunk_from_pos(cb[0],cb[2])

        world = nbt.world.AnvilWorldFolder(world_folder)

        # set up redstone stuff, get templates
        region = world.get_region(region_pos[0],region_pos[1]) # todo: add for multiple regions
        chunk = region.get_chunk(chunk_pos[0],chunk_pos[1])

        if not chunk or not 'Level' in chunk:
            print("failed to load chunk ("+str(chunk_pos[0])+", "+str(chunk_pos[1])+")")
        else:
            tiles = chunk['Level']['TileEntities']
            for tile in tiles:
                if tile['id'].value == "minecraft:command_block" and cb[0] == tile['x'].value and cb[1] == tile['y'].value and cb[2] == tile['z'].value: # found command block in same position, update
                    tile['Command'].value = cb[3] # set new command from cb info
                    region.write_chunk(chunk_pos[0],chunk_pos[1],chunk)
                    break

#command_block_placeholder = "bricks"
command_block_placeholder = "command_block"
activation_redstone_block_placeholder = "sand"
cleanup_redstone_block_placeholder = "gravel"

size = get_size("desert") # bases environment sizes off of desert

# update sizes to account for walls around each environment
size[0] += border_thickness+1
size[1] += border_thickness+1

environment_variant_logs = []
chosen_env = ""

environments = ["plains","desert","nether","cave","city","mansion","snow","town"]

def get_random_environment():
    return environments[randint(0,len(environments)-1)]


def main():

    ###
    ###     Read QEA pairs from csv
    ###

    with open("qea_for_environment_generation.csv",'r') as csv_file:
        env_rows = list(csv.reader(csv_file))

        first_row = env_rows[0]
        env_column = -1
        question_col = -1
        for col in range(len(first_row)): # find which column in csv has environment info.
            if first_row[col] == "Environment":
                env_column = col 

        if question_col == -1:
            print("file 'qea_for_environment_generation.csv' is missing 'Environment' column")

        for row in env_rows[1::]:
            question = row[question_col]
            env = row[env_column]
            env_split = env.split(" ")
            biome = env_split[0]
            
            fix_mobs = False

            if biome == "plain":
                biome = "plains"
                fix_mobs = True
            elif biome == "caves":
                biome = "cave"
                fix_mobs = True
            env_corners = env_split[1]
            mobs = []
            if len(env_split) > 2:
                mobs = env_split[2:]

            if len(env_corners) == 1: # env_corners not given, assume given is number
                env_corners = "nw"+env_corners+"_ne"+env_corners+"_sw"+env_corners+"_se"+env_corners

            env_corners = env_corners.split("_")
            qea_envs.append([question,biome,env_corners,mobs])

    qea_env_locations = []

    num_envs = 9999999999 # make single line for smoother TP

    print("Cloning environment template")

    setup_new_environment() # clones template world and changes name to new_environment

    world = amulet.load_level("saves/pre_commands")

    command_block_template = world.get_version_block(-8,4,-8, "minecraft:overworld",game_version) # get CB from template

    print("Generating environments:")

    for i, env in tqdm(enumerate(qea_envs)):
        chosen_env = env[1]

        # find closest thing to square grid layout for environments
        x = i//2000000
        z = i%2000000000


        location = (size[0]*x+1,y,size[1]*z+1) # inner corner of environment
        local_logs = str(location[0])+" "+str(location[2])+" "+chosen_env # start log of environment info
        local_logs += " "+build_environment(world,chosen_env,env[2],location) # make the environment, log corners used
        local_logs += " "+add_animal_spawns(world,chosen_env,env[3],command_block_template,location[0]+size[0]//2,100,location[2]+size[1]//2) # setup animal spawns, add to logs

        qea_env_locations.append(env[0]+" : "+str(location))

        build_env_walls(world,(size[0]*x,y,size[1]*z),size,border_mat,border_height) # make walls around environment
        environment_variant_logs.append(local_logs)

    print("Saving world file")

    world.save()
    world.close()

    if len(qea_locations) > 0:
        with open("qea_environment_locations","w") as output_file:
            output_file.write("\n".join(qea_locations))

    with open("environment_key.txt","w") as output_file:
        output_file.write("\n".join(environment_variant_logs))

    if len(command_block_list) > 0:
        with open("command_block_bounds.txt","w") as cb_bounds:
            output = str(lower_worldedit_bounds[0])+" "+str(lower_worldedit_bounds[1])+" "+str(lower_worldedit_bounds[2])+" "+str(upper_worldedit_bounds[0])+" "+str(upper_worldedit_bounds[1]+1)+" "+str(upper_worldedit_bounds[2])
            output += " "+command_block_placeholder+" "+activation_redstone_block_placeholder+" "+cleanup_redstone_block_placeholder
            cb_bounds.write(output)

        with open("manual_commands_to_run.txt","w") as cb_manual_bounds:
            cb_manual_bounds.write("//pos1 "+str(lower_worldedit_bounds[0])+","+str(lower_worldedit_bounds[1])+","+str(lower_worldedit_bounds[2])+"\n"+
            "//pos2 "+str(upper_worldedit_bounds[0])+","+str(upper_worldedit_bounds[1]+1)+","+str(upper_worldedit_bounds[2])+"\n"+
            "//replace "+activation_redstone_block_placeholder+" redstone_block"+"\n"+
            "//replace "+cleanup_redstone_block_placeholder+" redstone_block")

        with open("command_block_list.txt","w") as cb_list:
            output = []
            for cb in command_block_list:
                output.append("|".join(cb))
            cb_list.write("\n".join(output))

if __name__ == "__main__":
    main()