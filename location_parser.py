from math import floor, ceil

# gets mca region areas from bounds, regions are 512x512 blocks 0-indexed
def get_regions_from_bounds(low_x,low_z,upp_x,upp_z):
    lower_region_x = floor(low_x/512)
    upper_region_x = ceil(upp_x/512)

    lower_region_z = floor(low_z/512)
    upper_region_z = ceil(upp_z/512)

    regions = {}

    for x in range(lower_region_x,upper_region_x):
        for z in range(lower_region_z,upper_region_z):
            regions[(x,z)] = {}
    
    return regions

# get a [(x,z), ...] list of empty chunks from regions with global chunk values i.e. chunk 32,32 is the first chunk in region 1,1
def get_chunks_from_regions(regions):
    chunks = {}
    for region in regions:
        for x in range(32*region[0],32*(region[0]+1)):
            for z in range(32*region[1],32*(region[1]+1)):
                chunks[(x,z)] = {}
    return chunks

# from global chunk position get region
def get_region_from_chunk(chunk):
    region = (chunk[0]//32,chunk[1]//32)
    return region

# put global chunks in local format [0,16) for every region
def pack_regions_from_global_chunks(regions,chunks):
    for region in regions:
        for chunk in chunks:
            local_ref = get_local_chunk_ref((region[0],region[1]),chunk[0],chunk[1])
            regions[region][local_ref] = chunks[chunk]

    return regions

# get local chunk position from global chunk position
def get_local_chunk_ref(region,global_chunk_x,global_chunk_z):
    return (global_chunk_x%32,global_chunk_z%32)

# get the global chunk from position
def get_global_chunk_from_pos(x,z):
    return (floor(x/16),floor(z/16))

# get the region and chunk from x and z coords
def get_region_and_chunk_from_pos(x,z):
    chunk_x = x//16
    chunk_z = z//16

    region_x = chunk_x//32
    region_z = chunk_z//32

    return (region_x,region_z),get_local_chunk_ref((region_x,region_z),chunk_x,chunk_z) # ex: (-1,-1), (26,28) for chunk -6, -4

# pack a list of blocks into a list of regions with blocks in their correct chunks
def get_mca_format_from_block_list(block_list): # blocks in block_list need a x and z property!
    min_x = 0
    max_x = 0
    min_z = 0
    max_z = 0

    for block in block_list:
        min_x = min(block.x,min_x)
        max_x = max(block.x,max_x)
        min_z = min(block.z,min_z)
        max_z = max(block.z,max_z)

    regions = get_regions_from_bounds(min_x,min_z,max_x,max_z)
    chunks = get_chunks_from_regions(regions)

    for block in block_list:
        block_chunk = (block.x//16,block.z//16)
        chunks[block_chunk].append(block)
    
    return pack_regions_from_global_chunks(regions,chunks)


if __name__ == "__main__":
    regions = get_regions_from_bounds(-220,-110,-50,-50)
    chunks = get_chunks_from_regions(regions)

    # test location --> chunk --> region chunk
    cur_chunk = get_global_chunk_from_pos(-88,-57)
    relative = get_local_chunk_ref((-1,-1),cur_chunk[0],cur_chunk[1])
    #print(relative)

    # test packing
    #print(pack_regions_from_global_chunks(regions,chunks))

    # test location --> region info
    print(get_region_and_chunk_from_pos(-512,-512))