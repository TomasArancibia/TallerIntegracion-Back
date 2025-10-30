from fastapi import APIRouter

router = APIRouter()

informacion = {
    "procesos_clinicos": "Información de procesos clínicos al paciente.",
    "seguridad_cuidados": "Información sobre seguridad asistencial y cuidados clínicos.",
    "info_administrativa": "Información administrativa y de otros pacientes.",
    "acompañantes_visitas": "Información sobre acompañantes y visitas."
}

@router.get("/info")
def obtener_todas_las_info():
    return informacion

@router.get("/info/{consulta}")
def obtener_info(consulta: str):
    return {"consulta": consulta, "info": "Información relevante sobre " + consulta}
