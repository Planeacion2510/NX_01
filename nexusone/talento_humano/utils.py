from decimal import Decimal
from datetime import date, timedelta
from django.db.models import Sum
import os
from django.conf import settings

# ============================================================================
# CONSTANTES LEGALES COLOMBIA 2025
# ============================================================================

SMLV_2025 = Decimal('1423500')  # Salario Mínimo Legal Vigente 2025
AUXILIO_TRANSPORTE_2025 = Decimal('200000')  # Auxilio de transporte 2025
IBC_MINIMO = SMLV_2025
IBC_MAXIMO = SMLV_2025 * 25  # 25 SMLV

# Porcentajes de aportes
PORCENTAJE_SALUD_EMPLEADO = Decimal('4.0')
PORCENTAJE_SALUD_EMPLEADOR = Decimal('8.5')
PORCENTAJE_PENSION_EMPLEADO = Decimal('4.0')
PORCENTAJE_PENSION_EMPLEADOR = Decimal('12.0')
PORCENTAJE_FONDO_SOLIDARIDAD = Decimal('1.0')  # Si salario > 4 SMLV
PORCENTAJE_CAJA_COMPENSACION = Decimal('4.0')
PORCENTAJE_ICBF = Decimal('3.0')
PORCENTAJE_SENA = Decimal('2.0')

# Parafiscales
LIMITE_PARAFISCALES = SMLV_2025 * 10  # Si nómina > 10 SMLV paga parafiscales

# Prestaciones sociales
PORCENTAJE_CESANTIAS = Decimal('8.33')
PORCENTAJE_INTERESES_CESANTIAS = Decimal('12.0')
PORCENTAJE_PRIMA = Decimal('8.33')
PORCENTAJE_VACACIONES = Decimal('4.17')


# ============================================================================
# CÁLCULOS DE NÓMINA
# ============================================================================

def calcular_salario_hora_ordinaria(salario_basico):
    """
    Calcula el valor de la hora ordinaria
    Formula: Salario / 240 horas mensuales
    """
    return salario_basico / Decimal('240')


def calcular_hora_extra_diurna(salario_basico):
    """
    Hora extra diurna: 25% de recargo
    Formula: (Salario / 240) * 1.25
    """
    hora_ordinaria = calcular_salario_hora_ordinaria(salario_basico)
    return hora_ordinaria * Decimal('1.25')


def calcular_hora_extra_nocturna(salario_basico):
    """
    Hora extra nocturna: 75% de recargo
    Formula: (Salario / 240) * 1.75
    """
    hora_ordinaria = calcular_salario_hora_ordinaria(salario_basico)
    return hora_ordinaria * Decimal('1.75')


def calcular_hora_extra_dominical_festiva(salario_basico):
    """
    Hora extra dominical/festiva: 100% de recargo
    Formula: (Salario / 240) * 2.0
    """
    hora_ordinaria = calcular_salario_hora_ordinaria(salario_basico)
    return hora_ordinaria * Decimal('2.0')


def calcular_recargo_nocturno(salario_basico):
    """
    Recargo nocturno: 35% de recargo
    Formula: (Salario / 240) * 0.35
    """
    hora_ordinaria = calcular_salario_hora_ordinaria(salario_basico)
    return hora_ordinaria * Decimal('0.35')


def calcular_recargo_dominical(salario_basico):
    """
    Recargo dominical: 75% de recargo
    Formula: (Salario / 240) * 0.75
    """
    hora_ordinaria = calcular_salario_hora_ordinaria(salario_basico)
    return hora_ordinaria * Decimal('0.75')


def aplica_auxilio_transporte(salario_basico):
    """
    Verifica si aplica auxilio de transporte
    Aplica si salario <= 2 SMLV
    """
    limite = SMLV_2025 * 2
    return salario_basico <= limite


def calcular_ibc(salario_basico, devengos_adicionales=0):
    """
    Calcula el Ingreso Base de Cotización (IBC)
    IBC = Salario básico + devengos salariales (sin aux. transporte)
    """
    ibc = salario_basico + Decimal(str(devengos_adicionales))
    
    # Validar límites
    if ibc < IBC_MINIMO:
        ibc = IBC_MINIMO
    elif ibc > IBC_MAXIMO:
        ibc = IBC_MAXIMO
    
    return ibc


def calcular_aporte_salud_empleado(ibc):
    """Aporte a salud del empleado (4%)"""
    return ibc * (PORCENTAJE_SALUD_EMPLEADO / 100)


def calcular_aporte_salud_empleador(ibc):
    """Aporte a salud del empleador (8.5%)"""
    return ibc * (PORCENTAJE_SALUD_EMPLEADOR / 100)


def calcular_aporte_pension_empleado(ibc):
    """Aporte a pensión del empleado (4%)"""
    return ibc * (PORCENTAJE_PENSION_EMPLEADO / 100)


def calcular_aporte_pension_empleador(ibc):
    """Aporte a pensión del empleador (12%)"""
    return ibc * (PORCENTAJE_PENSION_EMPLEADOR / 100)


def calcular_fondo_solidaridad(ibc):
    """
    Calcula aporte al fondo de solidaridad pensional
    Aplica si IBC > 4 SMLV
    
    Escalas:
    - 4 a 16 SMLV: 1.0%
    - 16 a 17 SMLV: 1.2%
    - 17 a 18 SMLV: 1.4%
    - 18 a 19 SMLV: 1.6%
    - 19 a 20 SMLV: 1.8%
    - > 20 SMLV: 2.0%
    """
    if ibc <= SMLV_2025 * 4:
        return Decimal('0')
    
    if ibc <= SMLV_2025 * 16:
        porcentaje = Decimal('1.0')
    elif ibc <= SMLV_2025 * 17:
        porcentaje = Decimal('1.2')
    elif ibc <= SMLV_2025 * 18:
        porcentaje = Decimal('1.4')
    elif ibc <= SMLV_2025 * 19:
        porcentaje = Decimal('1.6')
    elif ibc <= SMLV_2025 * 20:
        porcentaje = Decimal('1.8')
    else:
        porcentaje = Decimal('2.0')
    
    return ibc * (porcentaje / 100)


def calcular_aporte_arl(ibc, clase_riesgo='I'):
    """
    Calcula aporte a ARL según clase de riesgo
    100% empleador
    
    Clase I: 0.522%
    Clase II: 1.044%
    Clase III: 2.436%
    Clase IV: 4.350%
    Clase V: 6.960%
    """
    porcentajes = {
        'I': Decimal('0.522'),
        'II': Decimal('1.044'),
        'III': Decimal('2.436'),
        'IV': Decimal('4.350'),
        'V': Decimal('6.960'),
    }
    
    porcentaje = porcentajes.get(clase_riesgo, Decimal('0.522'))
    return ibc * (porcentaje / 100)


def calcular_parafiscales(ibc, nomina_total):
    """
    Calcula parafiscales (Caja, ICBF, SENA)
    Solo aplica si nómina total empresa > 10 SMLV
    """
    if nomina_total <= LIMITE_PARAFISCALES:
        return {
            'caja_compensacion': Decimal('0'),
            'icbf': Decimal('0'),
            'sena': Decimal('0'),
            'total': Decimal('0'),
        }
    
    caja = ibc * (PORCENTAJE_CAJA_COMPENSACION / 100)
    icbf = ibc * (PORCENTAJE_ICBF / 100)
    sena = ibc * (PORCENTAJE_SENA / 100)
    
    return {
        'caja_compensacion': caja,
        'icbf': icbf,
        'sena': sena,
        'total': caja + icbf + sena,
    }


def calcular_cesantias(salario_basico, dias_trabajados=360):
    """
    Calcula cesantías
    Formula: (Salario * Días trabajados) / 360
    """
    return (salario_basico * Decimal(str(dias_trabajados))) / Decimal('360')


def calcular_intereses_cesantias(cesantias):
    """
    Calcula intereses sobre cesantías (12% anual)
    """
    return cesantias * (PORCENTAJE_INTERESES_CESANTIAS / 100)


def calcular_prima_servicios(salario_basico, dias_trabajados=180):
    """
    Calcula prima de servicios (semestral)
    Formula: (Salario * Días trabajados) / 360
    """
    return (salario_basico * Decimal(str(dias_trabajados))) / Decimal('360')


def calcular_vacaciones(salario_basico, dias_trabajados=360):
    """
    Calcula vacaciones (15 días hábiles por año)
    Formula: (Salario * Días trabajados) / 720
    
    Nota: Se divide entre 720 porque son 15 días hábiles por 360 días
    """
    return (salario_basico * Decimal(str(dias_trabajados))) / Decimal('720')


# ============================================================================
# UTILIDADES GENERALES
# ============================================================================

def calcular_antiguedad(fecha_ingreso):
    """
    Calcula la antigüedad en años, meses y días
    """
    if not fecha_ingreso:
        return None
    
    hoy = date.today()
    delta = hoy - fecha_ingreso
    
    años = delta.days // 365
    meses = (delta.days % 365) // 30
    dias = (delta.days % 365) % 30
    
    return {
        'años': años,
        'meses': meses,
        'dias': dias,
        'total_dias': delta.days,
        'texto': f"{años} año(s), {meses} mes(es), {dias} día(s)"
    }


def calcular_edad(fecha_nacimiento):
    """
    Calcula la edad en años
    """
    if not fecha_nacimiento:
        return None
    
    hoy = date.today()
    edad = hoy.year - fecha_nacimiento.year
    
    # Ajustar si aún no ha cumplido años este año
    if hoy.month < fecha_nacimiento.month or (hoy.month == fecha_nacimiento.month and hoy.day < fecha_nacimiento.day):
        edad -= 1
    
    return edad


def dias_habiles_entre(fecha_inicio, fecha_fin):
    """
    Calcula días hábiles entre dos fechas (excluyendo sábados y domingos)
    """
    dias_habiles = 0
    fecha_actual = fecha_inicio
    
    while fecha_actual <= fecha_fin:
        # 0 = Lunes, 6 = Domingo
        if fecha_actual.weekday() < 5:  # Lunes a Viernes
            dias_habiles += 1
        fecha_actual += timedelta(days=1)
    
    return dias_habiles


def es_festivo(fecha, festivos=[]):
    """
    Verifica si una fecha es festivo
    
    Args:
        fecha: Fecha a verificar
        festivos: Lista de fechas festivas
    """
    return fecha in festivos


def numero_a_letras(numero):
    """
    Convierte un número a letras (para certificaciones y desprendibles)
    Solo para valores comunes en nómina
    """
    # Implementación básica - se puede mejorar con librería num2words
    unidades = ['', 'UN', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
    # ... (implementación completa según necesidad)
    
    return f"{numero:,.0f}".replace(',', '.')  # Por ahora retorna formato numérico


def generar_numero_documento(prefijo, modelo):
    """
    Genera número de documento consecutivo
    
    Args:
        prefijo: Prefijo del documento (ej: 'CERT', 'CONT')
        modelo: Modelo para obtener el último número
    """
    ultimo = modelo.objects.order_by('-id').first()
    numero = 1 if not ultimo else ultimo.id + 1
    año = date.today().year
    
    return f"{prefijo}-{año}-{numero:05d}"


def validar_formato_documento(tipo_documento, numero):
    """
    Valida formato de documento según tipo
    """
    if tipo_documento == 'CC':
        # Cédula debe ser numérica
        return numero.isdigit() and len(numero) >= 6 and len(numero) <= 10
    elif tipo_documento == 'CE':
        # Cédula de extranjería
        return len(numero) >= 6
    elif tipo_documento == 'PA':
        # Pasaporte
        return len(numero) >= 6
    
    return True


def formatear_moneda(valor):
    """
    Formatea valor a moneda colombiana
    """
    return f"${valor:,.0f}".replace(',', '.')


def calcular_porcentaje_ausentismo(empleado, fecha_inicio, fecha_fin):
    """
    Calcula porcentaje de ausentismo de un empleado
    """
    from .models import Incapacidad, Permiso
    
    # Días totales del periodo
    dias_totales = (fecha_fin - fecha_inicio).days + 1
    
    # Días de incapacidad
    dias_incapacidad = Incapacidad.objects.filter(
        empleado=empleado,
        fecha_inicio__lte=fecha_fin,
        fecha_fin__gte=fecha_inicio
    ).aggregate(
        total=Sum('dias_incapacidad')
    )['total'] or 0
    
    # Días de permisos sin goce
    permisos_sin_goce = Permiso.objects.filter(
        empleado=empleado,
        fecha_inicio__lte=fecha_fin,
        fecha_fin__gte=fecha_inicio,
        con_goce_sueldo=False,
        aprobado=True
    )
    
    dias_permisos = sum([
        (p.fecha_fin - p.fecha_inicio).days + 1 
        for p in permisos_sin_goce
    ])
    
    # Calcular porcentaje
    dias_ausente = dias_incapacidad + dias_permisos
    if dias_totales > 0:
        porcentaje = (dias_ausente / dias_totales) * 100
        return round(porcentaje, 2)
    
    return 0


def generar_color_por_nivel(nivel):
    """
    Genera color según nivel (para gráficos y badges)
    """
    colores = {
        'bajo': '#28a745',
        'medio': '#ffc107',
        'alto': '#fd7e14',
        'muy_alto': '#dc3545',
        'critico': '#6f42c1',
    }
    return colores.get(nivel, '#6c757d')