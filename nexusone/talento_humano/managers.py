from django.db import models
from django.db.models import Q, Count, Avg, Sum, F
from datetime import date, timedelta

# ============================================================================
# MANAGERS PERSONALIZADOS
# ============================================================================

class EmpleadoManager(models.Manager):
    """Manager personalizado para Empleado"""
    
    def activos(self):
        """Empleados activos"""
        return self.filter(estado='activo')
    
    def inactivos(self):
        """Empleados inactivos"""
        return self.filter(estado='inactivo')
    
    def por_area(self, area):
        """Empleados por área"""
        return self.filter(area=area, estado='activo')
    
    def nuevos_ultimo_mes(self):
        """Empleados nuevos del último mes"""
        fecha_limite = date.today() - timedelta(days=30)
        return self.filter(fecha_ingreso__gte=fecha_limite)
    
    def cumpleañeros_mes(self, mes=None):
        """Empleados que cumplen años en el mes especificado"""
        if mes is None:
            mes = date.today().month
        return self.filter(fecha_nacimiento__month=mes, estado='activo')
    
    def con_contratos_por_vencer(self, dias=30):
        """Empleados con contratos por vencer"""
        fecha_limite = date.today() + timedelta(days=dias)
        return self.filter(
            contratos__activo=True,
            contratos__fecha_fin__lte=fecha_limite,
            contratos__fecha_fin__gte=date.today()
        ).distinct()
    
    def sin_seguridad_social(self):
        """Empleados sin seguridad social completa"""
        return self.filter(
            Q(eps__isnull=True) | 
            Q(afp__isnull=True) | 
            Q(arl__isnull=True)
        )


class ContratoManager(models.Manager):
    """Manager personalizado para Contrato"""
    
    def vigentes(self):
        """Contratos vigentes"""
        return self.filter(activo=True)
    
    def vencidos(self):
        """Contratos vencidos"""
        return self.filter(fecha_fin__lt=date.today(), activo=True)
    
    def por_vencer(self, dias=30):
        """Contratos por vencer en los próximos X días"""
        fecha_limite = date.today() + timedelta(days=dias)
        return self.filter(
            fecha_fin__gte=date.today(),
            fecha_fin__lte=fecha_limite,
            activo=True
        )
    
    def termino_indefinido(self):
        """Contratos a término indefinido"""
        return self.filter(tipo='indefinido', activo=True)
    
    def termino_fijo(self):
        """Contratos a término fijo"""
        return self.filter(tipo='fijo', activo=True)


class VacanteManager(models.Manager):
    """Manager personalizado para Vacante"""
    
    def abiertas(self):
        """Vacantes abiertas"""
        return self.filter(estado='abierta', fecha_cierre__gte=date.today())
    
    def cerradas(self):
        """Vacantes cerradas"""
        return self.filter(estado='cerrada')
    
    def en_proceso(self):
        """Vacantes en proceso"""
        return self.filter(estado='en_proceso')
    
    def con_candidatos(self):
        """Vacantes con candidatos aplicados"""
        return self.annotate(num_candidatos=Count('procesos')).filter(num_candidatos__gt=0)


class CapacitacionManager(models.Manager):
    """Manager personalizado para Capacitación"""
    
    def proximas(self):
        """Capacitaciones próximas"""
        return self.filter(
            fecha_programada__gte=date.today(),
            completada=False
        ).order_by('fecha_programada')
    
    def completadas(self):
        """Capacitaciones completadas"""
        return self.filter(completada=True)
    
    def del_mes(self, mes=None, año=None):
        """Capacitaciones de un mes específico"""
        if mes is None:
            mes = date.today().month
        if año is None:
            año = date.today().year
        return self.filter(
            fecha_programada__month=mes,
            fecha_programada__year=año
        )
    
    def por_tipo(self, tipo):
        """Capacitaciones por tipo"""
        return self.filter(tipo=tipo)


class AccidenteTrabajoManager(models.Manager):
    """Manager personalizado para Accidente de Trabajo"""
    
    def del_año(self, año=None):
        """Accidentes del año"""
        if año is None:
            año = date.today().year
        return self.filter(fecha_accidente__year=año)
    
    def graves(self):
        """Accidentes graves"""
        return self.filter(severidad__in=['grave', 'mortal'])
    
    def no_investigados(self):
        """Accidentes sin investigar"""
        return self.filter(fecha_investigacion__isnull=True)
    
    def no_reportados_arl(self):
        """Accidentes no reportados a ARL"""
        return self.filter(reportado_arl=False)


class PermisoManager(models.Manager):
    """Manager personalizado para Permiso"""
    
    def pendientes(self):
        """Permisos pendientes de aprobación"""
        return self.filter(aprobado=False)
    
    def aprobados(self):
        """Permisos aprobados"""
        return self.filter(aprobado=True)
    
    def del_mes(self, mes=None, año=None):
        """Permisos del mes"""
        if mes is None:
            mes = date.today().month
        if año is None:
            año = date.today().year
        return self.filter(
            fecha_inicio__month=mes,
            fecha_inicio__year=año
        )


class VacacionManager(models.Manager):
    """Manager personalizado para Vacación"""
    
    def pendientes(self):
        """Vacaciones pendientes"""
        return self.filter(aprobada=False)
    
    def aprobadas(self):
        """Vacaciones aprobadas"""
        return self.filter(aprobada=True)
    
    def proximas(self):
        """Vacaciones próximas (próximos 30 días)"""
        fecha_limite = date.today() + timedelta(days=30)
        return self.filter(
            fecha_inicio__gte=date.today(),
            fecha_inicio__lte=fecha_limite,
            aprobada=True
        )
    
    def en_curso(self):
        """Vacaciones en curso"""
        hoy = date.today()
        return self.filter(
            fecha_inicio__lte=hoy,
            fecha_fin__gte=hoy,
            aprobada=True
        )


class ExamenMedicoManager(models.Manager):
    """Manager personalizado para Examen Médico"""
    
    def vencidos(self):
        """Exámenes vencidos (más de 1 año)"""
        fecha_limite = date.today() - timedelta(days=365)
        return self.filter(
            fecha__lte=fecha_limite,
            empleado__estado='activo'
        )
    
    def proximos_vencer(self, dias=30):
        """Exámenes próximos a vencer"""
        fecha_inicio = date.today() - timedelta(days=365)
        fecha_fin = fecha_inicio + timedelta(days=dias)
        return self.filter(
            fecha__gte=fecha_inicio,
            fecha__lte=fecha_fin,
            empleado__estado='activo'
        )
    
    def por_tipo(self, tipo):
        """Exámenes por tipo"""
        return self.filter(tipo=tipo)