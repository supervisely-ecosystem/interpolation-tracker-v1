import functools

import sly_globals as g
import supervisely_lib as sly

from tracker import InterpolationTracker
from interpolation import LinearPolygonInterpolation


def send_error_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        value = None
        try:
            value = func(*args, **kwargs)
        except Exception as e:
            track_id = kwargs["context"]["trackId"]
            g.api.post(
                "videos.notify-annotation-tool",
                data={
                    "type": "videos:tracking-error",
                    "data": {"trackId": track_id, "error": {"message": repr(e)}},
                },
            )
        return value

    return wrapper


@g.my_app.callback("ping")
@sly.timeit
@send_error_data
def get_session_info(api: sly.Api, task_id, context, state, app_logger):
    pass


@g.my_app.callback("track")
@sly.timeit
@send_error_data
def track(api: sly.Api, task_id, context, state, app_logger):
    model = LinearPolygonInterpolation(g.shape_complexity)
    tracker = InterpolationTracker(context, model)
    tracker.track()
    return


def main():
    sly.logger.info(
        "Script arguments",
        extra={"context.teamId": g.team_id, "context.workspaceId": g.workspace_id},
    )
    g.my_app.run()


if __name__ == "__main__":
    sly.main_wrapper("main", main)
