#!/usr/bin/env python
"""
Script para poblar la base de datos con datos de ejemplo.
Ejecutar desde Django shell: python manage.py shell < populate_db.py
O crear como comando de management.
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configurar Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from django.contrib.auth.models import User
from nomencladores.models import *
from registro.models import *


def clear_and_populate():
    """Limpia y puebla la base de datos con datos de ejemplo"""

    print("Iniciando población de la base de datos...")

    # 1. NOMENCLADORES BÁSICOS
    print("Creando nomencladores básicos...")

    # TipoEntidad
    TipoEntidad.objects.all().delete()
    tipos_entidad = [
        "Ministerio", "Instituto", "Empresa Estatal", "ONG", "Universidad"
    ]
    for nombre in tipos_entidad:
        TipoEntidad.objects.create(nombre=nombre)

    # Cargo
    Cargo.objects.all().delete()
    cargos = [
        "Director General", "Subdirector", "Jefe de Departamento",
        "Especialista", "Técnico"
    ]
    for nombre in cargos:
        Cargo.objects.create(nombre=nombre)

    # Sector
    Sector.objects.all().delete()
    sectores = [
        "Agricultura", "Energía", "Transporte", "Industria", "Turismo"
    ]
    for nombre in sectores:
        Sector.objects.create(nombre=nombre)

    # TipoAccion
    TipoAccion.objects.all().delete()
    tipos_accion_data = [
        ("Mitigación", "Acciones para reducir emisiones de GEI", 1),
        ("Adaptación", "Acciones para adaptarse al cambio climático", 2),
        ("Transversal", "Acciones que combinan mitigación y adaptación", 3),
        ("Investigación", "Proyectos de investigación climática", 4),
        ("Capacitación", "Programas de formación y capacitación", 5)
    ]
    for nombre, tooltip, orden in tipos_accion_data:
        TipoAccion.objects.create(nombre=nombre, info_tooltip=tooltip, orden=orden)

    # TipoIndicador
    TipoIndicador.objects.all().delete()
    tipos_indicador_data = [
        ("Impacto", "Indicadores de impacto final", 1),
        ("Resultado", "Indicadores de resultado intermedio", 2),
        ("Proceso", "Indicadores de proceso o actividad", 3),
        ("Contexto", "Indicadores de contexto o entorno", 4),
        ("Eficiencia", "Indicadores de eficiencia o productividad", 5)
    ]
    for nombre, tooltip, orden in tipos_indicador_data:
        TipoIndicador.objects.create(nombre=nombre, info_tooltip=tooltip, orden=orden)

    # Escala
    Escala.objects.all().delete()
    escalas = ["Nacional", "Provincial", "Municipal", "Local", "Internacional"]
    for nombre in escalas:
        Escala.objects.create(nombre=nombre)

    # Alcance
    Alcance.objects.all().delete()
    alcances = ["Corto plazo", "Mediano plazo", "Largo plazo", "Permanente", "Temporal"]
    for nombre in alcances:
        Alcance.objects.create(nombre=nombre)

    # TipoMoneda
    TipoMoneda.objects.all().delete()
    monedas_data = [
        ("Peso Cubano (CUP)", "Moneda nacional de Cuba", 1),
        ("Dólar Estadounidense (USD)", "Moneda internacional de referencia", 2),
        ("Euro (EUR)", "Moneda europea", 3),
        ("Yuan Chino (CNY)", "Moneda china", 4),
        ("Peso Mexicano (MXN)", "Moneda mexicana", 5)
    ]
    for nombre, tooltip, orden in monedas_data:
        TipoMoneda.objects.create(nombre=nombre, info_tooltip=tooltip, orden=orden)

    # TipoPresupuesto
    TipoPresupuesto.objects.all().delete()
    tipos_presupuesto_data = [
        ("Inversión", "Presupuesto para inversiones de capital", 1),
        ("Operacional", "Presupuesto para gastos operacionales", 2),
        ("Investigación", "Presupuesto para actividades de I+D", 3),
        ("Capacitación", "Presupuesto para formación de personal", 4),
        ("Equipamiento", "Presupuesto para compra de equipos", 5)
    ]
    for nombre, tooltip, orden in tipos_presupuesto_data:
        TipoPresupuesto.objects.create(nombre=nombre, info_tooltip=tooltip, orden=orden)

    # Escenario
    Escenario.objects.all().delete()
    escenarios = [
        "Escenario Base", "Escenario Optimista", "Escenario Pesimista",
        "Escenario Intermedio", "Escenario de Crisis"
    ]
    for nombre in escenarios:
        Escenario.objects.create(nombre=nombre)

    # CategoriaPresupuesto
    CategoriaPresupuesto.objects.all().delete()
    categorias = [
        "Personal", "Materiales", "Servicios", "Equipamiento", "Infraestructura"
    ]
    for nombre in categorias:
        CategoriaPresupuesto.objects.create(nombre=nombre)

    # EstadoAccion
    EstadoAccion.objects.all().delete()
    estados_accion_data = [
        ("Planificada", 1), ("En Ejecución", 2), ("Suspendida", 3),
        ("Completada", 4), ("Cancelada", 5)
    ]
    for nombre, orden in estados_accion_data:
        EstadoAccion.objects.create(nombre=nombre, orden=orden)

    # EstadoPresupuesto
    EstadoPresupuesto.objects.all().delete()
    estados_presupuesto_data = [
        ("Aprobado", 1), ("Pendiente", 2), ("Ejecutado", 3),
        ("Suspendido", 4), ("Rechazado", 5)
    ]
    for nombre, orden in estados_presupuesto_data:
        EstadoPresupuesto.objects.create(nombre=nombre, orden=orden)

    # ProgramaProductivo
    ProgramaProductivo.objects.all().delete()
    programas_productivos = [
        "Programa Agrícola Sostenible", "Programa Industrial Verde",
        "Programa Energético Renovable", "Programa Turismo Sostenible",
        "Programa Pesca Responsable"
    ]
    for nombre in programas_productivos:
        ProgramaProductivo.objects.create(nombre=nombre)

    # ProgramaApoyo
    ProgramaApoyo.objects.all().delete()
    programas_apoyo = [
        "Programa de Financiamiento Climático", "Programa de Cooperación Internacional",
        "Programa de Desarrollo Tecnológico", "Programa de Formación Técnica",
        "Programa de Investigación Aplicada"
    ]
    for nombre in programas_apoyo:
        ProgramaApoyo.objects.create(nombre=nombre)

    # UnidadMedidaIndicador
    UnidadMedidaIndicador.objects.all().delete()
    unidades_data = [
        ("Toneladas de CO2 equivalente", "tCO2eq"),
        ("Kilowatt hora", "kWh"),
        ("Metros cúbicos", "m³"),
        ("Hectáreas", "ha"),
        ("Porcentaje", "%")
    ]
    for nombre, sigla in unidades_data:
        UnidadMedidaIndicador.objects.create(nombre=nombre, sigla=sigla)

    # EnfoqueIPCC
    EnfoqueIPCC.objects.all().delete()
    enfoques = [
        "Energía", "Procesos Industriales", "Agricultura",
        "Cambio de Uso de Suelo", "Residuos"
    ]
    for nombre in enfoques:
        EnfoqueIPCC.objects.create(nombre=nombre)

    # ObjetivosDesarrolloSostenible
    ObjetivosDesarrolloSostenible.objects.all().delete()
    ods = [
        "ODS 7: Energía Asequible y No Contaminante",
        "ODS 13: Acción por el Clima",
        "ODS 15: Vida de Ecosistemas Terrestres",
        "ODS 6: Agua Limpia y Saneamiento",
        "ODS 11: Ciudades y Comunidades Sostenibles"
    ]
    for nombre in ods:
        ObjetivosDesarrolloSostenible.objects.create(nombre=nombre)

    # AmenazaClimatica
    AmenazaClimatica.objects.all().delete()
    amenazas = [
        "Aumento del nivel del mar", "Sequías prolongadas",
        "Huracanes intensos", "Inundaciones", "Olas de calor"
    ]
    for nombre in amenazas:
        AmenazaClimatica.objects.create(nombre=nombre)

    # FrecuenciaMedicion
    FrecuenciaMedicion.objects.all().delete()
    frecuencias_data = [
        ("Medición Mensual", 1, "meses"),
        ("Medición Trimestral", 3, "meses"),
        ("Medición Semestral", 6, "meses"),
        ("Medición Anual", 1, "años"),
        ("Medición Semanal", 1, "semanas")
    ]
    for nombre, cantidad, unidad in frecuencias_data:
        FrecuenciaMedicion.objects.create(nombre=nombre, cantidad=cantidad, unidad=unidad)

    # VariableIndicador
    VariableIndicador.objects.all().delete()
    variables_data = [
        ("Emisiones totales", "emisiones_total"),
        ("Consumo energético", "consumo_energia"),
        ("Área reforestada", "area_reforestacion"),
        ("Población beneficiada", "poblacion_beneficiada"),
        ("Inversión ejecutada", "inversion_ejecutada")
    ]
    for nombre, variable in variables_data:
        VariableIndicador.objects.create(nombre=nombre, variable=variable)

    print("Nomencladores básicos creados exitosamente.")

    # 2. ENTIDADES
    print("Creando entidades...")
    Entidad.objects.all().delete()

    # Obtener municipios existentes (asumiendo que existen)
    municipios = list(Municipio.objects.all()[:5]) if Municipio.objects.exists() else [None] * 5

    entidades_data = [
        ("Ministerio de Ciencia, Tecnología y Medio Ambiente", "Calle 20 No. 514", "citma@example.cu"),
        ("Instituto de Meteorología", "Calle 17 No. 4026", "insmet@example.cu"),
        ("Centro de Investigaciones de Energía Solar", "Ave. 47 No. 2818", "cies@example.cu"),
        ("Empresa Nacional de Flora y Fauna", "Calle 18A No. 4108", "flora_fauna@example.cu"),
        ("Instituto de Planificación Física", "Calle 7ma No. 4455", "ipf@example.cu")
    ]

    for i, (nombre, direccion, correo) in enumerate(entidades_data):
        Entidad.objects.create(
            nombre=nombre,
            direccion=direccion,
            correo=correo,
            municipio=municipios[i] if municipios[i] else None
        )

    print("Entidades creadas exitosamente.")


    # 4. COBENEFICIOS
    print("Creando cobeneficios...")
    Cobeneficio.objects.all().delete()

    cobeneficios_data = [
        ("Reducción de contaminación del aire", "Disminución de emisiones de partículas", True),
        ("Mejora de la salud pública", "Reducción de enfermedades respiratorias", True),
        ("Creación de empleos verdes", "Generación de nuevos puestos de trabajo", False),
        ("Conservación de la biodiversidad", "Protección de especies nativas", True),
        ("Ahorro energético", "Reducción del consumo de combustibles", False)
    ]

    for nombre, descripcion, cumplimiento in cobeneficios_data:
        Cobeneficio.objects.create(
            nombre=nombre,
            descripcion=descripcion,
            cumplimiento=cumplimiento
        )

    # 5. INDICADORES
    print("Creando indicadores...")
    Indicador.objects.all().delete()

    tipos_indicador = list(TipoIndicador.objects.all())
    unidades_medida = list(UnidadMedidaIndicador.objects.all())
    enfoques_ipcc = list(EnfoqueIPCC.objects.all())
    frecuencias = list(FrecuenciaMedicion.objects.all())
    variables = list(VariableIndicador.objects.all())

    indicadores_data = [
        ("Reducción de emisiones GEI", "Cantidad de CO2eq reducidas anualmente",
         "Fuente: Inventarios nacionales", "Emisiones base - Emisiones actuales"),
        ("Eficiencia energética", "Mejora porcentual en eficiencia energética",
         "Fuente: Sistema energético nacional", "(Consumo anterior - Consumo actual) / Consumo anterior * 100"),
        ("Área de bosques restaurados", "Hectáreas de bosque restauradas o reforestadas",
         "Fuente: Servicio Forestal Nacional", "Suma de áreas restauradas en el período"),
        ("Población beneficiada por adaptación", "Número de personas beneficiadas",
         "Fuente: Censos y registros locales", "Conteo directo de beneficiarios"),
        ("Inversión climática ejecutada", "Monto de inversión climática realizada",
         "Fuente: Registros financieros", "Suma de inversiones ejecutadas")
    ]

    for i, (nombre, descripcion, fuente, formula) in enumerate(indicadores_data):
        indicador = Indicador.objects.create(
            nombre=nombre,
            tipo_indicador=tipos_indicador[i],
            descripcion=descripcion,
            fuente_indicador=fuente,
            formula=formula,
            unidad_medida=unidades_medida[i],
            enfoqueIPCC=enfoques_ipcc[i] if i < len(enfoques_ipcc) else None,
            frecuencia_medicion=frecuencias[i]
        )

        # Agregar variables al indicador
        if i < len(variables):
            indicador.variable_indicador.add(variables[i])

    # 6. RESULTADOS DE INDICADORES
    print("Creando resultados de indicadores...")
    ResultadoIndicador.objects.all().delete()

    for i in range(5):
        fecha_resultado = date.today() - timedelta(days=30 * i)
        resultado = ResultadoIndicador.objects.create(
            fuente_dato=f"Sistema de monitoreo {i + 1}",
            valor=100.5 + (i * 25.3),
            observacion=f"Resultado del período {i + 1}",
            fecha=fecha_resultado
        )

        # Agregar variables al resultado
        if i < len(variables):
            resultado.variable_indicador.add(variables[i])

    # 7. RESULTADOS DE VARIABLES
    print("Creando resultados de variables...")
    ResultadoVariable.objects.all().delete()

    resultados = list(ResultadoIndicador.objects.all())
    for i in range(min(5, len(resultados), len(variables))):
        ResultadoVariable.objects.create(
            resultado=resultados[i],
            variable_indicador=variables[i],
            valor=50.25 + (i * 10.75)
        )

    # 8. RESULTADOS DE ACCIONES
    print("Creando resultados de acciones...")
    ResultadoAccion.objects.all().delete()

    resultados_accion = [
        "Se logró una reducción del 15% en las emisiones de GEI del sector",
        "Se implementaron 3 tecnologías limpias en la industria local",
        "Se capacitaron 150 técnicos en tecnologías ambientales",
        "Se establecieron 5 estaciones de monitoreo climático",
        "Se desarrolló un plan de contingencia ante eventos extremos"
    ]

    for descripcion in resultados_accion:
        ResultadoAccion.objects.create(descripcion=descripcion)

    # 9. PRESUPUESTOS EJECUTADOS
    print("Creando presupuestos ejecutados...")
    PresupuestoEjecutado.objects.all().delete()

    for i in range(5):
        fecha_inicio = date.today() - timedelta(days=90 * (i + 1))
        fecha_fin = fecha_inicio + timedelta(days=60)
        PresupuestoEjecutado.objects.create(
            monto=50000.0 + (i * 25000.0),
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            observacion=f"Ejecución presupuestaria período {i + 1}"
        )

    # 10. PRESUPUESTOS PLANIFICADOS
    print("Creando presupuestos planificados...")
    PresupuestoPlanificado.objects.all().delete()

    tipos_presupuesto = list(TipoPresupuesto.objects.all())
    tipos_moneda = list(TipoMoneda.objects.all())
    estados_presupuesto = list(EstadoPresupuesto.objects.all())
    categorias = list(CategoriaPresupuesto.objects.all())
    presupuestos_ejecutados = list(PresupuestoEjecutado.objects.all())

    for i in range(5):
        presupuesto = PresupuestoPlanificado.objects.create(
            tipo_presupuesto=tipos_presupuesto[i],
            tipo_moneda=tipos_moneda[i],
            monto=100000.0 + (i * 50000.0),
            fuente_financiamiento=f"Fuente de financiamiento {i + 1}",
            estado_presupuesto=estados_presupuesto[i],
            categoria=categorias[i]
        )

        # Agregar presupuestos ejecutados
        if i < len(presupuestos_ejecutados):
            presupuesto.presupuestos_ejecutados.add(presupuestos_ejecutados[i])

    # 11. ACCIONES
    print("Creando acciones...")
    Accion.objects.all().delete()

    # Obtener usuarios existentes o usar el primer admin
    try:
        usuario = User.objects.filter(is_superuser=True).first()
        if not usuario:
            usuario = User.objects.first()
        if not usuario:
            print("Advertencia: No se encontraron usuarios. Creando usuario admin por defecto.")
            usuario = User.objects.create_user('admin', 'admin@example.com', 'admin123')
    except:
        print("Error al obtener usuario. Saltando creación de acciones.")
        return

    tipos_accion = list(TipoAccion.objects.all())
    sectores = list(Sector.objects.all())
    escenarios = list(Escenario.objects.all())
    alcances = list(Alcance.objects.all())
    escalas = list(Escala.objects.all())
    estados_accion = list(EstadoAccion.objects.all())
    entidades = list(Entidad.objects.all())
    programas_apoyo = list(ProgramaApoyo.objects.all())
    programas_productivos = list(ProgramaProductivo.objects.all())
    provincias = list(Provincia.objects.all()[:3]) if Provincia.objects.exists() else []

    acciones_data = [
        ("Proyecto de Energías Renovables", "Desarrollar capacidades en energías renovables",
         "Instalación de paneles solares en edificaciones públicas", "Reducir dependencia de combustibles fósiles"),
        ("Plan de Adaptación Costera", "Fortalecer defensas costeras",
         "Construcción de diques y restauración de manglares", "Proteger comunidades costeras"),
        ("Programa de Agricultura Sostenible", "Promover prácticas agrícolas sostenibles",
         "Capacitación a productores en técnicas agroecológicas", "Aumentar productividad y sostenibilidad"),
        ("Sistema de Alerta Temprana", "Implementar sistema de monitoreo climático",
         "Instalación de estaciones meteorológicas automáticas", "Mejorar capacidad de respuesta"),
        ("Reforestación Urbana", "Incrementar cobertura vegetal urbana",
         "Plantación de árboles en áreas urbanas y periurbanas", "Mejorar calidad del aire")
    ]

    presupuestos_planificados = list(PresupuestoPlanificado.objects.all())
    indicadores = list(Indicador.objects.all())
    cobeneficios = list(Cobeneficio.objects.all())
    resultados_accion = list(ResultadoAccion.objects.all())

    for i, (nombre, objetivo, descripcion, meta) in enumerate(acciones_data):
        fecha_inicio = date.today() - timedelta(days=180)
        fecha_fin = date.today() + timedelta(days=365)

        accion = Accion.objects.create(
            user=usuario,
            tipo_accion=tipos_accion[i],
            nombre=nombre,
            objetivo=objetivo,
            descripcion=descripcion,
            sector=sectores[i],
            escenario=escenarios[i] if i < len(escenarios) else None,
            alcance=alcances[i] if i < len(alcances) else None,
            escala=escalas[i] if i < len(escalas) else None,
            lugar_intervencion=f"Región {i + 1}",
            meta=meta,
            publicado=True,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado_accion=estados_accion[i] if i < len(estados_accion) else None,
            entidad_responsable=entidades[i] if i < len(entidades) else None,
            programa_apoyo=programas_apoyo[i] if i < len(programas_apoyo) else None,
            programa_productivo=programas_productivos[i] if i < len(programas_productivos) else None
        )

        # Agregar relaciones ManyToMany
        if provincias:
            accion.provincia.add(provincias[i % len(provincias)])

        if entidades and len(entidades) > 1:
            accion.otras_entidades.add(entidades[(i + 1) % len(entidades)])

        if i < len(presupuestos_planificados):
            accion.presupuestos_planificados.add(presupuestos_planificados[i])

        if i < len(indicadores):
            accion.indicadores.add(indicadores[i])

        if i < len(cobeneficios):
            accion.cobeneficios.add(cobeneficios[i])

        if i < len(resultados_accion):
            accion.resultados_accion.add(resultados_accion[i])

    print("Acciones creadas exitosamente.")

    # Agregar resultados a indicadores
    print("Vinculando resultados a indicadores...")
    indicadores_list = list(Indicador.objects.all())
    resultados_list = list(ResultadoIndicador.objects.all())

    for i, indicador in enumerate(indicadores_list):
        if i < len(resultados_list):
            indicador.resultados.add(resultados_list[i])

        # Actualizar última medición
        ultimo_resultado = indicador.resultados.order_by('-fecha').first()
        if ultimo_resultado:
            indicador.ultima_medicion = ultimo_resultado.fecha
            indicador.save()

    print("✅ Base de datos poblada exitosamente!")
    print(f"✅ Creados {TipoAccion.objects.count()} tipos de acción")
    print(f"✅ Creados {Sector.objects.count()} sectores")
    print(f"✅ Creados {Entidad.objects.count()} entidades")
    print(f"✅ Creados {Indicador.objects.count()} indicadores")
    print(f"✅ Creados {Accion.objects.count()} acciones")
    print(f"✅ Creados {PresupuestoPlanificado.objects.count()} presupuestos planificados")
    print(f"✅ Creados {ResultadoIndicador.objects.count()} resultados de indicadores")


if __name__ == "__main__":
    clear_and_populate()