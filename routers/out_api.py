from typing import List, Union
from settings import settings
from datetime import datetime
from model.events import FederatedUserParams, HttpResult, IdentidadesFederadas, Metrics, ResetPasswordParams, UserAction, UserParams, UsosDeAcciones
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


@router.get("/events/metrics", summary="Retorna una entidad con los valores de las metricas.", response_class=Metrics)
async def view_matchs(client_db = Depends(client.get_db)):
    logger.info("------ Iniciando metricas ------")
    response_data = Metrics()

    sql_query1 = '''
        Select Count(end_date) / Count(1) TazaExito, 
            SUM(end_date - start_date) / COUNT(end_date) TiempoPromedio
        from user_registration
    '''
    logger.info("--- Obtener metricas de registros.")
    result1 = await client_db.fetch_one(sql_query1)

    if result1 is not None:
        response_data.taza_exito_de_registros = result1["TazaExito"]
        response_data.tiempo_promedio_de_registros = result1["TiempoPromedio"]

    sql_query2 = '''
        Select ur.federated_identity group,
            count(distinct ur.userid) count,
            count(logins.success) success,
            count(logins.failure) failure,
            
            sum(logins.delay_ms) tot_time,
            count(ul_user) tot_regs
        from user_registration ur
            outer apply (
                select ul.userid, 1 success, null failure, delay_ms from user_login ul on ur.userid = ul.userid and ul.status_code like '2__'
                union all
                select ul.userid, null success, 1 failure, delay_ms from user_login ul on ur.userid = ul.userid and ul.status_code not like '2__'
            ) logins
        where 
    '''
    logger.info("--- Obtener metricas de identidades federadas.")
    result2 = await client_db.fetch_all(sql_query2)

    cantidad_total = 0
    response_data.identidades_federadas = []
    for item in result2:
        cantidad_total += item["count"]
        calc = 0
        if (item["tot_regs"] > 0):
            calc = item["tot_time"] / item["tot_regs"]

        inst = IdentidadesFederadas()
        inst.grupo = item["group"]
        inst.cantidad = item["count"]
        inst.porcentaje = item["count"]
        inst.logins_exitosos = item["success"]
        inst.logins_fallados = item["failure"]
        inst.promedio_inicio_sesion = calc

        response_data.identidades_federadas.append(inst)

    for item in response_data.identidades_federadas:
        item.porcentaje /= cantidad_total

    sql_query3 = '''
        Select Count(1) total,
            count(1) - count(ub.end_date) current,
            extract(epoch from 
                (ub.end_date)::timestamp - (ub.start_date)::timestamp
            ) / 60 duracion_promedio
        from user_block ub
    '''
    logger.info("--- Obtener metricas de bloqueos.")
    result3 = await client_db.fetch_one(sql_query3)
    
    response_data.bloqueos_totales = result3["total"]
    response_data.bloqueos_actuales = result3["current"]
    response_data.bloqueos_duracion = result3["duracion_promedio"]

    sql_query4 = '''
        Select count(1) total,
            count(used_date) used,
            extract(epoch from 
                (end_date)::timestamp - (start_date)::timestamp
            ) duracion_promedio
        from user_reset_password
    '''
    logger.info("--- Obtener metricas de reinicios de contrasenias.")

    result4 = await client_db.fetch_one(sql_query4)
    response_data.password_reset_total = result4["total"]
    response_data.password_reset_usados = result4["used"]
    response_data.password_reset_duracion_promedio = result4["duracion_promedio"]

    sql_query5 = '''
        select action, count(1) total
        from user_action
        group by action
    '''
    logger.info("--- Obtener metricas de acciones de acciones.")
    result5 = await client_db.fetch_all(sql_query5)
    
    response_data.usos_de_acciones = []
    for item in result5:
        inst = UsosDeAcciones()
        inst.accion = item["action"].upper()
        inst.total = item["total"]

        response_data.usos_de_acciones.append(inst)

    return response_data
