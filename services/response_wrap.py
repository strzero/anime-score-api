from uuid import uuid4

from models.response_model import IdResponse

def warp_id_success_db(db_data, title) -> IdResponse:
    return IdResponse(
        status=200,
        message='成功从数据库读取数据',
        bangumi_id=db_data.bangumi_id,
        title=title,
        myanimelist_id=db_data.myanimelist_id,
        anilist_id=db_data.anilist_id,
        filmarks_id=db_data.filmarks_id,
        anikore_id=db_data.anikore_id,
        user_add=db_data.user_add,
        verification_count=db_data.verification_count
    )

# def warp_id_success_webdata(result, title, task_id) -> IdResponse:
#     return IdResponse(
#         status=200,
#         task_id=task_id,
#         bangumi_id=result.bangumi_id,
#         title=title,
#         myanimelist_id=result.myanimelist_id,
#         anilist_id=result.anilist_id,
#         filmarks_id=result.filmarks_id,
#         anikore_id=result.anikore_id,
#         user_add=0,
#         verification_count=0
#     )

def warp_id_wait(task_id) -> IdResponse:
    return IdResponse(
        status=202,
        message='任务时间耗时过长，请等待处理完毕',
        task_id=task_id
    )