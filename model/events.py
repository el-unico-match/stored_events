from typing import List
from pydantic import BaseModel

class UserParams(BaseModel):
   userid: str

class FederatedUserParams(UserParams):
   federated_identity: str
   email: str

class HttpResult(UserParams):
   status_code: str
   delay_ms: int

class BlockedUserParams(UserParams):
   reason: str

class UserAction(UserParams):
   action: str
      # like
      # rewind
      # send_message
   
class ResetPasswordParams(BaseModel):
   email: str
   token: str

class IdentidadesFederadas(BaseModel):
   grupo: int
   cantidad: int
   porcentaje: float
   logins_exitosos: int
   logins_fallados: int
   promedio_inicio_sesion: float

class UsosDeAcciones(BaseModel):
   accion: str
   total: int

class MetricsResponse(BaseModel):
   taza_exito_de_registros: float
   tiempo_promedio_de_registros: float
   identidades_federadas: List[IdentidadesFederadas]
   
   bloqueos_totales: int
   bloqueos_actuales: int
   bloqueos_duracion: float

   password_reset_total: int
   password_reset_usados: int
   password_reset_duracion_promedio: int

   usos_de_acciones: List[UsosDeAcciones]
