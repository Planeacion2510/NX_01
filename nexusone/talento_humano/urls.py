from django.urls import path
from . import views

app_name = 'talento_humano'

urlpatterns = [
    # ============================================================================
    # DASHBOARD
    # ============================================================================
    path('', views.dashboard_talento_humano, name='dashboard'),
    
    # ============================================================================
    # 1. ADMINISTRACIÓN DE PERSONAL - EMPLEADOS
    # ============================================================================
    path('empleados/', views.EmpleadoListView.as_view(), name='lista_empleados'),
    path('empleados/nuevo/', views.EmpleadoCreateView.as_view(), name='crear_empleado'),
    path('empleados/<int:pk>/', views.EmpleadoDetailView.as_view(), name='detalle_empleado'),
    path('empleados/<int:pk>/editar/', views.EmpleadoUpdateView.as_view(), name='editar_empleado'),
    path('empleados/<int:pk>/inactivar/', views.inactivar_empleado, name='inactivar_empleado'),
    
    # ============================================================================
    # CONTRATOS
    # ============================================================================
    path('contratos/', views.ContratoListView.as_view(), name='lista_contratos'),
    path('contratos/nuevo/', views.ContratoCreateView.as_view(), name='crear_contrato'),
    path('contratos/<int:pk>/renovar/', views.renovar_contrato, name='renovar_contrato'),
    
    # ============================================================================
    # CERTIFICACIONES
    # ============================================================================
    path('certificaciones/generar/', views.generar_certificacion, name='generar_certificacion'),
    path('certificaciones/generar/<int:empleado_id>/', views.generar_certificacion, name='generar_certificacion_empleado'),
    
    # ============================================================================
    # 3. SELECCIÓN Y TALENTO
    # ============================================================================
    
    # Perfiles de cargo
    path('perfiles-cargo/', views.PerfilCargoListView.as_view(), name='lista_perfiles_cargo'),
    path('perfiles-cargo/nuevo/', views.PerfilCargoCreateView.as_view(), name='crear_perfil_cargo'),
    path('perfiles-cargo/<int:pk>/', views.PerfilCargoDetailView.as_view(), name='detalle_perfil_cargo'),
    path('perfiles-cargo/<int:pk>/editar/', views.PerfilCargoUpdateView.as_view(), name='editar_perfil_cargo'),
    
    # Vacantes
    path('vacantes/', views.VacanteListView.as_view(), name='lista_vacantes'),
    path('vacantes/nueva/', views.VacanteCreateView.as_view(), name='crear_vacante'),
    path('vacantes/<int:pk>/', views.VacanteDetailView.as_view(), name='detalle_vacante'),
    path('vacantes/<int:pk>/editar/', views.VacanteUpdateView.as_view(), name='editar_vacante'),
    
    # Candidatos
    path('candidatos/', views.CandidatoListView.as_view(), name='lista_candidatos'),
    path('candidatos/nuevo/', views.CandidatoCreateView.as_view(), name='crear_candidato'),
    path('candidatos/<int:pk>/', views.CandidatoDetailView.as_view(), name='detalle_candidato'),
    
    # Proceso de selección
    path('proceso-seleccion/<int:proceso_id>/actualizar/', views.actualizar_etapa_candidato, name='actualizar_etapa_candidato'),
    
    # ============================================================================
    # 4. CAPACITACIÓN Y DESARROLLO
    # ============================================================================
    path('capacitaciones/', views.CapacitacionListView.as_view(), name='lista_capacitaciones'),
    path('capacitaciones/nueva/', views.CapacitacionCreateView.as_view(), name='crear_capacitacion'),
    path('capacitaciones/<int:pk>/', views.CapacitacionDetailView.as_view(), name='detalle_capacitacion'),
    path('capacitaciones/<int:pk>/editar/', views.CapacitacionUpdateView.as_view(), name='editar_capacitacion'),
    path('capacitaciones/<int:capacitacion_id>/inscribir/<int:empleado_id>/', views.inscribir_capacitacion, name='inscribir_capacitacion'),
    
    # ============================================================================
    # 5. SEGURIDAD Y SALUD EN EL TRABAJO
    # ============================================================================
    path('sst/', views.dashboard_sst, name='dashboard_sst'),
    
    # Matriz de riesgos
    path('sst/matriz-riesgos/', views.MatrizRiesgoListView.as_view(), name='matriz_riesgos'),
    path('sst/matriz-riesgos/nuevo/', views.MatrizRiesgoCreateView.as_view(), name='crear_riesgo'),
    path('sst/matriz-riesgos/<int:pk>/editar/', views.MatrizRiesgoUpdateView.as_view(), name='editar_riesgo'),
    
    # Exámenes médicos
    path('sst/examenes-medicos/', views.ExamenMedicoListView.as_view(), name='lista_examenes_medicos'),
    path('sst/examenes-medicos/nuevo/', views.ExamenMedicoCreateView.as_view(), name='crear_examen_medico'),
    path('sst/examenes-medicos/<int:pk>/', views.ExamenMedicoDetailView.as_view(), name='detalle_examen_medico'),
    
    # Accidentes de trabajo
    path('sst/accidentes/', views.AccidenteTrabajoListView.as_view(), name='lista_accidentes'),
    path('sst/accidentes/nuevo/', views.AccidenteTrabajoCreateView.as_view(), name='crear_accidente'),
    path('sst/accidentes/<int:pk>/', views.AccidenteTrabajoDetailView.as_view(), name='detalle_accidente'),
    path('sst/accidentes/<int:pk>/editar/', views.AccidenteTrabajoUpdateView.as_view(), name='editar_accidente'),
    
    # Elementos de protección (EPP)
    path('sst/epp/', views.ElementoProteccionListView.as_view(), name='lista_epp'),
    path('sst/epp/nuevo/', views.ElementoProteccionCreateView.as_view(), name='crear_epp'),
    path('sst/epp/<int:pk>/editar/', views.ElementoProteccionUpdateView.as_view(), name='editar_epp'),
    
    # Entregas de EPP
    path('sst/epp/entregas/', views.EntregaEPPListView.as_view(), name='lista_entregas_epp'),
    path('sst/epp/entregas/nueva/', views.EntregaEPPCreateView.as_view(), name='crear_entrega_epp'),
    
    # ============================================================================
    # 6. BIENESTAR LABORAL
    # ============================================================================
    path('bienestar/actividades/', views.ActividadBienestarListView.as_view(), name='lista_actividades_bienestar'),
    path('bienestar/actividades/nueva/', views.ActividadBienestarCreateView.as_view(), name='crear_actividad_bienestar'),
    path('bienestar/actividades/<int:pk>/', views.ActividadBienestarDetailView.as_view(), name='detalle_actividad_bienestar'),
    path('bienestar/actividades/<int:actividad_id>/inscribir/<int:empleado_id>/', views.inscribir_actividad_bienestar, name='inscribir_actividad_bienestar'),
    
    # Encuestas de clima
    path('bienestar/encuestas/', views.EncuestaClimaListView.as_view(), name='lista_encuestas_clima'),
    path('bienestar/encuestas/nueva/', views.EncuestaClimaCreateView.as_view(), name='crear_encuesta_clima'),
    path('bienestar/encuestas/<int:encuesta_id>/responder/', views.responder_encuesta_clima, name='responder_encuesta_clima'),
    path('bienestar/encuestas/<int:pk>/resultados/', views.resultados_encuesta_clima, name='resultados_encuesta_clima'),
    
    # ============================================================================
    # 7. GESTIÓN Y RELACIONES LABORALES
    # ============================================================================
    
    # Evaluaciones de desempeño
    path('evaluaciones/', views.EvaluacionDesempeñoListView.as_view(), name='lista_evaluaciones'),
    path('evaluaciones/nueva/', views.EvaluacionDesempeñoCreateView.as_view(), name='crear_evaluacion'),
    path('evaluaciones/<int:pk>/', views.EvaluacionDesempeñoDetailView.as_view(), name='detalle_evaluacion'),
    
    # Permisos
    path('permisos/', views.PermisoListView.as_view(), name='lista_permisos'),
    path('permisos/nuevo/', views.PermisoCreateView.as_view(), name='crear_permiso'),
    path('permisos/<int:pk>/aprobar/', views.aprobar_permiso, name='aprobar_permiso'),
    path('permisos/<int:pk>/rechazar/', views.rechazar_permiso, name='rechazar_permiso'),
    
    # Vacaciones
    path('vacaciones/', views.VacacionListView.as_view(), name='lista_vacaciones'),
    path('vacaciones/nueva/', views.VacacionCreateView.as_view(), name='crear_vacacion'),
    path('vacaciones/<int:pk>/aprobar/', views.aprobar_vacacion, name='aprobar_vacacion'),
    
    # Incapacidades
    path('incapacidades/', views.IncapacidadListView.as_view(), name='lista_incapacidades'),
    path('incapacidades/nueva/', views.IncapacidadCreateView.as_view(), name='crear_incapacidad'),
    path('incapacidades/<int:pk>/', views.IncapacidadDetailView.as_view(), name='detalle_incapacidad'),
    
    # Memorandos
    path('memorandos/', views.MemorandoListView.as_view(), name='lista_memorandos'),
    path('memorandos/nuevo/', views.MemorandoCreateView.as_view(), name='crear_memorando'),
    path('memorandos/<int:pk>/', views.MemorandoDetailView.as_view(), name='detalle_memorando'),
    
    # Reglamento interno
    path('reglamento/', views.ReglamentoInternoListView.as_view(), name='lista_reglamentos'),
    path('reglamento/<int:pk>/', views.ReglamentoInternoDetailView.as_view(), name='detalle_reglamento'),
    
    # ============================================================================
    # REPORTES Y EXPORTACIONES
    # ============================================================================
    path('reportes/empleados/excel/', views.exportar_empleados_excel, name='exportar_empleados_excel'),
    path('reportes/nomina/', views.reporte_nomina, name='reporte_nomina'),
    path('reportes/sst/', views.reporte_sst, name='reporte_sst'),
    
    # ============================================================================
    # API / AJAX
    # ============================================================================
    path('api/empleado/<int:pk>/info/', views.empleado_info_json, name='empleado_info_json'),
    path('api/calcular-liquidacion/', views.calcular_liquidacion_ajax, name='calcular_liquidacion_ajax'),
]