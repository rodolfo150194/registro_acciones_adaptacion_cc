#!/usr/bin/env python
"""
Script para poblar la base de datos con datos realistas de ejemplo.

Uso:
    1. Desde raíz del proyecto: python poblar_bd.py
    2. Como comando Django: python manage.py shell < poblar_bd.py
    3. Desde Django shell: exec(open('poblar_bd.py').read())
"""

import os
import sys
import django
from datetime import date, timedelta
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from nomencladores.models import *
from registro.models import *


def crear_presupuestos_accion(accion, monto_total, estado_accion):
    """Crea presupuestos planificados y ejecutados para una acción"""
    tipos_presupuesto = list(TipoPresupuesto.objects.all())
    tipos_moneda = list(TipoMoneda.objects.all())
    estados_presupuesto = list(EstadoPresupuesto.objects.all())
    categorias = list(CategoriaPresupuesto.objects.all())

    # Distribuir presupuesto en 2-3 categorías
    num_categorias = random.randint(2, 3)
    categorias_seleccionadas = random.sample(categorias, num_categorias)

    # Dividir monto
    porcentajes = [random.uniform(0.2, 0.5) for _ in range(num_categorias)]
    total_porcentaje = sum(porcentajes)
    porcentajes = [p / total_porcentaje for p in porcentajes]

    for i, categoria in enumerate(categorias_seleccionadas):
        monto = monto_total * porcentajes[i]

        presupuesto_plan = PresupuestoPlanificado.objects.create(
            tipo_presupuesto=random.choice(tipos_presupuesto),
            tipo_moneda=random.choice(tipos_moneda),
            monto=round(monto, 2),
            fuente_financiamiento=random.choice([
                "Presupuesto Nacional",
                "Cooperación Internacional",
                "Fondo Climático Verde",
                "Banco Mundial",
                "PNUD"
            ]),
            estado_presupuesto=estados_presupuesto[0],
            categoria=categoria
        )

        accion.presupuestos_planificados.add(presupuesto_plan)

        # Determinar porcentaje de ejecución
        if estado_accion == 3:  # Completada
            porcentaje_ejecucion = random.uniform(0.9, 1.0)
        elif estado_accion == 1:  # En ejecución
            if random.random() < 0.3:
                porcentaje_ejecucion = random.uniform(0.1, 0.3)  # Baja (problema)
            else:
                porcentaje_ejecucion = random.uniform(0.5, 0.8)
        elif estado_accion == 0:  # Planificada
            porcentaje_ejecucion = random.uniform(0.0, 0.1)
        else:
            porcentaje_ejecucion = random.uniform(0.3, 0.6)

        # Crear ejecuciones
        num_ejecuciones = random.randint(1, 3)
        monto_restante = monto * porcentaje_ejecucion

        for j in range(num_ejecuciones):
            monto_ejecutado = monto_restante / num_ejecuciones

            dias_desde_inicio = (date.today() - accion.fecha_inicio).days
            if dias_desde_inicio > 0:
                dias_inicio_ejec = random.randint(0, min(dias_desde_inicio, 180))
                dias_fin_ejec = dias_inicio_ejec + random.randint(30, 90)

                fecha_inicio_ejec = accion.fecha_inicio + timedelta(days=dias_inicio_ejec)
                fecha_fin_ejec = accion.fecha_inicio + timedelta(days=dias_fin_ejec)

                presupuesto_ejec = PresupuestoEjecutado.objects.create(
                    monto=round(monto_ejecutado, 2),
                    fecha_inicio=fecha_inicio_ejec,
                    fecha_fin=fecha_fin_ejec,
                    observacion=f"Ejecución período {j + 1}"
                )

                presupuesto_plan.presupuestos_ejecutados.add(presupuesto_ejec)


def crear_nomencladores():
    """Crea todos los nomencladores básicos"""
    print("\n[1/12] Creando nomencladores básicos...")

    # TipoEntidad
    TipoEntidad.objects.all().delete()
    for nombre in ["Ministerio", "Instituto", "Empresa Estatal", "ONG", "Universidad"]:
        TipoEntidad.objects.create(nombre=nombre)

    # Cargo
    Cargo.objects.all().delete()
    for nombre in ["Director General", "Subdirector", "Jefe de Departamento", "Especialista", "Técnico"]:
        Cargo.objects.create(nombre=nombre)

    # Sector
    Sector.objects.all().delete()
    sectores = [
        "Agricultura y Ganadería", "Energía y Recursos Naturales", "Transporte",
        "Industria", "Turismo", "Recursos Hídricos", "Zonas Costeras",
        "Salud", "Biodiversidad y Ecosistemas"
    ]
    for nombre in sectores:
        Sector.objects.create(nombre=nombre)

    # TipoAccion
    TipoAccion.objects.all().delete()
    tipos_accion = [
        ("Mitigación", "Acciones para reducir emisiones de GEI", 1),
        ("Adaptación", "Acciones para adaptarse al cambio climático", 2),
        ("Transversal", "Acciones que combinan mitigación y adaptación", 3),
        ("Investigación", "Proyectos de investigación climática", 4),
        ("Capacitación", "Programas de formación y capacitación", 5)
    ]
    for nombre, tooltip, orden in tipos_accion:
        TipoAccion.objects.create(nombre=nombre, info_tooltip=tooltip, orden=orden)

    # TipoIndicador
    TipoIndicador.objects.all().delete()
    tipos_indicador = [
        ("Impacto", "Indicadores de impacto final", 1),
        ("Resultado", "Indicadores de resultado intermedio", 2),
        ("Proceso", "Indicadores de proceso o actividad", 3),
        ("Contexto", "Indicadores de contexto o entorno", 4),
        ("Eficiencia", "Indicadores de eficiencia o productividad", 5)
    ]
    for nombre, tooltip, orden in tipos_indicador:
        TipoIndicador.objects.create(nombre=nombre, info_tooltip=tooltip, orden=orden)

    # Escala
    Escala.objects.all().delete()
    for nombre in ["Local", "Municipal", "Provincial", "Nacional", "Regional"]:
        Escala.objects.create(nombre=nombre)

    # Alcance
    Alcance.objects.all().delete()
    for nombre in ["Corto Plazo (1-2 años)", "Mediano Plazo (3-5 años)", "Largo Plazo (>5 años)"]:
        Alcance.objects.create(nombre=nombre)

    # Escenario
    Escenario.objects.all().delete()
    for nombre in ["RCP 2.6", "RCP 4.5", "RCP 6.0", "RCP 8.5", "Línea Base"]:
        Escenario.objects.create(nombre=nombre)

    # TipoMoneda
    TipoMoneda.objects.all().delete()
    monedas = [
        ("Peso Cubano", "CUP", "$", True),
        ("Dólar Estadounidense", "USD", "$", True),
        ("Euro", "EUR", "€", True)
    ]
    for nombre, sigla, simbolo, estado in monedas:
        TipoMoneda.objects.create(nombre=nombre, sigla=sigla, simbolo=simbolo, estado=estado)

    # TipoPresupuesto
    TipoPresupuesto.objects.all().delete()
    for nombre, orden in [("Inversión", 1), ("Operativo", 2), ("Mantenimiento", 3), ("Investigación", 4),
                          ("Capacitación", 5)]:
        TipoPresupuesto.objects.create(nombre=nombre, orden=orden)

    # CategoriaPresupuesto
    CategoriaPresupuesto.objects.all().delete()
    for nombre in ["Recursos Humanos", "Equipamiento", "Infraestructura", "Servicios", "Materiales", "Tecnología"]:
        CategoriaPresupuesto.objects.create(nombre=nombre)

    # EstadoAccion
    EstadoAccion.objects.all().delete()
    for nombre, orden in [("Planificada", 1), ("En Ejecución", 2), ("Suspendida", 3), ("Completada", 4),
                          ("Cancelada", 5)]:
        EstadoAccion.objects.create(nombre=nombre, orden=orden)

    # EstadoPresupuesto
    EstadoPresupuesto.objects.all().delete()
    for nombre, orden in [("Aprobado", 1), ("Pendiente", 2), ("Ejecutado", 3), ("Suspendido", 4), ("Rechazado", 5)]:
        EstadoPresupuesto.objects.create(nombre=nombre, orden=orden)

    # ProgramaProductivo y ProgramaApoyo
    ProgramaProductivo.objects.all().delete()
    for nombre in ["Programa Agrícola Sostenible", "Programa Industrial Verde", "Programa Energético Renovable",
                   "Programa Turismo Sostenible", "Programa Pesca Responsable"]:
        ProgramaProductivo.objects.create(nombre=nombre)

    ProgramaApoyo.objects.all().delete()
    for nombre in ["Programa de Financiamiento Climático", "Programa de Cooperación Internacional",
                   "Programa de Desarrollo Tecnológico", "Programa de Formación Técnica",
                   "Programa de Investigación Aplicada"]:
        ProgramaApoyo.objects.create(nombre=nombre)

    # UnidadMedidaIndicador
    UnidadMedidaIndicador.objects.all().delete()
    unidades = [
        ("Toneladas de CO2 equivalente", "tCO2eq"), ("Kilowatt hora", "kWh"),
        ("Metros cúbicos", "m³"), ("Hectáreas", "ha"), ("Porcentaje", "%"),
        ("Personas", "pers"), ("Millones de pesos", "MM $"), ("Kilómetros", "km"), ("Unidades", "u")
    ]
    for nombre, sigla in unidades:
        UnidadMedidaIndicador.objects.create(nombre=nombre, sigla=sigla)

    # EnfoqueIPCC
    EnfoqueIPCC.objects.all().delete()
    for nombre in ["Energía", "Procesos Industriales", "Agricultura", "Cambio de Uso de Suelo", "Residuos"]:
        EnfoqueIPCC.objects.create(nombre=nombre)

    # ODS
    ObjetivosDesarrolloSostenible.objects.all().delete()
    for nombre in ["ODS 7: Energía Asequible y No Contaminante", "ODS 13: Acción por el Clima",
                   "ODS 15: Vida de Ecosistemas Terrestres", "ODS 6: Agua Limpia y Saneamiento",
                   "ODS 11: Ciudades y Comunidades Sostenibles", "ODS 2: Hambre Cero", "ODS 14: Vida Submarina"]:
        ObjetivosDesarrolloSostenible.objects.create(nombre=nombre)

    # AmenazaClimatica
    AmenazaClimatica.objects.all().delete()
    for nombre in ["Aumento del nivel del mar", "Sequías prolongadas", "Huracanes intensos", "Inundaciones",
                   "Olas de calor", "Erosión costera", "Salinización"]:
        AmenazaClimatica.objects.create(nombre=nombre)

    # FrecuenciaMedicion
    FrecuenciaMedicion.objects.all().delete()
    frecuencias = [
        ("Medición Mensual", 1, "meses"), ("Medición Trimestral", 3, "meses"),
        ("Medición Semestral", 6, "meses"), ("Medición Anual", 1, "años"), ("Medición Semanal", 1, "semanas")
    ]
    for nombre, cantidad, unidad in frecuencias:
        FrecuenciaMedicion.objects.create(nombre=nombre, cantidad=cantidad, unidad=unidad)

    # VariableIndicador
    VariableIndicador.objects.all().delete()
    variables = [
        ("Emisiones totales", "emisiones_total"), ("Consumo energético", "consumo_energia"),
        ("Área reforestada", "area_reforestacion"), ("Población beneficiada", "poblacion_beneficiada"),
        ("Inversión ejecutada", "inversion_ejecutada"), ("Cantidad producida", "cantidad_prod"),
        ("Eficiencia obtenida", "eficiencia"), ("Reducción lograda", "reduccion")
    ]
    for nombre, variable in variables:
        VariableIndicador.objects.create(nombre=nombre, variable=variable)

    print(f"✓ Creados {Sector.objects.count()} sectores")
    print(f"✓ Creados {TipoIndicador.objects.count()} tipos de indicador")


def crear_entidades():
    """Crea entidades responsables"""
    print("\n[2/12] Creando entidades...")
    Entidad.objects.all().delete()

    entidades = [
        ("Ministerio de Ciencia, Tecnología y Medio Ambiente", "Calle 20 No. 514", "citma@example.cu"),
        ("Instituto de Meteorología", "Calle 17 No. 4026", "insmet@example.cu"),
        ("Centro de Investigaciones de Energía Solar", "Ave. 47 No. 2818", "cies@example.cu"),
        ("Empresa Nacional de Flora y Fauna", "Calle 18A No. 4108", "flora_fauna@example.cu"),
        ("Instituto de Planificación Física", "Calle 7ma No. 4455", "ipf@example.cu"),
        ("Instituto Nacional de Recursos Hidráulicos", "Ave. Rancho Boyeros", "inrh@example.cu"),
        ("Ministerio de Agricultura", "Ave. Independencia 10512", "minag@example.cu"),
        ("Centro de Estudios Ambientales de Cienfuegos", "Calle 37 No. 4604", "ceac@example.cu")
    ]

    for nombre, direccion, correo in entidades:
        Entidad.objects.create(nombre=nombre, direccion=direccion, correo=correo)

    print(f"✓ Creadas {Entidad.objects.count()} entidades")


def crear_cobeneficios():
    """Crea cobeneficios"""
    print("\n[3/12] Creando cobeneficios...")
    Cobeneficio.objects.all().delete()

    cobeneficios = [
        ("Reducción de contaminación del aire", "Disminución de emisiones de partículas", True),
        ("Mejora de la salud pública", "Reducción de enfermedades respiratorias", True),
        ("Creación de empleos verdes", "Generación de nuevos puestos de trabajo", False),
        ("Conservación de la biodiversidad", "Protección de especies nativas", True),
        ("Ahorro energético", "Reducción del consumo de combustibles", False),
        ("Seguridad alimentaria", "Aumento de la producción local sostenible", True),
        ("Protección de recursos hídricos", "Mejora en la gestión del agua", True)
    ]

    for nombre, descripcion, cumplimiento in cobeneficios:
        Cobeneficio.objects.create(nombre=nombre, descripcion=descripcion, cumplimiento=cumplimiento)

    print(f"✓ Creados {Cobeneficio.objects.count()} cobeneficios")


def obtener_usuario():
    """Obtiene o crea usuario administrador"""
    print("\n[4/12] Verificando usuario...")
    try:
        usuario = User.objects.filter(is_superuser=True).first()
        if not usuario:
            usuario = User.objects.first()
        if not usuario:
            print("⚠ Creando usuario admin...")
            usuario = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print(f"✓ Usuario: {usuario.username}")
        return usuario
    except Exception as e:
        print(f"✗ Error con usuario: {e}")
        return None


def get_acciones_data():
    """Retorna datos de las 20 acciones"""
    return [
        {
            'nombre': 'Instalación de Parques Solares Fotovoltaicos',
            'tipo': 0, 'sector': 1,
            'objetivo': 'Aumentar la generación de energía renovable en un 25%',
            'descripcion': 'Instalación de 50 MW de capacidad solar fotovoltaica distribuida en 5 parques solares',
            'meta': 'Reducir 30,000 tCO2eq anuales',
            'dias_inicio': -365, 'dias_fin': 730, 'estado': 1, 'presupuesto_monto': 15000000,
        },
        {
            'nombre': 'Programa de Eficiencia Energética Industrial',
            'tipo': 2, 'sector': 3,
            'objetivo': 'Reducir el consumo energético industrial en 15%',
            'descripcion': 'Implementación de tecnologías eficientes y capacitación en 20 industrias',
            'meta': 'Ahorro de 50 GWh anuales',
            'dias_inicio': -180, 'dias_fin': 900, 'estado': 1, 'presupuesto_monto': 8000000,
        },
        {
            'nombre': 'Sustitución de Calderas por Biomasa',
            'tipo': 0, 'sector': 3,
            'objetivo': 'Sustituir combustibles fósiles por biomasa renovable',
            'descripcion': 'Reemplazo de 15 calderas de fuel oil por sistemas de biomasa',
            'meta': 'Reducir 45,000 tCO2eq anuales',
            'dias_inicio': -90, 'dias_fin': 540, 'estado': 1, 'presupuesto_monto': 12000000,
        },
        {
            'nombre': 'Agricultura de Conservación y Agroecología',
            'tipo': 1, 'sector': 0,
            'objetivo': 'Implementar prácticas agroecológicas en 5,000 ha',
            'descripcion': 'Capacitación y asistencia técnica a 500 productores en técnicas sostenibles',
            'meta': 'Aumentar rendimientos en 20% y resiliencia climática',
            'dias_inicio': -270, 'dias_fin': 810, 'estado': 1, 'presupuesto_monto': 3500000,
        },
        {
            'nombre': 'Sistema de Riego Eficiente',
            'tipo': 2, 'sector': 0,
            'objetivo': 'Reducir consumo de agua en 30% mediante riego por goteo',
            'descripcion': 'Instalación de sistemas de riego tecnificado en 2,000 ha',
            'meta': 'Ahorrar 6 millones m³ agua/año',
            'dias_inicio': -150, 'dias_fin': 600, 'estado': 1, 'presupuesto_monto': 5000000,
        },
        {
            'nombre': 'Banco de Semillas Resilientes al Clima',
            'tipo': 1, 'sector': 0,
            'objetivo': 'Conservar y distribuir variedades adaptadas a sequía y calor',
            'descripcion': 'Establecimiento de banco con 200 variedades de cultivos resistentes',
            'meta': 'Distribuir 50 toneladas de semillas/año',
            'dias_inicio': -120, 'dias_fin': 1095, 'estado': 1, 'presupuesto_monto': 2000000,
        },
        {
            'nombre': 'Restauración de Manglares Costeros',
            'tipo': 2, 'sector': 6,
            'objetivo': 'Restaurar 500 ha de manglares degradados',
            'descripcion': 'Reforestación y protección de ecosistemas de manglar',
            'meta': 'Capturar 15,000 tCO2/año y proteger 20 km de costa',
            'dias_inicio': -200, 'dias_fin': 1460, 'estado': 1, 'presupuesto_monto': 4000000,
        },
        {
            'nombre': 'Sistema de Alerta Temprana Costera',
            'tipo': 1, 'sector': 6,
            'objetivo': 'Implementar SAT en 10 comunidades vulnerables',
            'descripcion': 'Instalación de sensores, estaciones meteorológicas y sistema de comunicación',
            'meta': 'Proteger a 50,000 habitantes de eventos extremos',
            'dias_inicio': -60, 'dias_fin': 365, 'estado': 1, 'presupuesto_monto': 3000000,
        },
        {
            'nombre': 'Infraestructura Costera Resiliente',
            'tipo': 1, 'sector': 6,
            'objetivo': 'Construir defensas costeras naturales y obras de protección',
            'descripcion': 'Diques, espigones y restauración de dunas en 15 km',
            'meta': 'Proteger infraestructura valorada en $50MM',
            'dias_inicio': -400, 'dias_fin': -30, 'estado': 3, 'presupuesto_monto': 25000000,
        },
        {
            'nombre': 'Cosecha de Agua de Lluvia Rural',
            'tipo': 1, 'sector': 5,
            'objetivo': 'Instalar 1,000 sistemas de captación de agua de lluvia',
            'descripcion': 'Tanques y sistemas de filtración para comunidades rurales',
            'meta': 'Garantizar agua potable a 5,000 familias',
            'dias_inicio': -180, 'dias_fin': 540, 'estado': 1, 'presupuesto_monto': 2500000,
        },
        {
            'nombre': 'Rehabilitación de Cuencas Hidrográficas',
            'tipo': 2, 'sector': 5,
            'objetivo': 'Recuperar la cobertura vegetal en 3 cuencas prioritarias',
            'descripcion': 'Reforestación de 10,000 ha con especies nativas',
            'meta': 'Aumentar infiltración y disponibilidad de agua en 25%',
            'dias_inicio': -300, 'dias_fin': 1095, 'estado': 1, 'presupuesto_monto': 6000000,
        },
        {
            'nombre': 'Electrificación del Transporte Público',
            'tipo': 0, 'sector': 2,
            'objetivo': 'Introducir 100 autobuses eléctricos en La Habana',
            'descripcion': 'Adquisición de flota eléctrica e infraestructura de carga',
            'meta': 'Reducir 8,000 tCO2eq/año',
            'dias_inicio': -45, 'dias_fin': 720, 'estado': 1, 'presupuesto_monto': 20000000,
        },
        {
            'nombre': 'Red de Ciclovías Urbanas',
            'tipo': 2, 'sector': 2,
            'objetivo': 'Construir 50 km de ciclovías seguras',
            'descripcion': 'Infraestructura ciclística integrada al transporte público',
            'meta': 'Reducir 5,000 tCO2eq/año y mejorar calidad del aire',
            'dias_inicio': -200, 'dias_fin': 400, 'estado': 1, 'presupuesto_monto': 8000000,
        },
        {
            'nombre': 'Certificación de Hoteles Sostenibles',
            'tipo': 2, 'sector': 4,
            'objetivo': 'Certificar 30 instalaciones turísticas en estándares verdes',
            'descripcion': 'Implementación de medidas de eficiencia energética, gestión de residuos y agua',
            'meta': 'Reducir huella de carbono del sector en 15%',
            'dias_inicio': -150, 'dias_fin': 600, 'estado': 1, 'presupuesto_monto': 4500000,
        },
        {
            'nombre': 'Corredor Biológico Nacional',
            'tipo': 1, 'sector': 8,
            'objetivo': 'Conectar 5 áreas protegidas mediante corredores ecológicos',
            'descripcion': 'Restauración de 15,000 ha para conectividad ecosistémica',
            'meta': 'Proteger 150 especies endémicas',
            'dias_inicio': -450, 'dias_fin': 900, 'estado': 1, 'presupuesto_monto': 7000000,
        },
        {
            'nombre': 'Monitoreo de Especies Amenazadas',
            'tipo': 3, 'sector': 8,
            'objetivo': 'Establecer sistema de monitoreo de 50 especies vulnerables',
            'descripcion': 'Red de observación, cámaras trampa y análisis genético',
            'meta': 'Base de datos con 10,000 registros/año',
            'dias_inicio': -90, 'dias_fin': 1095, 'estado': 1, 'presupuesto_monto': 1500000,
        },
        {
            'nombre': 'Vigilancia de Enfermedades Sensibles al Clima',
            'tipo': 1, 'sector': 7,
            'objetivo': 'Fortalecer sistema de vigilancia epidemiológica',
            'descripcion': 'Monitoreo de dengue, leptospirosis y enfermedades transmitidas por vectores',
            'meta': 'Reducir incidencia en 30%',
            'dias_inicio': -180, 'dias_fin': 730, 'estado': 1, 'presupuesto_monto': 2000000,
        },
        {
            'nombre': 'Centro de Investigación en Cambio Climático',
            'tipo': 3, 'sector': 1,
            'objetivo': 'Establecer laboratorio de investigación aplicada',
            'descripcion': 'Construcción e equipamiento de centro de excelencia',
            'meta': 'Publicar 20 investigaciones/año',
            'dias_inicio': -500, 'dias_fin': 180, 'estado': 2, 'presupuesto_monto': 10000000,
        },
        {
            'nombre': 'Reforestación Urbana Municipal',
            'tipo': 2, 'sector': 8,
            'objetivo': 'Plantar 50,000 árboles en áreas urbanas',
            'descripcion': 'Campaña masiva de arborización en 10 municipios',
            'meta': 'Aumentar cobertura arbórea urbana en 25%',
            'dias_inicio': -600, 'dias_fin': -100, 'estado': 1, 'presupuesto_monto': 1000000,
        },
        {
            'nombre': 'Adaptación de Infraestructura Vial',
            'tipo': 1, 'sector': 2,
            'objetivo': 'Adaptar 100 km de carreteras a eventos climáticos extremos',
            'descripcion': 'Mejora de drenaje y elevación de tramos vulnerables',
            'meta': 'Reducir interrupciones por inundaciones en 80%',
            'dias_inicio': -30, 'dias_fin': 900, 'estado': 0, 'presupuesto_monto': 18000000,
        },
    ]


def crear_acciones(usuario):
    """Crea 20 acciones con presupuestos, provincias y municipios"""
    print("\n[5/12] Creando acciones...")
    Accion.objects.all().delete()

    tipos_accion = list(TipoAccion.objects.all())
    sectores = list(Sector.objects.all())
    escenarios = list(Escenario.objects.all())
    alcances = list(Alcance.objects.all())
    escalas = list(Escala.objects.all())
    estados_accion = list(EstadoAccion.objects.all())
    entidades = list(Entidad.objects.all())
    programas_apoyo = list(ProgramaApoyo.objects.all())
    programas_productivos = list(ProgramaProductivo.objects.all())
    cobeneficios = list(Cobeneficio.objects.all())

    # Obtener provincias y municipios existentes
    provincias = list(Provincia.objects.all())

    if not provincias:
        print("⚠ No hay provincias en la BD. Las acciones se crearán sin provincias asignadas.")
    else:
        print(f"✓ Encontradas {len(provincias)} provincias en la BD")

    acciones_data = get_acciones_data()
    acciones_creadas = []

    for i, data in enumerate(acciones_data):
        fecha_inicio = date.today() + timedelta(days=data['dias_inicio'])
        fecha_fin = date.today() + timedelta(days=data['dias_fin'])

        accion = Accion.objects.create(
            user=usuario,
            tipo_accion=tipos_accion[data['tipo']],
            nombre=data['nombre'],
            objetivo=data['objetivo'],
            descripcion=data['descripcion'],
            sector=sectores[data['sector']],
            escenario=random.choice(escenarios),
            alcance=random.choice(alcances),
            escala=random.choice(escalas),
            lugar_intervencion=f"Región {i + 1}, múltiples municipios",
            meta=data['meta'],
            publicado=True,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estado_accion=estados_accion[data['estado']],
            entidad_responsable=random.choice(entidades),
            programa_apoyo=random.choice(programas_apoyo) if i % 2 == 0 else None,
            programa_productivo=random.choice(programas_productivos) if i % 3 == 0 else None
        )

        # Asignar provincias (1-3 provincias por acción)
        if provincias:
            num_provincias = random.randint(1, min(3, len(provincias)))
            provincias_seleccionadas = random.sample(provincias, num_provincias)
            accion.provincias.add(*provincias_seleccionadas)

            # Asignar municipios de las provincias seleccionadas (2-5 municipios)
            municipios_disponibles = Municipio.objects.filter(provincia__in=provincias_seleccionadas)
            if municipios_disponibles.exists():
                num_municipios = random.randint(2, min(5, municipios_disponibles.count()))
                municipios_seleccionados = random.sample(list(municipios_disponibles), num_municipios)
                accion.municipios.add(*municipios_seleccionados)

        # Cobeneficios
        num_cobeneficios = random.randint(2, 4)
        accion.cobeneficios.add(*random.sample(cobeneficios, num_cobeneficios))

        acciones_creadas.append(accion)

        # Presupuestos
        crear_presupuestos_accion(accion, data['presupuesto_monto'], data['estado'])

    print(f"✓ Creadas {len(acciones_creadas)} acciones")
    return acciones_creadas


def crear_indicadores(acciones_creadas):
    """Crea 2-3 indicadores por acción CON VARIABLES ASOCIADAS"""
    print("\n[6/12] Creando indicadores...")
    Indicador.objects.all().delete()

    tipos_indicador = list(TipoIndicador.objects.all())
    unidades_medida = list(UnidadMedidaIndicador.objects.all())
    enfoques_ipcc = list(EnfoqueIPCC.objects.all())
    frecuencias = list(FrecuenciaMedicion.objects.all())
    ods_list = list(ObjetivosDesarrolloSostenible.objects.all())

    # Obtener todas las variables disponibles
    todas_variables = list(VariableIndicador.objects.all())

    # Mapeo de fórmulas a variables que necesitan
    formula_variables_map = {
        'consumo_energia': ['consumo_energia'],
        'eficiencia': ['eficiencia'],
        'emisiones_total': ['emisiones_total'],
        'area_reforestacion*500': ['area_reforestacion'],
        'area_reforestacion': ['area_reforestacion'],
        'cantidad_prod': ['cantidad_prod'],
        'poblacion_beneficiada': ['poblacion_beneficiada'],
        'inversion_ejecutada': ['inversion_ejecutada'],
        'reduccion': ['reduccion'],
    }

    templates = {
        'energia': [
            ('Generación de energía renovable', 'kWh generados', 'consumo_energia', 1, 'incremento'),
            ('Eficiencia energética', '% de reducción', 'eficiencia', 4, 'incremento'),
        ],
        'emision': [
            ('Reducción de emisiones GEI', 'tCO2eq reducidas', 'emisiones_total', 0, 'incremento'),
        ],
        'agua': [
            ('Disponibilidad de agua', 'm³ disponibles', 'area_reforestacion*500', 2, 'incremento'),
        ],
        'biodiversidad': [
            ('Área restaurada', 'Hectáreas recuperadas', 'area_reforestacion', 3, 'incremento'),
            ('Especies protegidas', 'Número de especies', 'cantidad_prod', 8, 'incremento'),
        ],
        'social': [
            ('Población beneficiada', 'Personas beneficiadas', 'poblacion_beneficiada', 5, 'incremento'),
        ],
        'economico': [
            ('Inversión ejecutada', 'Monto invertido', 'inversion_ejecutada', 6, 'incremento'),
        ],
    }

    indicadores_creados = []

    for accion in acciones_creadas:
        # Seleccionar templates según sector
        if 'Energía' in accion.sector.nombre or 'Solar' in accion.nombre:
            templates_sel = templates['energia'] + templates['emision']
        elif 'Agua' in accion.nombre or 'Hídric' in accion.sector.nombre:
            templates_sel = templates['agua'] + templates['social']
        elif 'Biodiversidad' in accion.sector.nombre or 'Manglar' in accion.nombre:
            templates_sel = templates['biodiversidad'] + templates['social']
        else:
            templates_sel = templates['social'] + templates['economico']

        num_indicadores = random.randint(2, 3)
        templates_seleccionados = random.sample(templates_sel, min(num_indicadores, len(templates_sel)))

        for nombre, descripcion, formula, unidad_idx, direccion in templates_seleccionados:
            tiene_meta = random.random() > 0.3

            if tiene_meta:
                valor_baseline = random.uniform(10, 100)
                if direccion == 'incremento':
                    meta_valor = valor_baseline * random.uniform(1.2, 1.8)
                else:
                    meta_valor = valor_baseline * random.uniform(0.5, 0.8)

                dias_para_meta = random.randint(
                    (accion.fecha_fin - accion.fecha_inicio).days // 2,
                    (accion.fecha_fin - accion.fecha_inicio).days
                )
                meta_fecha = accion.fecha_inicio + timedelta(days=dias_para_meta)
            else:
                valor_baseline = None
                meta_valor = None
                meta_fecha = None

            indicador = Indicador.objects.create(
                nombre=f"{nombre} - {accion.nombre[:30]}",
                tipo_indicador=random.choice(tipos_indicador),
                descripcion=descripcion,
                fuente_indicador=f"Sistema de monitoreo - {accion.entidad_responsable.nombre}",
                formula=formula,
                unidad_medida=unidades_medida[unidad_idx],
                enfoqueIPCC=random.choice(enfoques_ipcc) if random.random() > 0.5 else None,
                frecuencia_medicion=random.choice(frecuencias),
                direccion_optima=direccion,
                meta_valor=meta_valor,
                meta_fecha_limite=meta_fecha,
                valor_baseline=valor_baseline
            )

            # *** AGREGAR VARIABLES AL INDICADOR ***
            # Obtener las variables necesarias para esta fórmula
            variables_necesarias = formula_variables_map.get(formula, [])

            for var_code in variables_necesarias:
                try:
                    variable = VariableIndicador.objects.get(variable=var_code)
                    indicador.variable_indicador.add(variable)
                except VariableIndicador.DoesNotExist:
                    print(f"⚠ Variable '{var_code}' no encontrada para indicador {indicador.nombre}")

            # Si no se encontraron variables específicas, agregar 1-2 aleatorias
            if not indicador.variable_indicador.exists() and todas_variables:
                num_vars = random.randint(1, 2)
                vars_aleatorias = random.sample(todas_variables, min(num_vars, len(todas_variables)))
                indicador.variable_indicador.add(*vars_aleatorias)

            indicador.objetivos_relacionados.add(*random.sample(ods_list, random.randint(1, 3)))
            accion.indicadores.add(indicador)

            indicadores_creados.append({
                'indicador': indicador,
                'accion': accion,
                'tiene_meta': tiene_meta,
                'baseline': valor_baseline
            })

    print(f"✓ Creados {len(indicadores_creados)} indicadores con variables asociadas")
    return indicadores_creados


def crear_resultados(indicadores_creados):
    """Crea resultados variados para los indicadores"""
    print("\n[7/12] Creando resultados de indicadores...")
    ResultadoIndicador.objects.all().delete()
    ResultadoVariable.objects.all().delete()

    resultados_creados = 0

    for ind_data in indicadores_creados:
        indicador = ind_data['indicador']
        accion = ind_data['accion']
        tiene_meta = ind_data['tiene_meta']
        baseline = ind_data['baseline']

        # Obtener las variables del indicador
        variables_indicador = list(indicador.variable_indicador.all())

        # Determinar tipo de evolución
        if accion.estado_accion.orden == 3:
            tipo_evolucion = 'excelente'
        elif accion.estado_accion.orden == 2:
            tipo_evolucion = 'critico'
        elif accion.estado_accion.orden == 0:
            tipo_evolucion = 'sin_datos'
        else:
            rand = random.random()
            if rand < 0.3:
                tipo_evolucion = 'critico'
            elif rand < 0.6:
                tipo_evolucion = 'regular'
            else:
                tipo_evolucion = 'bueno'

        if tipo_evolucion == 'sin_datos':
            continue

        dias_desde_inicio = (date.today() - accion.fecha_inicio).days
        if dias_desde_inicio < 0:
            continue

        # Determinar intervalo según frecuencia de medición
        if indicador.frecuencia_medicion:
            if 'Mensual' in indicador.frecuencia_medicion.nombre:
                intervalo_dias = 30
            elif 'Trimestral' in indicador.frecuencia_medicion.nombre:
                intervalo_dias = 90
            elif 'Semestral' in indicador.frecuencia_medicion.nombre:
                intervalo_dias = 180
            elif 'Anual' in indicador.frecuencia_medicion.nombre:
                intervalo_dias = 365
            elif 'Semanal' in indicador.frecuencia_medicion.nombre:
                intervalo_dias = 7
            else:
                intervalo_dias = 90
        else:
            intervalo_dias = 90

        # FORZAR: Crear entre 3 y 5 resultados por indicador
        if tipo_evolucion == 'critico':
            num_mediciones = random.randint(1, 2)  # Pocos resultados para críticos
        else:
            num_mediciones = random.randint(3, 5)  # 3-5 resultados normales

        # Ajustar si no hay suficiente tiempo transcurrido
        max_mediciones_posibles = dias_desde_inicio // intervalo_dias
        if max_mediciones_posibles < num_mediciones:
            if max_mediciones_posibles > 0:
                num_mediciones = max_mediciones_posibles
            else:
                continue  # Saltar si no hay tiempo para ni una medición

        # Generar valores
        for i in range(num_mediciones):
            if tipo_evolucion == 'excelente':
                if tiene_meta and baseline:
                    progreso = (i + 1) / num_mediciones * 1.1
                    if indicador.direccion_optima == 'incremento':
                        valor = baseline + (indicador.meta_valor - baseline) * progreso
                    else:
                        valor = baseline - (baseline - indicador.meta_valor) * progreso
                else:
                    valor = (i + 1) * random.uniform(80, 120)

            elif tipo_evolucion == 'bueno':
                if tiene_meta and baseline:
                    progreso = (i + 1) / num_mediciones * random.uniform(0.8, 1.0)
                    if indicador.direccion_optima == 'incremento':
                        valor = baseline + (indicador.meta_valor - baseline) * progreso
                    else:
                        valor = baseline - (baseline - indicador.meta_valor) * progreso
                else:
                    valor = (i + 1) * random.uniform(60, 100)

            elif tipo_evolucion == 'regular':
                if tiene_meta and baseline:
                    progreso = (i + 1) / num_mediciones * random.uniform(0.4, 0.6)
                    if indicador.direccion_optima == 'incremento':
                        valor = baseline + (indicador.meta_valor - baseline) * progreso
                    else:
                        valor = baseline - (baseline - indicador.meta_valor) * progreso
                else:
                    valor = (i + 1) * random.uniform(30, 60)

            else:  # critico
                if tiene_meta and baseline:
                    if indicador.direccion_optima == 'incremento':
                        valor = baseline * random.uniform(0.9, 1.1)
                    else:
                        valor = baseline * random.uniform(1.0, 1.2)
                else:
                    valor = random.uniform(10, 30)

            # Determinar fecha según intervalo de frecuencia
            from datetime import datetime

            if tipo_evolucion == 'critico' and i == num_mediciones - 1:
                # Última medición hace mucho tiempo (120-200 días)
                dias_ultima_medicion = random.randint(120, 200)
                fecha_base = date.today() - timedelta(days=dias_ultima_medicion)
            else:
                # Fecha basada en el intervalo de frecuencia del indicador
                fecha_base = accion.fecha_inicio + timedelta(days=(i + 1) * intervalo_dias)

                # Asegurar que no sea futura
                if fecha_base > date.today():
                    fecha_base = date.today() - timedelta(days=random.randint(1, 30))

            # Convertir a datetime con hora específica para evitar duplicados
            fecha_hora = datetime.combine(fecha_base, datetime.min.time()) + timedelta(
                hours=random.randint(8, 17),
                minutes=random.randint(0, 59),
                seconds=i  # Usar índice para garantizar unicidad
            )

            # Crear resultado
            resultado = ResultadoIndicador.objects.create(
                fuente_dato=f"Medición {i + 1}",
                valor=round(max(0, valor), 2),
                observacion=f"Medición período {i + 1}",
                fecha=fecha_hora
            )

            # *** CREAR RESULTADOS DE VARIABLES ***
            # Asignar valores a cada variable del indicador
            if variables_indicador:
                for var in variables_indicador:
                    # Calcular un valor derivado del valor principal del resultado
                    # con algo de variación aleatoria
                    valor_variable = valor * random.uniform(0.8, 1.2) / len(variables_indicador)

                    ResultadoVariable.objects.create(
                        resultado=resultado,
                        variable_indicador=var,
                        valor=round(max(0, valor_variable), 2)
                    )

            indicador.resultados.add(resultado)
            indicador.ultima_medicion = fecha_hora
            indicador.save()

            resultados_creados += 1

    print(f"✓ Creados {resultados_creados} resultados con variables")


def mostrar_estadisticas():
    """Muestra estadísticas finales"""
    print("\n" + "=" * 70)
    print("RESUMEN DE POBLACIÓN DE BASE DE DATOS")
    print("=" * 70)
    print(f"✓ Acciones:                      {Accion.objects.count()}")
    print(f"✓ Indicadores:                   {Indicador.objects.count()}")
    print(f"✓ Resultados:                    {ResultadoIndicador.objects.count()}")
    print(f"✓ Resultados de Variables:       {ResultadoVariable.objects.count()}")
    print(f"✓ Presupuestos planificados:     {PresupuestoPlanificado.objects.count()}")
    print(f"✓ Presupuestos ejecutados:       {PresupuestoEjecutado.objects.count()}")

    # Estadísticas de ubicación
    acciones_con_provincias = Accion.objects.filter(provincias__isnull=False).distinct().count()
    acciones_con_municipios = Accion.objects.filter(municipios__isnull=False).distinct().count()
    print(f"✓ Acciones con provincias:       {acciones_con_provincias}")
    print(f"✓ Acciones con municipios:       {acciones_con_municipios}")

    # Estadísticas de variables
    indicadores_con_variables = Indicador.objects.filter(variable_indicador__isnull=False).distinct().count()
    print(f"✓ Indicadores con variables:     {indicadores_con_variables}")

    print("\n" + "-" * 70)
    print("ALERTAS POTENCIALES:")
    print("-" * 70)

    # Sin mediciones
    sin_mediciones = 0
    for accion in Accion.objects.filter(publicado=True):
        for ind in accion.indicadores.all():
            if not ind.resultados.exists():
                sin_mediciones += 1

    # Sin medición reciente
    sin_medicion_reciente = 0
    fecha_limite = date.today() - timedelta(days=90)
    for accion in Accion.objects.filter(publicado=True):
        for ind in accion.indicadores.all():
            ultima = ind.resultados.order_by('-fecha').first()
            if ultima and ultima.fecha.date() < fecha_limite:
                sin_medicion_reciente += 1

    # Metas próximas
    metas_proximas = 0
    fecha_30_dias = date.today() + timedelta(days=30)
    for accion in Accion.objects.filter(publicado=True):
        for ind in accion.indicadores.filter(
                meta_fecha_limite__isnull=False,
                meta_fecha_limite__lte=fecha_30_dias
        ):
            metas_proximas += 1

    print(f"⚠ Sin mediciones:                {sin_mediciones}")
    print(f"⚠ Sin medición reciente (>90d):  {sin_medicion_reciente}")
    print(f"⚠ Metas próximas (30 días):      {metas_proximas}")

    print("\n" + "=" * 70)
    print("✅ POBLACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)


def clear_and_populate():
    """Función principal"""
    print("=" * 70)
    print("INICIANDO POBLACIÓN DE LA BASE DE DATOS")
    print("=" * 70)

    crear_nomencladores()
    crear_entidades()
    crear_cobeneficios()

    usuario = obtener_usuario()
    if not usuario:
        print("Error: No se pudo obtener usuario")
        return

    acciones = crear_acciones(usuario)
    indicadores = crear_indicadores(acciones)
    crear_resultados(indicadores)

    mostrar_estadisticas()


if __name__ == "__main__":
    clear_and_populate()