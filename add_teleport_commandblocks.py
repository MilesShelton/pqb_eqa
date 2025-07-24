from random import randint
import shutil
from tqdm import tqdm

import csv

from duplicate_save_file import setup_new_environment

import amulet
from amulet_nbt import StringTag, IntTag, AbstractBaseTag
game_version = ("java",(1,16,5))

redstone_block_placeholder = "polished_blackstone_wall"

structure_folder = "aqua_structures"

current_question_number = 0

y = 4 # world grass height (4 for superflat)
num_variants = 3 # number of variants per corner
corners = ["nw","ne","sw","se"]

# placeholder bounds for worldedit macro
lower_worldedit_bounds = (9999999,9999999,9999999)
upper_worldedit_bounds = (-9999999,-9999999,-9999999)

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

border_thickness = 2
size = get_size("desert") # bases environment sizes off of desert

# update sizes to account for walls around each environment
size[0] += border_thickness+1
size[1] += border_thickness+1

# environments where spawning you in the middle is NOT a good idea
custom_spawn_dict = {
    "nether": [-24,-14,-9],
    "cave": [20,-11, -19],
    "mansion": [-1,-12,-25],
    "plains": [-4, -13, 0], # base height 20
    "town": [-5, -13, 0],
    "city": [-3, -15, 0],
    "desert": [-6, -12, 0],
    "snow": [-2, -13, 0],
    "jungle": [0,-6,8],
    "beach": [1,-6,-1],
    "circus": [0,-13,0]
}

command_block_list = []

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

"""

def make_setup_command_block(command,command_block_location):
    global lower_worldedit_bounds
    global upper_worldedit_bounds

    x,y,z = command_block_location

    update_block(world,(x,y,z),"minecraft:repeating_command_block") # cleaning block
    update_block(world,(x,y+1,z),"minecraft:stone_button[face=floor]") # placeholder between for redstone
    
    command_block_template[1].nbt["Command"] = StringTag(command) # update command of command block for spawning
    world.set_version_block(x,y,z,"minecraft:overworld",game_version,command_block_template[0],command_block_template[1])

    #/setblock ~ ~ ~ 

def add_spawn_teleporter(world,env,env_number,env_location,repeating_cb_template,command_block_location):
    global lower_worldedit_bounds
    global upper_worldedit_bounds

    x,y,z = command_block_location

    update_block(world,(x,y,z),"minecraft:repeating_command_block") # cleaning block
    update_block(world,(x,y+1,z),redstone_block_placeholder) # placeholder between for redstone
    update_block(world,(x,y+2,z),"minecraft:repeating_command_block") # teleport block

    lower_worldedit_bounds = (min(lower_worldedit_bounds[0],x),min(lower_worldedit_bounds[1],y+1),min(lower_worldedit_bounds[2],z))
    upper_worldedit_bounds = (max(upper_worldedit_bounds[0],x),max(upper_worldedit_bounds[1],y+1),max(upper_worldedit_bounds[2],z))
    
    spawn_location = [env_location[0],env_location[1],env_location[2]] # [x,y,z]

    spawn_offset = custom_spawn_dict.get(env)
    if spawn_offset:
        print(env,spawn_offset)
        spawn_location[0] += spawn_offset[0]
        spawn_location[1] += spawn_offset[1]
        spawn_location[2] += spawn_offset[2]

    spawn_location[0] = str(spawn_location[0])
    spawn_location[1] = str(spawn_location[1])
    spawn_location[2] = str(spawn_location[2])

    teleport_cmd = "execute as @a[scores={question_number="+str(env_number)+"}] run tp @a "+" ".join(spawn_location)
    clean_cmd = "execute as @a[scores={question_number="+str(env_number)+"}] run setblock ~ ~-1 ~ minecraft:air"
    #command_block_list.append([str(x+command_block_offset),str(y),str(z),teleport_cmd])
    #command_block_list.append([str(x+command_block_offset),str(y+2),str(z),clean_cmd])

    repeating_cb_template[1].nbt["Command"] = StringTag(teleport_cmd) # update command of command block for spawning
    world.set_version_block(x,y,z,"minecraft:overworld",game_version,repeating_cb_template[0],repeating_cb_template[1])
    repeating_cb_template[1].nbt["Command"] = StringTag(clean_cmd) # update command of command block for cleanup
    world.set_version_block(x,y+2,z,"minecraft:overworld",game_version,repeating_cb_template[0],repeating_cb_template[1])

"""

def add_spawn_teleporter(world,env,env_number,env_location,command_block_template,command_block_location):
    global lower_worldedit_bounds
    global upper_worldedit_bounds
    global current_question_number

    x,y,z = command_block_location

    
    spawn_location = [env_location[0],env_location[1],env_location[2]] # [x,y,z]


    spawn_offset = custom_spawn_dict.get(env)
    if spawn_offset:
        print(env,spawn_offset)
        spawn_location[0] += spawn_offset[0]
        spawn_location[1] += spawn_offset[1]
        spawn_location[2] += spawn_offset[2]
        
    new_cmd_location = [spawn_location[0],spawn_location[1],spawn_location[2]]

    if current_question_number > 0:
        update_block(world,(x,y-1,z),"minecraft:repeating_command_block") # teleport block
        update_block(world,(x,y,z),"minecraft:stone_button[face=floor]") # activation block
        update_block(world,(x,y,z+2),"minecraft:heavy_weighted_pressure_plate") # activation block
        spawn_location[0] = str(spawn_location[0])
        spawn_location[1] = str(spawn_location[1])
        spawn_location[2] = str(spawn_location[2])

        teleport_cmd = "tp @a "+" ".join(spawn_location)
        #command_block_list.append([str(x+command_block_offset),str(y),str(z),teleport_cmd])
        #command_block_list.append([str(x+command_block_offset),str(y+2),str(z),clean_cmd])

        command_block_template[1].nbt["Command"] = StringTag(teleport_cmd) # update command of command block for teleporting
        world.set_version_block(x,y-1,z,"minecraft:overworld",game_version,command_block_template[0],command_block_template[1])
        
        command_block_template[1].nbt["Command"] = StringTag("say Current Question: "+str(current_question_number)) # update command of command block for teleporting
        world.set_version_block(x,y-1,z+2,"minecraft:overworld",game_version,command_block_template[0],command_block_template[1])
    

    current_question_number += 1

    return new_cmd_location 


def main():
    print("Cloning built environment")

    source_name = "eqa_environment"
    new_env_name = "env_with_teleports"

    setup_new_environment(source=source_name,dest=new_env_name) # clones template world and changes name to new_environment

    world = amulet.load_level("saves/"+new_env_name)

    command_block_template = world.get_version_block(-8,4,-8, "minecraft:overworld",game_version) # get CB from template
    repeating_cb_template = world.get_version_block(-8,4,-7, "minecraft:overworld",game_version) # get CB from template
    sign_template = world.get_version_block(-8,4,-9, "minecraft:overworld",game_version) # get sign from template
    sign_template[1].nbt["Text1"] = AbstractBaseTag({"text":"Question Num:"})
    sign_template[1].nbt["Text2"] = AbstractBaseTag({"text":str(current_question_number)})
    sign_template[1].nbt["Text3"] = AbstractBaseTag({"text":""})
    # Text1, Text2, Text3, Text4

    print("Reading QEA pairs: ")

    qea_envs = []
    with open("qea_for_environment_generation.csv",'r') as csv_file:
        env_rows = list(csv.reader(csv_file))

        first_row = env_rows[0]
        env_column = -1
        question_col = -1
        for col in range(len(first_row)): # find which column in csv has environment info.
            if first_row[col] == "Environment":
                env_column = col 
            elif first_row[col] == "Question":
                question_col = col

        if env_column == -1 or question_col == -1:
            print("file 'qea_for_environment_generation.csv' is missing one or more column(s): 'Environment' or 'Question'")

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

    num_envs = 9999999999999 # make single line for smoother TP

    print("Constructing teleport blocks: ")

    command_block_location = [24,7,28]

    for i, env in tqdm(enumerate(qea_envs)):

        chosen_env = env[1]

        # find closest thing to square grid layout for environments
        x = i//int(num_envs**.5)
        z = i%int(num_envs**.5)

        location = [size[0]*x,y,size[1]*z] # inner corner of environment
        env_center = [location[0]+size[0]//2,20,location[2]+size[1]//2]

        command_block_location = add_spawn_teleporter(world,chosen_env,i+1,env_center,command_block_template,command_block_location)

    print("Saving world file")

    world.save()
    world.close()

    """
    commands = [
        "//pos1 "+str(lower_worldedit_bounds[0])+","+str(command_block_location[1]+1)+","+str(lower_worldedit_bounds[2]),
        "//pos2 "+str(upper_worldedit_bounds[0])+","+str(command_block_location[1]+1)+","+str(upper_worldedit_bounds[2]),
        "//replace "+redstone_block_placeholder+" redstone_block"
    ]

    with open("manual_commands_to_run.txt","w") as cb_manual_bounds:
        cb_manual_bounds.write("\n".join(commands))
    """

    try:
        shutil.rmtree("saves/"+source_name)
    except:
        print("could not delete saves/"+source_name)

if __name__ == "__main__":
    main()