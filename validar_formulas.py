#!/usr/bin/env python
"""
Script para validar fórmulas de indicadores y sus variables.
Ejecutar: python manage.py shell < validar_formulas.py
"""

import os
import django
import re
from sympy import sympify, symbols
from sympy.core.sympify import SympifyError

# Configurar Django
if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
    django.setup()

from registro.models import Indicador, VariableIndicador
from nomencladores.models import VariableIndicador as VarNomenclador


def extraer_variables_de_formula(formula):
    """
    Extrae variables de una fórmula matemática.
    """
    formula_limpia = re.sub(r'[\+\-\*/\(\)\s]', ' ', formula)
    variables = []
    for palabra in formula_limpia.split():
        if palabra and not palabra.replace('.', '').replace(',', '').isdigit():
            variables.append(palabra)

    variables_unicas = []
    for var in variables:
        if var not in variables_unicas:
            variables_unicas.append(var)

    return variables_unicas


def validar_sintaxis_formula(formula):
    """
    Valida que la sintaxis de la fórmula sea correcta matemáticamente.
    """
    try:
        # Extraer variables
        variables = extraer_variables_de_formula(formula)

        # Crear símbolos de SymPy
        vars_dict = {var: symbols(var) for var in variables}

        # Intentar parsear la fórmula
        expr = sympify(formula, locals=vars_dict)

        return True, "Fórmula válida", expr
    except SympifyError as e:
        return False, f"Error de sintaxis: {str(e)}", None
    except Exception as e:
        return False, f"Error inesperado: {str(e)}", None


def evaluar_formula_con_valores(formula, valores):
    """
    Evalúa una fórmula con valores específicos para las variables.

    Args:
        formula (str): La fórmula a evaluar
        valores (dict): Diccionario con valores para cada variable

    Returns:
        tuple: (éxito, resultado/error)
    """
    try:
        variables = extraer_variables_de_formula(formula)

        # Verificar que todos los valores estén presentes
        for var in variables:
            if var not in valores:
                return False, f"Falta valor para la variable: {var}"

        # Crear símbolos
        vars_dict = {var: symbols(var) for var in variables}

        # Parsear fórmula
        expr = sympify(formula, locals=vars_dict)

        # Sustituir valores
        resultado = expr.subs(valores)

        return True, float(resultado)
    except Exception as e:
        return False, f"Error al evaluar: {str(e)}"


def validar_indicadores():
    """
    Valida todos los indicadores en la base de datos.
    """
    print("\n" + "=" * 70)
    print("VALIDACIÓN DE FÓRMULAS E INDICADORES")
    print("=" * 70)

    indicadores = Indicador.objects.all()

    if not indicadores.exists():
        print("⚠️  No hay indicadores en la base de datos.")
        print("   Ejecute primero: python manage.py shell < poblar_bd.py")
        return

    print(f"\n📊 Total de indicadores: {indicadores.count()}\n")

    for i, indicador in enumerate(indicadores, 1):
        print(f"\n{'─' * 70}")
        print(f"🔍 INDICADOR {i}: {indicador.nombre}")
        print(f"{'─' * 70}")
        print(f"   Tipo: {indicador.tipo_indicador.nombre}")
        print(f"   Fórmula: {indicador.formula}")

        # Validar sintaxis
        es_valida, mensaje, expr = validar_sintaxis_formula(indicador.formula)

        if es_valida:
            print(f"   ✅ Sintaxis válida")
            print(f"   📐 Expresión parseada: {expr}")
        else:
            print(f"   ❌ Sintaxis inválida: {mensaje}")
            continue

        # Mostrar variables asociadas
        variables = indicador.variable_indicador.all()
        variables_formula = extraer_variables_de_formula(indicador.formula)

        print(f"\n   Variables en la fórmula: {', '.join(variables_formula)}")
        print(f"   Variables en BD: {variables.count()}")

        if variables.exists():
            print(f"\n   📋 Detalle de variables:")
            for var in variables:
                esta_en_formula = var.variable in variables_formula
                icono = "✓" if esta_en_formula else "⚠️"
                print(f"      {icono} {var.nombre} ({var.variable})")

        # Validar que todas las variables de la fórmula estén en BD
        variables_bd = [v.variable for v in variables]
        faltantes = [v for v in variables_formula if v not in variables_bd]

        if faltantes:
            print(f"\n   ⚠️  Variables faltantes en BD: {', '.join(faltantes)}")
        else:
            print(f"\n   ✅ Todas las variables están registradas")

        # Ejemplo de evaluación con valores de prueba
        print(f"\n   🧪 Prueba de evaluación:")
        valores_prueba = {var: 10.0 for var in variables_formula}
        print(f"      Valores de prueba: {valores_prueba}")

        exito, resultado = evaluar_formula_con_valores(indicador.formula, valores_prueba)
        if exito:
            print(f"      ✅ Resultado: {resultado}")
        else:
            print(f"      ❌ Error: {resultado}")


def probar_formulas_ejemplo():
    """
    Prueba formulas de ejemplo sin necesidad de BD.
    """
    print("\n" + "=" * 70)
    print("PRUEBAS DE FÓRMULAS DE EJEMPLO")
    print("=" * 70)

    formulas_ejemplo = [
        {
            "nombre": "Emisiones ganaderas",
            "formula": "(cantidad * animal) - grasa",
            "valores": {"cantidad": 100, "animal": 2.5, "grasa": 15.0}
        },
        {
            "nombre": "Energía promedio",
            "formula": "(energia_m + energia_n + cantidad_v) / 2",
            "valores": {"energia_m": 50, "energia_n": 60, "cantidad_v": 40}
        },
        {
            "nombre": "Eficiencia energética",
            "formula": "(consumo_anterior - consumo_actual) / consumo_anterior * 100",
            "valores": {"consumo_anterior": 1000, "consumo_actual": 800}
        },
        {
            "nombre": "Temperatura simple",
            "formula": "temperatura",
            "valores": {"temperatura": 25.5}
        },
        {
            "nombre": "Fórmula compleja",
            "formula": "((a + b) * c) / (d - e) + f",
            "valores": {"a": 10, "b": 20, "c": 5, "d": 100, "e": 50, "f": 15}
        }
    ]

    for i, ejemplo in enumerate(formulas_ejemplo, 1):
        print(f"\n{'─' * 70}")
        print(f"📝 EJEMPLO {i}: {ejemplo['nombre']}")
        print(f"{'─' * 70}")
        print(f"   Fórmula: {ejemplo['formula']}")

        # Validar sintaxis
        es_valida, mensaje, expr = validar_sintaxis_formula(ejemplo['formula'])
        print(f"   Sintaxis: {'✅ Válida' if es_valida else '❌ Inválida'}")

        if not es_valida:
            print(f"   Error: {mensaje}")
            continue

        print(f"   Expresión: {expr}")

        # Extraer variables
        variables = extraer_variables_de_formula(ejemplo['formula'])
        print(f"   Variables detectadas: {', '.join(variables)}")

        # Evaluar
        print(f"\n   Valores de entrada:")
        for var, val in ejemplo['valores'].items():
            print(f"      {var} = {val}")

        exito, resultado = evaluar_formula_con_valores(
            ejemplo['formula'],
            ejemplo['valores']
        )

        if exito:
            print(f"\n   ✅ Resultado calculado: {resultado}")
        else:
            print(f"\n   ❌ Error: {resultado}")


def mostrar_resumen():
    """
    Muestra un resumen estadístico de las variables e indicadores.
    """
    print("\n" + "=" * 70)
    print("RESUMEN ESTADÍSTICO")
    print("=" * 70)

    total_indicadores = Indicador.objects.count()
    total_variables = VariableIndicador.objects.count()

    print(f"\n📊 Indicadores totales: {total_indicadores}")
    print(f"📋 Variables totales: {total_variables}")

    if total_indicadores > 0:
        # Variables promedio por indicador
        suma_vars = sum(ind.variable_indicador.count() for ind in Indicador.objects.all())
        promedio = suma_vars / total_indicadores if total_indicadores > 0 else 0
        print(f"📈 Promedio de variables por indicador: {promedio:.2f}")

        # Indicadores sin variables
        sin_variables = Indicador.objects.filter(variable_indicador__isnull=True).count()
        if sin_variables > 0:
            print(f"⚠️  Indicadores sin variables: {sin_variables}")

        # Variables más utilizadas
        print(f"\n🏆 Variables más utilizadas:")
        from django.db.models import Count
        vars_top = VariableIndicador.objects.annotate(
            num_indicadores=Count('variables_indicador')
        ).order_by('-num_indicadores')[:5]

        for var in vars_top:
            print(f"   • {var.nombre} ({var.variable}): {var.num_indicadores} indicadores")

    print("\n" + "=" * 70)


def main():
    """
    Función principal de validación.
    """
    print("\n🚀 Iniciando validación de fórmulas...")

    # Opción 1: Probar fórmulas de ejemplo sin BD
    probar_formulas_ejemplo()

    # Opción 2: Validar indicadores en BD
    validar_indicadores()

    # Opción 3: Mostrar resumen
    mostrar_resumen()

    print("\n✅ Validación completada.\n")


if __name__ == "__main__":
    main()