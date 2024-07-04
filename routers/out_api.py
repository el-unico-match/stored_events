from typing import List, Union
from settings import settings
from datetime import datetime
from model.events import BlockedUserParams, EventIn, FederatedUserParams, HttpResult, ResetPasswordParams, UserAction, UserEventIn, UserParams
from fastapi import APIRouter, Path, Depends, Response, HTTPException
from endpoints.putWhitelist import update_whitelist, PutWhiteList
import data.client as client
import logging

logging.basicConfig(format='%(asctime)s [%(filename)s] %(levelname)s %(message)s',filename=settings.log_filename,level=settings.logging_level)

logger = logging.getLogger(__name__)
router = APIRouter(tags=["events"])

@router.put("/whitelist",summary="Actualiza la whitelist del servicio")
async def updateWhitelist(whitelist: PutWhiteList):
    update_whitelist(whitelist)
    return Response(status_code=201,content="Lista actualizada")


################ REGISTRACION ################
@router.post("/events/registration/start", summary="Almacena el evento de alta de usuario.", response_class=Response)
async def user_registration_start(values: FederatedUserParams, client_db = Depends(client.get_db)):    
    await client_db.execute(client.user_registration.insert().values(
        userid = values.userid, 
        email = values.email,
        federated_identity = values.federated_identity,
        start_date = datetime.now()
    ))

@router.post("/events/registration/finish", summary="Almacena el evento de finalizacion de registro de usuario.", response_class=Response)
async def user_registration_end(values: UserParams, client_db = Depends(client.get_db)):
    table = client.user_registration
    await client_db.execute(table.update().where(table.columns.userid == values.userid).values(
        end_date = datetime.now()
    ))
################################################

################ BLOQUEO ################
@router.post("/events/block", summary="Almacena el evento de bloqueo de usuario.", response_class=Response)
async def user_block_start(values: UserParams ,client_db = Depends(client.get_db)):
    await client_db.execute(client.user_block.insert().values(
        userid = values.userid, reason = "unknown",
        start_date = datetime.now()
    ))

@router.post("/events/unblock", summary="Almacena el evento de desbloqueo de usuario.", response_class=Response)
async def user_block_end(values: UserParams, client_db = Depends(client.get_db)):
    table = client.user_block
    await client_db.execute(table.update().where(table.columns.userid == values.userid).values(
        end_date = datetime.now()
    ))
#########################################

################ RESET DE CONTRASENIA ################
@router.post("/events/password-reset/request", summary="Almacena el evento de pedido de recuperacion de contrasenia.", response_class=Response)
async def user_reset_password_start(values: ResetPasswordParams, client_db = Depends(client.get_db)):
    user = await client_db.fetch_one(query = "select * from user_registration where email = :email", values = values.email)

    await client_db.execute(client.user_reset_password.insert().values(
        userid = user["userid"],
        start_date = datetime.now()
    ))

@router.post("/events/password-reset/complete", summary="Almacena el evento de finalizacion de recuperacion de contrasenia.", response_class=Response)
async def user_reset_password_use(values: ResetPasswordParams, client_db = Depends(client.get_db)):
    user = await client_db.fetch_one(query = "select * from user_registration where email = :email", values = values.email)

    table = client.user_reset_password
    await client_db.execute(table.update().where(table.columns.userid == user["userid"]).values(
        used_date = datetime.now()
    ))
######################################################


@router.post("/events/login", summary="Almacena el evento de finalizacion de recuperacion de contrasenia.", response_class=Response)
async def user_login_log(values: HttpResult, client_db = Depends(client.get_db)):
    await client_db.execute(client.user_login.insert().values(
        userid = values.userid,
        status_code = values.status_code,
        delay_ms = values.delay_ms
    ))

@router.post("/events/actions/log", summary="Almacena el evento de finalizacion de recuperacion de contrasenia.", response_class=Response)
async def user_action_log(values: UserAction, client_db = Depends(client.get_db)):
    await client_db.execute(client.user_login.insert().values(
        userid = values.userid,
        action = values.action,
        date = datetime.now()
    ))

# @router.get("/user/{id}/matchs",
#         response_model=List[MatchOut],
#         summary="Retorna una lista con todos los matchs")
# async def view_matchs(id:str,client_db = Depends(client.get_db)):
#     logger.error("retornando lista de matchs")

#     sql_query = '''
#         Select orig.userid_qualificator userid_1, orig.userid_qualificated userid_2,
#                orig.qualification qualification_1, dest.qualification qualification_2,
#                orig.qualification_date qualification_date_1, dest.qualification_date qualification_date_2,
#                pf1.username username_1, pf2.username username_2
#         from matchs orig
#            inner join profiles pf1 on orig.userid_qualificator = pf1.userid
#            inner join matchs dest on orig.userid_qualificated = dest.userid_qualificator 
#                                  and orig.userid_qualificator = dest.userid_qualificated
#            inner join profiles pf2 on orig.userid_qualificated = pf2.userid
#         where orig.qualification = :like
#           and dest.qualification = :like
#           and orig.userid_qualificator = :id
#           and not orig.blocked and not dest.blocked
#         order by orig.last_message_date desc
#     '''
    
#     results=await client_db.fetch_all(query = sql_query, values = {"id":id,"like":"like"})
    
#     #for result in results:
#     #    print(tuple(result.values()))

#     return matchs_schema(results) 
