import shutil, errno

def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno in (errno.ENOTDIR, errno.EINVAL):
            shutil.copy(src, dst)
        else: raise

def duplicate_world(template_name, world_name):
    copyanything("saves/"+template_name,"saves/"+world_name)

def setup_new_environment(source="template_please_dont_delete",dest="pre_commands"):
    try:
        shutil.rmtree("saves/"+dest)
    except:
        pass
    duplicate_world(source,dest)