from uuid import uuid4


from models.db_model import Score, IdLink
from models.response_model import IdResponse, ScoreResponseSingle, ScoreResponse


def warp_id_success_db(db_data: IdLink, title) -> IdResponse:
    return IdResponse(
        status=200,
        message='成功从数据库读取数据',
        bangumi_id=db_data.bangumi_id,
        title=title,
        myanimelist_id=db_data.myanimelist_id,
        anilist_id=db_data.anilist_id,
        filmarks_id=db_data.filmarks_id,
        anikore_id=db_data.anikore_id,
        myanimelist_useradd=db_data.myanimelist_useradd,
        anilist_useradd=db_data.anilist_useradd,
        filmarks_useradd=db_data.filmarks_useradd,
        anikore_useradd=db_data.anikore_useradd,
        verification_count=db_data.verification_count
    )


def warp_id_wait(task_id) -> IdResponse:
    return IdResponse(
        status=202,
        message='任务时间耗时过长，请等待处理完毕',
        task_id=task_id
    )

def warp_score_success_db(db_data: Score, title) -> ScoreResponse:
    return ScoreResponse(
        status=200,
        message='成功从数据库读取数据',
        bangumi_id=db_data.bangumi_id,
        title=title,
        myanimelist=ScoreResponseSingle(
            status=200 if db_data.myanimelist_score else 404,
            id=db_data.myanimelist_id,
            title=db_data.myanimelist_title,
            score=db_data.myanimelist_score,
            count=db_data.myanimelist_count
        ),
        anilist=ScoreResponseSingle(
            status=200 if db_data.anilist_score else 404,
            id=db_data.anilist_id,
            title=db_data.anilist_title,
            score=db_data.anilist_score,
            count=db_data.anilist_count
        ),
        filmarks=ScoreResponseSingle(
            status=200 if db_data.filmarks_score else 404,
            id=db_data.filmarks_id,
            title=db_data.filmarks_title,
            score=db_data.filmarks_score,
            count=db_data.filmarks_count
        ),
        anikore=ScoreResponseSingle(
            status=200 if db_data.anikore_score else 404,
            id=db_data.anikore_id,
            title=db_data.anikore_title,
            score=db_data.anikore_score,
            count=db_data.anikore_count
        )
    )

def warp_score_wait(task_id) -> ScoreResponse:
    return ScoreResponse(
        status=202,
        message='任务时间耗时过长，请等待处理完毕',
        task_id=task_id
    )