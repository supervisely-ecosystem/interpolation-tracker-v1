import os
import sys
import pathlib
from dotenv import load_dotenv

load_dotenv("debug.env")

import supervisely_lib as sly


logger = sly.logger

# load_dotenv("debug.env")
load_dotenv("secret_debug.env", override=True)

my_app = sly.AppService()
api = my_app.public_api
task_id = my_app.task_id

sly.fs.clean_dir(my_app.data_dir)  # @TODO: for debug

root_source_path = str(pathlib.Path(os.path.abspath(sys.argv[0])).parents[1])
sly.logger.info(f"Root source directory: {root_source_path}")
sys.path.append(root_source_path)

team_id = int(os.environ["context.teamId"])
workspace_id = int(os.environ["context.workspaceId"])
# device = os.environ['modal.state.device']
shape_complexity = os.environ["modal.state.shapeComplexity"]


local_info_dir = os.path.join(my_app.data_dir, "info")
sly.fs.mkdir(local_info_dir)


def get_files_paths(src_dir, extensions):
    files_paths = []
    for root, dirs, files in os.walk(src_dir):
        for extension in extensions:
            for file in files:
                if file.endswith(extension):
                    file_path = os.path.join(root, file)
                    files_paths.append(file_path)

    return files_paths
