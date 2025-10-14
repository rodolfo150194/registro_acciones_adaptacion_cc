from django import template

register = template.Library()
@register.filter(name='formato_numero')
def formato_numero(value, simbolo="$"):
    """
    Template filter para formatear números como moneda
    Uso: {{ precio|formato_moneda }} o {{ precio|formato_moneda:"€" }}
    """
    if value is None:
        return ""

    try:
        if isinstance(value, str):
            value = value.replace(',', '').replace('.', '')
            numero = float(value)
        else:
            numero = float(value)

        return f"{simbolo}{numero:,.2f}"
    except (ValueError, TypeError):
        return f"{simbolo}{value}"
