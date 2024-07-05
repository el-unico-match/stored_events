from typing import List, Union
from settings import settings
from datetime import datetime
from model.events import FederatedUserParams, HttpResult, IdentidadesFederadas, MetricsResponse, ResetPasswordParams, UserAction, UserParams, UsosDeAcciones
from model.try_set import try_set
from fastapi import APIRouter, Path, Depends, Response, HTTPException
from endpoints.putWhitelist import update_whitelist, PutWhiteList
import data.client as client
#import logging
from common.utilities import getLogger
logger = getLogger(__name__)
#logging.basicConfig(format='%(asctime)s [%(filename)s] %(levelname)s %(message)s',filename=settings.log_filename,level=settings.logging_level)
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


@router.post("/events/login", summary="Almacena el evento de finalizacion de recuperacion de contrasenia.", response_class = Response)
async def user_login_log(values: HttpResult, client_db = Depends(client.get_db)):
    await client_db.execute(client.user_login.insert().values(
        userid = values.userid,
        status_code = values.status_code,
        delay_ms = values.delay_ms
    ))

@router.post("/events/actions/log", summary="Almacena el evento de finalizacion de recuperacion de contrasenia.", response_class = Response)
async def user_action_log(values: UserAction, client_db = Depends(client.get_db)):
    await client_db.execute(client.user_login.insert().values(
        userid = values.userid,
        action = values.action,
        date = datetime.now()
    ))


@router.get("/events/metrics", summary="Retorna una entidad con los valores de las metricas.", response_class = MetricsResponse)
async def view_matchs(client_db = Depends(client.get_db)):
    logs = []

    try:
        logger.info("------ Iniciando metricas ------")
        logs.append("------ Iniciando metricas v4 ------")
        metrics_data = {
            "taza_exito_de_registros": 0,
            "tiempo_promedio_de_registros": 0,
            "identidades_federadas": [],
            "bloqueos_totales": 0,
            "bloqueos_actuales": 0,
            "bloqueos_duracion": 0,
            "password_reset_total": 0,
            "password_reset_usados": 0,
            "password_reset_duracion_promedio": 0,
            "usos_de_acciones": []
        }

        sql_query1 = '''
            Select Count(end_date) / Count(1) TazaExito, 
                SUM(extract(epoch from
                    (end_date)::timestamp - (start_date)::timestamp
                )) / COUNT(end_date) TiempoPromedio
            from user_registration
        '''
        
        logs.append("--- Obtener metricas de registros.")
        result1 = await client_db.fetch_one(sql_query1)
        logs.append(f"--- Resultado de metricas de registros: {dict(result1)}")

        try_set(result1,"TazaExito").to(metrics_data,"taza_exito_de_registros")
        try_set(result1,"TiempoPromedio").to(metrics_data,"tiempo_promedio_de_registros")

        sql_query2 = '''
            Select ur.federated_identity fed_identity,
                count(distinct ur.userid) usercount,
                count(logins.success) success,
                count(logins.failure) failure,
                sum(logins.delay_ms) tot_time,
                count(logins.userid) tot_regs
            from user_registration ur
                left join lateral (
                    select ul.userid, 1 success, null failure, ul.delay_ms 
                    from user_login ul 
                    where ur.userid = ul.userid and ul.status_code like '2__'
                
                    union all
                
                    select ul.userid, null success, 1 failure, delay_ms 
                    from user_login ul 
                    where ur.userid = ul.userid and ul.status_code not like '2__'
                ) logins on true
            group by ur.federated_identity
        '''
        #logger.info("--- Obtener metricas de identidades federadas.")
        logs.append("--- Obtener metricas de identidades federadas.")
        result2 = await client_db.fetch_all(sql_query2)
        logs.append(f"--- Resultado de metricas de identidades federadas: {result2}")

        cantidad_total = 0
        for item in result2:
            cantidad_total += item["usercount"]
            calc = 0
            if (item["tot_regs"] > 0):
                calc = item["tot_time"] / item["tot_regs"]

            inst = {
                "grupo": item["group"],
                "cantidad": item["usercount"],
                "porcentaje": item["usercount"],
                "logins_exitosos": item["success"],
                "logins_fallados": item["failure"],
                "promedio_inicio_sesion": calc
            }

            metrics_data["identidades_federadas"].append(inst)

        for item in metrics_data["identidades_federadas"]:
            item.porcentaje /= cantidad_total
        logs.append("--- Proceso metricas de registros.")

        sql_query3 = '''
            Select Count(1) total,

                Count(1) - count(ub.end_date) active,

                Sum(extract( epoch from
                    (ub.end_date)::timestamp - (ub.start_date)::timestamp
                )) / (60*count(1))
                duracion_promedio

            from user_block ub
        '''
        #logger.info("--- Obtener metricas de bloqueos.")
        logs.append("--- Obtener metricas de bloqueos.")
        result3 = await client_db.fetch_one(sql_query3)
        logs.append("--- Obtubo metricas de bloqueos.")
        
        if result3 is not None:
            metrics_data["bloqueos_totales"] = result3["total"]
            metrics_data["bloqueos_actuales"] = result3["active"]
            metrics_data["bloqueos_duracion"] = result3["duracion_promedio"]

        sql_query4 = '''
            Select count(1) total,
                count(used_date) used,
                Sum(extract( epoch from
                    (used_date)::timestamp - (start_date)::timestamp
                )) / count(1) duracion_promedio
            from user_reset_password
        '''
        #logger.info("--- Obtener metricas de reinicios de contrasenias.")
        logs.append("--- Obtener metricas de reinicios de contrasenias.")
        result4 = await client_db.fetch_one(sql_query4)
        logs.append(f"--- Resultados de metricas de reinicios de contrasenias: {result4}")

        if result4 is not None:
            metrics_data["password_reset_total"] = result4["total"]
            metrics_data["password_reset_usados"] = result4["used"]
            metrics_data["password_reset_duracion_promedio"] = result4["duracion_promedio"]

        sql_query5 = '''
            select action, count(1) total
            from user_action
            group by action
        '''
        #logger.info("--- Obtener metricas de conteo de acciones.")
        logs.append("--- Obtener metricas de conteo de acciones.")
        result5 = await client_db.fetch_all(sql_query5)
        logs.append(f"--- Resultados de metricas de conteo de acciones: {result5}")
        
        for item in result5:
            inst = {
                "accion": item["action"].upper(),
                "total": item["total"]
            }

            metrics_data["usos_de_acciones"].append(inst)

        #metrics_data = Metrics(**metrics_data)
        # metrics_data #Response(status_code = 200, content = f"{metrics_data}")
        return Response(status_code=200, content= "all good")
    except Exception as e:
        logs.append("FALLO: " + str(e))
        #return Response(status_code = 500, content = f"An error occurred: {err}")
    
    return Response(status_code=200, content = "\n".join(logs))
