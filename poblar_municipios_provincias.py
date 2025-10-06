from django.db import transaction

from nomencladores.models import Provincia, Municipio


def poblar_bd_municipio_provincia():
    PROVINCIAS_DATA = [
        {'nombre': 'Pinar del Río', 'hc_keys': 'PR', 'codigo': '21', 'sigla': 'PR'},
        {'nombre': 'Artemisa', 'hc_keys': 'AR', 'codigo': '22', 'sigla': 'ART'},
        {'nombre': 'La Habana', 'hc_keys': 'LH', 'codigo': '23', 'sigla': 'LH'},
        {'nombre': 'Mayabeque', 'hc_keys': 'MY', 'codigo': '24', 'sigla': 'MAY'},
        {'nombre': 'Matanzas', 'hc_keys': 'MT', 'codigo': '25', 'sigla': 'MTZ'},
        {'nombre': 'Cienfuegos', 'hc_keys': 'CF', 'codigo': '26', 'sigla': 'CFG'},
        {'nombre': 'Villa Clara', 'hc_keys': 'VC', 'codigo': '27', 'sigla': 'VCL'},
        {'nombre': 'Sancti Spíritus', 'hc_keys': 'SS', 'codigo': '28', 'sigla': 'SSP'},
        {'nombre': 'Ciego de Ávila', 'hc_keys': 'CA', 'codigo': '29', 'sigla': 'CAV'},
        {'nombre': 'Camagüey', 'hc_keys': 'CM', 'codigo': '30', 'sigla': 'CMG'},
        {'nombre': 'Las Tunas', 'hc_keys': 'LT', 'codigo': '31', 'sigla': 'LTU'},
        {'nombre': 'Holguín', 'hc_keys': 'HO', 'codigo': '32', 'sigla': 'HOL'},
        {'nombre': 'Granma', 'hc_keys': 'GR', 'codigo': '33', 'sigla': 'GRA'},
        {'nombre': 'Santiago de Cuba', 'hc_keys': 'SC', 'codigo': '34', 'sigla': 'SCU'},
        {'nombre': 'Guantánamo', 'hc_keys': 'GU', 'codigo': '35', 'sigla': 'GTM'},
        {'nombre': 'Isla de la Juventud', 'hc_keys': 'IJ', 'codigo': '40', 'sigla': 'IJV'},
    ]

    MUNICIPIOS_DATA = {
        'Pinar del Río': [
            'Consolación del Sur', 'Guane', 'La Palma', 'Los Palacios',
            'Mantua', 'Minas de Matahambre', 'Pinar del Río',
            'San Juan y Martínez', 'San Luis', 'Sandino', 'Viñales'
        ],
        'Artemisa': [
            'Alquízar', 'Artemisa', 'Bahía Honda', 'Bauta', 'Caimito',
            'Guanajay', 'Güira de Melena', 'Mariel', 'San Antonio de los Baños',
            'San Cristóbal', 'Candelaria'
        ],
        'La Habana': [
            'Arroyo Naranjo', 'Boyeros', 'Centro Habana', 'Cerro', 'Cotorro',
            'Diez de Octubre', 'Guanabacoa', 'La Habana del Este',
            'La Habana Vieja', 'La Lisa', 'Marianao', 'Playa', 'Plaza de la Revolución',
            'Regla', 'San Miguel del Padrón'
        ],
        'Mayabeque': [
            'Batabanó', 'Bejucal', 'Güines', 'Jaruco', 'Madruga',
            'Melena del Sur', 'Nueva Paz', 'Quivicán', 'San José de las Lajas',
            'San Nicolás de Bari', 'Santa Cruz del Norte'
        ],
        'Matanzas': [
            'Calimete', 'Cárdenas', 'Ciudad de Matanzas', 'Colón', 'Jagüey Grande',
            'Jovellanos', 'Limonar', 'Los Arabos', 'Martí', 'Pedro Betancourt',
            'Perico', 'Unión de Reyes', 'Varadero'
        ],
        'Cienfuegos': [
            'Abreus', 'Aguada de Pasajeros', 'Cienfuegos', 'Cruces',
            'Cumanayagua', 'Lajas', 'Palmira', 'Rodas', 'Santa Isabel de las Lajas'
        ],
        'Villa Clara': [
            'Caibarién', 'Camajuaní', 'Cifuentes', 'Corralillo', 'Encrucijada',
            'Manicaragua', 'Placetas', 'Quemado de Güines', 'Ranchuelo',
            'Remedios', 'Sagua la Grande', 'Santa Clara', 'Santo Domingo'
        ],
        'Sancti Spíritus': [
            'Cabaiguán', 'Fomento', 'Jatibonico', 'La Sierpe', 'Sancti Spíritus',
            'Taguasco', 'Trinidad', 'Yaguajay'
        ],
        'Ciego de Ávila': [
            'Baraguá', 'Bolivia', 'Chambas', 'Ciego de Ávila', 'Ciro Redondo',
            'Florencia', 'Majagua', 'Morón', 'Primero de Enero', 'Venezuela'
        ],
        'Camagüey': [
            'Camagüey', 'Carlos M. de Céspedes', 'Esmeralda', 'Florida',
            'Guáimaro', 'Jimaguayú', 'Minas', 'Najasa', 'Nuevitas',
            'Santa Cruz del Sur', 'Sibanicú', 'Sierra de Cubitas', 'Vertientes'
        ],
        'Las Tunas': [
            'Amancio', 'Colombia', 'Jesús Menéndez', 'Jobabo', 'Las Tunas',
            'Majibacoa', 'Manatí', 'Puerto Padre'
        ],
        'Holguín': [
            'Antilla', 'Báguanos', 'Banes', 'Cacocum', 'Calixto García',
            'Cueto', 'Frank País', 'Gibara', 'Holguín', 'Mayarí', 'Moa',
            'Rafael Freyre', 'Sagua de Tánamo', 'Urbano Noris'
        ],
        'Granma': [
            'Bartolomé Masó', 'Bayamo', 'Buey Arriba', 'Campechuela',
            'Cauto Cristo', 'Guisa', 'Jiguaní', 'Manzanillo', 'Media Luna',
            'Niquero', 'Pilón', 'Río Cauto', 'Yara'
        ],
        'Santiago de Cuba': [
            'Contramaestre', 'Guamá', 'Mella', 'Palma Soriano',
            'San Luis', 'Santiago de Cuba', 'Segundo Frente',
            'Songo-La Maya', 'Tercer Frente'
        ],
        'Guantánamo': [
            'Baracoa', 'Caimanera', 'El Salvador', 'Guantánamo',
            'Imías', 'Maisí', 'Manuel Tames', 'Niceto Pérez', 'San Antonio del Sur',
            'Yateras'
        ],
        'Isla de la Juventud': [
            'Isla de la Juventud'
        ]
    }
    try:
        with transaction.atomic():
            # Crear provincias
            for prov_data in PROVINCIAS_DATA:
                provincia, created = Provincia.objects.get_or_create(
                    nombre=prov_data['nombre'],
                    defaults={
                        'hc_keys': prov_data['hc_keys'],
                        'codigo': prov_data['codigo'],
                        'sigla': prov_data['sigla'],
                    }
                )
                if created:
                    print(f'Provincia creada: {provincia.nombre}')
                else:
                    print(f'Provincia ya existe: {provincia.nombre}')

                # Crear municipios para esta provincia
                municipios = MUNICIPIOS_DATA.get(prov_data['nombre'], [])
                for i, municipio_nombre in enumerate(municipios, start=1):
                    codigo_municipio = f"{prov_data['codigo']}.{i:02d}"

                    municipio, m_created = Municipio.objects.get_or_create(
                        nombre=municipio_nombre,
                        provincia=provincia,
                        defaults={
                            'codigo': codigo_municipio,
                        }
                    )

                    if m_created:
                        print(f'  Municipio creado: {municipio.nombre} ({codigo_municipio})')
                    else:
                        print(f'  Municipio ya existe: {municipio.nombre}')
    except Exception as e:
        return ValueError(str(e))
    return True
