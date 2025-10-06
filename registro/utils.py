# Grafico de linea para el comportamiento de los resultados del indicador
def data_chart_line(data_line, indicador):
    chart_data_line = {
        'series': [data_line['valores']],
        'chart': {
            'height': 350,
            'type': 'area',

        },
        'title': {
            'text': 'Comportamiento de los resultados de ' + indicador.nombre,
            'style': {
                'fontSize': '20px',
                'fontWeight': 'bold',
                'fontFamily': 'Inter, Helvetica, sans-serif',
            }
        },
        'colors':['#1B84FF'],
        'dataLabels': {
            'enabled': 'false',
            'style': {
                'colors': ['#1B84FF']
            }
        },
        'fill': {
            'colors': ['#1B84FF']
        },
        'xaxis': {
            'categories': data_line['labels'],
        },
        'legend': {
            'position': 'top',
            'horizontalAlign': 'right',
            'offsetX': -10
        },
    }
    return chart_data_line

def data_chart_donut():
    chart_donut_data = {
            'series': [],
            'labels': ['Restante', 'Ejecutado'],
            'locales': [
                {
                    "name": "en",
                    "options": {
                        "months": ["January", "February", "March", "April", "May", "June", "July", "August",
                                   "September",
                                   "October", "November", "December"],
                        "shortMonths": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
                                        "Dec"],
                        "days": ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                        "shortDays": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
                        "toolbar": {
                            "exportToSVG": "Download SVG",
                            "exportToPNG": "Download PNG",
                            "menu": "Menu",
                            "selection": "Selection",
                            "selectionZoom": "Selection Zoom",
                            "zoomIn": "Zoom In",
                            "zoomOut": "Zoom Out",
                            "pan": "Panning",
                            "reset": "Reset Zoom"
                        }
                    }
                }
            ],
            'chart': {
                'type': 'donut',
            },
            'plotOptions': {
                'pie': {
                    'donut': {
                        'labels': {
                            'show': 'true',
                            'total': {
                                'showAlways': 'true',
                                'show': 'true'
                            }
                        }
                    }
                }
            },

        }
    return chart_donut_data


class ChartConfigurationService:
    """Servicio para configurar diferentes tipos de gráficos"""

    @staticmethod
    def get_base_chart_config():
        """Configuración base común para todos los gráficos"""
        return {
            'chart': {
                'toolbar': {'show': True},
                'zoom': {'enabled': True},
                'animations': {'enabled': True, 'speed': 800}
            },
            'dataLabels': {'enabled': False},
            'stroke': {'curve': 'smooth', 'width': 3},
            'legend': {
                'position': 'top',
                'horizontalAlign': 'right',
                'offsetX': -10,
                'fontSize': '12px'
            },
            'grid': {
                'borderColor': '#e7e7e7',
                'strokeDashArray': 5,
                'xaxis': {'lines': {'show': True}},
                'yaxis': {'lines': {'show': True}}
            },
            'tooltip': {
                'enabled': True,
                'shared': True,
                'intersect': False
            }
        }

    @staticmethod
    def get_line_chart_config(title, data_series, categories, colors=None):
        """Configuración específica para gráficos de línea"""
        config = ChartConfigurationService.get_base_chart_config()
        config.update({
            'series': data_series,
            'chart': {
                **config['chart'],
                'height': 350,
                'type': 'line'
            },
            'title': {
                'text': title,
                'style': {
                    'fontSize': '18px',
                    'fontWeight': 'bold',
                    'fontFamily': 'Inter, sans-serif',
                    'color': '#181C32'
                }
            },
            'colors': colors or ['#1B84FF', '#f59e0b', '#ef4444', '#10b981'],
            'xaxis': {
                'categories': categories,
                'labels': {'style': {'fontSize': '12px'}}
            },
            'yaxis': {
                'labels': {'style': {'fontSize': '12px'}}
            }
        })
        return config

    @staticmethod
    def get_area_chart_config(title, data_series, categories, colors=None):
        """Configuración específica para gráficos de área"""
        config = ChartConfigurationService.get_line_chart_config(title, data_series, categories, colors)
        config['chart']['type'] = 'area'
        config['fill'] = {
            'type': 'gradient',
            'gradient': {
                'shadeIntensity': 1,
                'type': 'vertical',
                'colorStops': [
                    {'offset': 0, 'color': colors[0] if colors else '#1B84FF', 'opacity': 0.8},
                    {'offset': 100, 'color': colors[0] if colors else '#1B84FF', 'opacity': 0.1}
                ]
            }
        }
        return config

    @staticmethod
    def get_donut_chart_config(series_data, labels, colors=None):
        """Configuración específica para gráficos de dona"""
        return {
            'series': series_data,
            'labels': labels,
            'chart': {
                'type': 'donut',
                'height': 300
            },
            'colors': colors or ['#e74c3c', '#2ecc71', '#f39c12', '#3498db'],
            'plotOptions': {
                'pie': {
                    'donut': {
                        'size': '60%',
                        'labels': {
                            'show': True,
                            'total': {
                                'showAlways': True,
                                'show': True,
                                'fontSize': '16px',
                                'fontWeight': 'bold'
                            }
                        }
                    }
                }
            },
            'legend': {
                'position': 'bottom',
                'fontSize': '12px'
            },
            'tooltip': {
                'y': {
                    'formatter': "function(val) { return val + '%' }"
                }
            }
        }


# def data_chart_line(data_line, indicador, chart_type='area'):
#     """Función mejorada para generar gráficos de línea/área"""
#     series = [data_line['valores']]
#     categories = data_line['labels']
#     title = f'Comportamiento de {indicador.nombre}'
#
#     if chart_type == 'area':
#         return ChartConfigurationService.get_area_chart_config(title, series, categories)
#     else:
#         return ChartConfigurationService.get_line_chart_config(title, series, categories)


def data_chart_enhanced(data_line, indicador, projection=None, meta=None):
    """Gráfico mejorado con proyección y línea de meta"""
    series = [data_line['valores']]

    # Agregar proyección si existe
    if projection:
        projection_data = [None] * (len(data_line['labels']) - 1) + [projection['proximo_valor']]
        series.append({
            'name': 'Proyección',
            'data': projection_data,
            'type': 'line',
            'dashArray': 5
        })

    # Agregar línea de meta si existe
    if meta:
        meta_data = [meta['valor']] * len(data_line['labels'])
        series.append({
            'name': 'Meta',
            'data': meta_data,
            'type': 'line',
            'dashArray': 8
        })

    config = ChartConfigurationService.get_line_chart_config(
        f'Análisis Completo - {indicador.nombre}',
        series,
        data_line['labels'],
        ['#1B84FF', '#f59e0b', '#ef4444']
    )

    return config


# def data_chart_donut(series_data=None, labels=None):
#     """Función mejorada para gráficos de dona"""
#     default_series = [0, 0]
#     default_labels = ['Restante', 'Ejecutado']
#
#     return ChartConfigurationService.get_donut_chart_config(
#         series_data or default_series,
#         labels or default_labels
#     )