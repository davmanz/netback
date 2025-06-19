from django.core.management.base import BaseCommand
from datetime import datetime  # 👈 Añade esta línea arriba
from core.models import (Area, ClassificationRuleSet, Country, DeviceType,
                         Manufacturer, Site, UserSystem, BackupSchedule)


class Command(BaseCommand):
    help = "Carga datos iniciales: fabricantes, países, tipos de equipo y superusuario admin"

    def handle(self, *args, **kwargs):

        ##########################
        ####                  ####
        ####    Fabricantes   ####
        ####                  ####
        ##########################
        Manufacturer.objects.bulk_create(
            [
                Manufacturer(
                    name="Cisco",
                    get_running_config="show running-config",
                    get_vlan_info="show vlan brief",
                    netmiko_type="cisco_ios",
                ),
                Manufacturer(
                    name="Huawei",
                    get_running_config="display current-configuration",
                    get_vlan_info="display vlan",
                    netmiko_type="huawei",
                ),
                Manufacturer(
                    name="Desconocido",
                    get_running_config="show running-config",
                    get_vlan_info="show vlan",
                    netmiko_type="autodetect",
                ),
            ],
            ignore_conflicts=True,
        )

        ##########################
        ####                  ####
        ####      Paises      ####
        ####                  ####
        ##########################
        Country.objects.bulk_create(
            [
                Country(name="Perú"),
                Country(name="Chile"),
                Country(name="Colombia"),
                Country(name="Desconocido"),
            ],
            ignore_conflicts=True,
        )

        ##########################
        ####                  ####
        ####      Sitios      ####
        ####                  ####
        ##########################
        Site.objects.bulk_create(
            [
                # Sitios de Chile
                Site(name="Casa Matriz", country=Country.objects.get(name="Chile")),
                Site(name="Alameda", country=Country.objects.get(name="Chile")),
                Site(name="Antofagasta", country=Country.objects.get(name="Chile")),
                Site(name="Arica", country=Country.objects.get(name="Chile")),
                Site(name="Bio Bio", country=Country.objects.get(name="Chile")),
                Site(name="Calama", country=Country.objects.get(name="Chile")),
                Site(name="Copiapo", country=Country.objects.get(name="Chile")),
                Site(name="Egaña", country=Country.objects.get(name="Chile")),
                Site(name="Iquique", country=Country.objects.get(name="Chile")),
                Site(name="Los Angeles", country=Country.objects.get(name="Chile")),
                Site(name="Los Dominicos", country=Country.objects.get(name="Chile")),
                Site(name="La Serena", country=Country.objects.get(name="Chile")),
                Site(name="Norte", country=Country.objects.get(name="Chile")),
                Site(name="Oeste", country=Country.objects.get(name="Chile")),
                Site(name="Sur", country=Country.objects.get(name="Chile")),
                Site(name="Tobalada", country=Country.objects.get(name="Chile")),
                Site(name="Trebol", country=Country.objects.get(name="Chile")),
                Site(name="Vespucio", country=Country.objects.get(name="Chile")),
                Site(name="Sala COP", country=Country.objects.get(name="Chile")),
                # Sitios de Perú
                # MallPlaza
                Site(name="Bella Vista", country=Country.objects.get(name="Perú")),
                Site(name="Comas", country=Country.objects.get(name="Perú")),
                Site(name="Arequipa", country=Country.objects.get(name="Perú")),
                Site(name="Trujilo", country=Country.objects.get(name="Perú")),
                Site(name="Sala COP", country=Country.objects.get(name="Perú")),
                # Openplaza
                Site(name="Casa Matriz", country=Country.objects.get(name="Perú")),
                Site(name="Angamos", country=Country.objects.get(name="Perú")),
                Site(name="Piura", country=Country.objects.get(name="Perú")),
                Site(name="Huancayo", country=Country.objects.get(name="Perú")),
                Site(name="La Marina", country=Country.objects.get(name="Perú")),
                Site(name="Atocongo", country=Country.objects.get(name="Perú")),
                # Sitios de Colombia
                Site(name="Casa Matriz", country=Country.objects.get(name="Colombia")),
                Site(name="Cali", country=Country.objects.get(name="Colombia")),
                Site(name="Manizales", country=Country.objects.get(name="Colombia")),
                Site(name="Barranquilla", country=Country.objects.get(name="Colombia")),
                Site(name="Cartagena", country=Country.objects.get(name="Colombia")),
                Site(name="NQS", country=Country.objects.get(name="Colombia")),
                Site(name="Sala COP", country=Country.objects.get(name="Colombia")),
                # Sitios de Desconocido
                Site(name="Desconocido", country=Country.objects.get(name="Perú")),
                Site(name="Desconocido", country=Country.objects.get(name="Chile")),
                Site(name="Desconocido", country=Country.objects.get(name="Colombia")),
                Site(
                    name="Desconocido", country=Country.objects.get(name="Desconocido")
                ),
            ],
            ignore_conflicts=True,
        )

        # Definición de áreas por defecto
        # Sitios de Chile #####################################################################################
        site_casa_matriz_chile = Site.objects.get(
            name="Casa Matriz", country=Country.objects.get(name="Chile")
        )
        site_sala_cop_chile = Site.objects.get(
            name="Sala COP", country=Country.objects.get(name="Chile")
        )

        # Sitios de Mall Plaza
        site_alameda_chile = Site.objects.get(
            name="Alameda", country=Country.objects.get(name="Chile")
        )
        site_egana_chile = Site.objects.get(
            name="Egaña", country=Country.objects.get(name="Chile")
        )
        site_norte_chile = Site.objects.get(
            name="Norte", country=Country.objects.get(name="Chile")
        )
        site_sur_chile = Site.objects.get(
            name="Sur", country=Country.objects.get(name="Chile")
        )
        site_tobalada_chile = Site.objects.get(
            name="Tobalada", country=Country.objects.get(name="Chile")
        )
        site_bio_bio_chile = Site.objects.get(
            name="Bio Bio", country=Country.objects.get(name="Chile")
        )
        site_copiapó_chile = Site.objects.get(
            name="Copiapo", country=Country.objects.get(name="Chile")
        )
        site_arica_chile = Site.objects.get(
            name="Arica", country=Country.objects.get(name="Chile")
        )
        site_los_angeles_chile = Site.objects.get(
            name="Los Angeles", country=Country.objects.get(name="Chile")
        )
        site_los_dominicos_chile = Site.objects.get(
            name="Los Dominicos", country=Country.objects.get(name="Chile")
        )
        site_iquique_chile = Site.objects.get(
            name="Iquique", country=Country.objects.get(name="Chile")
        )
        site_antofagasta_chile = Site.objects.get(
            name="Antofagasta", country=Country.objects.get(name="Chile")
        )
        site_la_serena_chile = Site.objects.get(
            name="La Serena", country=Country.objects.get(name="Chile")
        )
        site_oeste_chile = Site.objects.get(
            name="Oeste", country=Country.objects.get(name="Chile")
        )
        site_vespucio_chile = Site.objects.get(
            name="Vespucio", country=Country.objects.get(name="Chile")
        )
        site_trebol_chile = Site.objects.get(
            name="Trebol", country=Country.objects.get(name="Chile")
        )
        site_calama_chile = Site.objects.get(
            name="Calama", country=Country.objects.get(name="Chile")
        )

        # Sitios de Perú #####################################################################################
        site_casa_matriz_peru = Site.objects.get(
            name="Casa Matriz", country=Country.objects.get(name="Perú")
        )

        # Sitios de Mall Plaza
        site_comas_peru = Site.objects.get(
            name="Comas", country=Country.objects.get(name="Perú")
        )
        site_arequipa_peru = Site.objects.get(
            name="Arequipa", country=Country.objects.get(name="Perú")
        )
        site_trujilo_peru = Site.objects.get(
            name="Trujilo", country=Country.objects.get(name="Perú")
        )
        site_bella_vista_peru = Site.objects.get(
            name="Bella Vista", country=Country.objects.get(name="Perú")
        )
        # Sitios de Open Plaza
        site_angamos_peru = Site.objects.get(
            name="Angamos", country=Country.objects.get(name="Perú")
        )
        site_piura_peru = Site.objects.get(
            name="Piura", country=Country.objects.get(name="Perú")
        )
        site_huancayo_peru = Site.objects.get(
            name="Huancayo", country=Country.objects.get(name="Perú")
        )
        site_la_marina_peru = Site.objects.get(
            name="La Marina", country=Country.objects.get(name="Perú")
        )
        site_atocongo_peru = Site.objects.get(
            name="Atocongo", country=Country.objects.get(name="Perú")
        )

        # Sitios de Colombia #####################################################################################
        site_casa_matriz_colombia = Site.objects.get(
            name="Casa Matriz", country=Country.objects.get(name="Colombia")
        )

        # Sitios de Mall Plaza
        site_cali_colombia = Site.objects.get(
            name="Cali", country=Country.objects.get(name="Colombia")
        )
        site_manizales_colombia = Site.objects.get(
            name="Manizales", country=Country.objects.get(name="Colombia")
        )
        site_barranquilla_colombia = Site.objects.get(
            name="Barranquilla", country=Country.objects.get(name="Colombia")
        )
        site_cartagena_colombia = Site.objects.get(
            name="Cartagena", country=Country.objects.get(name="Colombia")
        )
        site_nqs_colombia = Site.objects.get(
            name="NQS", country=Country.objects.get(name="Colombia")
        )

        # Sitios Desconocido
        site_desconocido_chile = Site.objects.get(
            name="Desconocido", country=Country.objects.get(name="Chile")
        )
        site_desconocido_peru = Site.objects.get(
            name="Desconocido", country=Country.objects.get(name="Perú")
        )
        site_desconocido_colombia = Site.objects.get(
            name="Desconocido", country=Country.objects.get(name="Colombia")
        )
        site_desconocido = Site.objects.get(
            name="Desconocido", country=Country.objects.get(name="Desconocido")
        )

        ##########################
        ####                  ####
        ####      Areas       ####
        ####                  ####
        ##########################
        Area.objects.bulk_create(
            [
                # Áreas de Chile #####################################################################################
                # Áreas de Casa Matriz Chile
                Area(name="Administracion", site=site_casa_matriz_chile),
                Area(name="Desconocido", site=site_casa_matriz_chile),
                # Áreas de Sala COP
                Area(name="COP", site=site_sala_cop_chile),
                Area(name="Desconocido", site=site_sala_cop_chile),
                # Áreas de Alameda
                Area(name="COP", site=site_alameda_chile),
                Area(name="Parking", site=site_alameda_chile),
                Area(name="Administracion", site=site_alameda_chile),
                Area(name="Desconocido", site=site_alameda_chile),
                # Áreas de Antofagasta
                Area(name="COP", site=site_antofagasta_chile),
                Area(name="Parking", site=site_antofagasta_chile),
                Area(name="Administracion", site=site_antofagasta_chile),
                Area(name="Desconocido", site=site_antofagasta_chile),
                # Áreas de Arica
                Area(name="COP", site=site_arica_chile),
                Area(name="Parking", site=site_arica_chile),
                Area(name="Administracion", site=site_arica_chile),
                Area(name="Desconocido", site=site_arica_chile),
                # Áreas de Bio Bio
                Area(name="COP", site=site_bio_bio_chile),
                Area(name="Parking", site=site_bio_bio_chile),
                Area(name="Administracion", site=site_bio_bio_chile),
                Area(name="Desconocido", site=site_bio_bio_chile),
                # Áreas de Calama
                Area(name="COP", site=site_calama_chile),
                Area(name="Parking", site=site_calama_chile),
                Area(name="Administracion", site=site_calama_chile),
                Area(name="Desconocido", site=site_calama_chile),
                # Áreas de Copiapó
                Area(name="COP", site=site_copiapó_chile),
                Area(name="Parking", site=site_copiapó_chile),
                Area(name="Administracion", site=site_copiapó_chile),
                Area(name="Desconocido", site=site_copiapó_chile),
                # Áreas de Egaña
                Area(name="COP", site=site_egana_chile),
                Area(name="Parking", site=site_egana_chile),
                Area(name="Administracion", site=site_egana_chile),
                Area(name="Desconocido", site=site_egana_chile),
                # Áreas de Iquique
                Area(name="COP", site=site_iquique_chile),
                Area(name="Parking", site=site_iquique_chile),
                Area(name="Administracion", site=site_iquique_chile),
                Area(name="Desconocido", site=site_iquique_chile),
                # Áreas de Los Angeles
                Area(name="COP", site=site_los_angeles_chile),
                Area(name="Parking", site=site_los_angeles_chile),
                Area(name="Administracion", site=site_los_angeles_chile),
                Area(name="Desconocido", site=site_los_angeles_chile),
                # Áreas de Los Dominicos
                Area(name="COP", site=site_los_dominicos_chile),
                Area(name="Parking", site=site_los_dominicos_chile),
                Area(name="Administracion", site=site_los_dominicos_chile),
                Area(name="Desconocido", site=site_los_dominicos_chile),
                # Áreas de La Serena
                Area(name="COP", site=site_la_serena_chile),
                Area(name="Parking", site=site_la_serena_chile),
                Area(name="Administracion", site=site_la_serena_chile),
                Area(name="Desconocido", site=site_la_serena_chile),
                # Áreas de Norte
                Area(name="COP", site=site_norte_chile),
                Area(name="Parking", site=site_norte_chile),
                Area(name="Administracion", site=site_norte_chile),
                Area(name="Desconocido", site=site_norte_chile),
                # Áreas de Oeste
                Area(name="COP", site=site_oeste_chile),
                Area(name="Parking", site=site_oeste_chile),
                Area(name="Administracion", site=site_oeste_chile),
                Area(name="Desconocido", site=site_oeste_chile),
                # Áreas de Sur
                Area(name="COP", site=site_sur_chile),
                Area(name="Parking", site=site_sur_chile),
                Area(name="Administracion", site=site_sur_chile),
                Area(name="Desconocido", site=site_sur_chile),
                # Áreas de Tobalada
                Area(name="COP", site=site_tobalada_chile),
                Area(name="Parking", site=site_tobalada_chile),
                Area(name="Administracion", site=site_tobalada_chile),
                Area(name="Desconocido", site=site_tobalada_chile),
                # Áreas de Trebol
                Area(name="COP", site=site_trebol_chile),
                Area(name="Parking", site=site_trebol_chile),
                Area(name="Administracion", site=site_trebol_chile),
                Area(name="Desconocido", site=site_trebol_chile),
                # Áreas de Vespucio
                Area(name="COP", site=site_vespucio_chile),
                Area(name="Parking", site=site_vespucio_chile),
                Area(name="Administracion", site=site_vespucio_chile),
                Area(name="Desconocido", site=site_vespucio_chile),
                # Áreas de Peru #####################################################################################
                # Áreas de Casa Matriz Perú
                Area(name="Administracion", site=site_casa_matriz_peru),
                Area(name="Desconocido", site=site_casa_matriz_peru),
                # Áreas de Arequipa
                Area(name="COP", site=site_arequipa_peru),
                Area(name="Parking", site=site_arequipa_peru),
                Area(name="Administracion", site=site_arequipa_peru),
                Area(name="Desconocido", site=site_arequipa_peru),
                # Áreas de Atocongo
                Area(name="COP", site=site_atocongo_peru),
                Area(name="Parking", site=site_atocongo_peru),
                Area(name="Administracion", site=site_atocongo_peru),
                Area(name="Desconocido", site=site_atocongo_peru),
                # Áreas de Angamos
                Area(name="COP", site=site_angamos_peru),
                Area(name="Parking", site=site_angamos_peru),
                Area(name="Administracion", site=site_angamos_peru),
                Area(name="Desconocido", site=site_angamos_peru),
                # Áreas de Bella Vista
                Area(name="COP", site=site_bella_vista_peru),
                Area(name="Parking", site=site_bella_vista_peru),
                Area(name="Administracion", site=site_bella_vista_peru),
                Area(name="Desconocido", site=site_bella_vista_peru),
                # Áreas de Comas
                Area(name="COP", site=site_comas_peru),
                Area(name="Parking", site=site_comas_peru),
                Area(name="Administracion", site=site_comas_peru),
                Area(name="Desconocido", site=site_comas_peru),
                # Áreas de Huancayo
                Area(name="COP", site=site_huancayo_peru),
                Area(name="Parking", site=site_huancayo_peru),
                Area(name="Administracion", site=site_huancayo_peru),
                Area(name="Desconocido", site=site_huancayo_peru),
                # Áreas de La Marina
                Area(name="COP", site=site_la_marina_peru),
                Area(name="Parking", site=site_la_marina_peru),
                Area(name="Administracion", site=site_la_marina_peru),
                Area(name="Desconocido", site=site_la_marina_peru),
                # Áreas de Piura
                Area(name="COP", site=site_piura_peru),
                Area(name="Parking", site=site_piura_peru),
                Area(name="Administracion", site=site_piura_peru),
                Area(name="Desconocido", site=site_piura_peru),
                # Áreas de Trujilo
                Area(name="COP", site=site_trujilo_peru),
                Area(name="Parking", site=site_trujilo_peru),
                Area(name="Administracion", site=site_trujilo_peru),
                Area(name="Desconocido", site=site_trujilo_peru),
                # Áreas de Colombia #####################################################################################
                # Áreas de Casa Matriz Colombia
                Area(name="Administracion", site=site_casa_matriz_colombia),
                Area(name="Desconocido", site=site_casa_matriz_colombia),
                # Áreas de Barranquilla
                Area(name="COP", site=site_barranquilla_colombia),
                Area(name="Parking", site=site_barranquilla_colombia),
                Area(name="Administracion", site=site_barranquilla_colombia),
                Area(name="Desconocido", site=site_barranquilla_colombia),
                # Áreas de Cali
                Area(name="COP", site=site_cali_colombia),
                Area(name="Parking", site=site_cali_colombia),
                Area(name="Administracion", site=site_cali_colombia),
                Area(name="Desconocido", site=site_cali_colombia),
                # Áreas de Cartagena
                Area(name="COP", site=site_cartagena_colombia),
                Area(name="Parking", site=site_cartagena_colombia),
                Area(name="Administracion", site=site_cartagena_colombia),
                Area(name="Desconocido", site=site_cartagena_colombia),
                # Áreas de Manizales
                Area(name="COP", site=site_manizales_colombia),
                Area(name="Parking", site=site_manizales_colombia),
                Area(name="Administracion", site=site_manizales_colombia),
                Area(name="Desconocido", site=site_manizales_colombia),
                # Áreas de NQS
                Area(name="COP", site=site_nqs_colombia),
                Area(name="Parking", site=site_nqs_colombia),
                Area(name="Administracion", site=site_nqs_colombia),
                Area(name="Desconocido", site=site_nqs_colombia),
                # Áreas de Desconocido
                Area(name="Desconocido", site=site_desconocido_chile),
                Area(name="Desconocido", site=site_desconocido_peru),
                Area(name="Desconocido", site=site_desconocido_colombia),
                Area(name="Desconocido", site=site_desconocido),
            ],
            ignore_conflicts=True,
        )

        ##########################
        ####                  ####
        #### Tipos De Equipos ####
        ####                  ####
        ##########################
        DeviceType.objects.bulk_create(
            [
                DeviceType(name="Router"),
                DeviceType(name="Switch"),
                DeviceType(name="Desconocido"),
            ],
            ignore_conflicts=True,
        )

        ##########################
        ####                  ####
        ####Reglas de Filtrado####
        ####                  ####
        ##########################
        rules = {
            "area": [
                {"value": "-TI-", "assign": "Administracion", "searchIn": ["hostname"]},
                {"value": "-COP-", "assign": "COP", "searchIn": ["hostname"]},
                {"value": "-PK-", "assign": "Parking", "searchIn": ["hostname"]},
            ],
            "site": [
                {"value": "-CM-", "assign": "Casa Matriz", "searchIn": ["hostname"]},
                {"value": "-PAL-", "assign": "Alameda", "searchIn": ["hostname"]},
                {"value": "-PAN-", "assign": "Antofagasta", "searchIn": ["hostname"]},
                {"value": "-PAR-", "assign": "Arica", "searchIn": ["hostname"]},
                {"value": "-PBB-", "assign": "Bio Bio", "searchIn": ["hostname"]},
                {"value": "-PCA-", "assign": "Calama", "searchIn": ["hostname"]},
                {"value": "-PCO-", "assign": "Copiapo", "searchIn": ["hostname"]},
                {"value": "-PEG-", "assign": "Egaña", "searchIn": ["hostname"]},
                {"value": "-PIQ-", "assign": "Iquique", "searchIn": ["hostname"]},
                {"value": "-PLA-", "assign": "Los Angeles", "searchIn": ["hostname"]},
                {"value": "-PLD-", "assign": "Los Dominicos", "searchIn": ["hostname"]},
                {"value": "-PLS-", "assign": "La Serena", "searchIn": ["hostname"]},
                {"value": "-PNO-", "assign": "Norte", "searchIn": ["hostname"]},
                {"value": "-POE-", "assign": "Oeste", "searchIn": ["hostname"]},
                {"value": "-PSU-", "assign": "Sur", "searchIn": ["hostname"]},
                {"value": "-PTO-", "assign": "Trebol", "searchIn": ["hostname"]},
                {"value": "-PVE-", "assign": "Vespucio", "searchIn": ["hostname"]},
                {"value": "-MAQ-", "assign": "Arequipa", "searchIn": ["hostname"]},
                {"value": "-MTR-", "assign": "Trujilo", "searchIn": ["hostname"]},
                {"value": "-MBV-", "assign": "Bella Vista", "searchIn": ["hostname"]},
                {"value": "-MCO-", "assign": "Comas", "searchIn": ["hostname"]},
                {"value": "-OPANG-", "assign": "Angamos", "searchIn": ["hostname"]},
                {"value": "-OPHUA-", "assign": "Huancayo", "searchIn": ["hostname"]},
                {"value": "-OPPIU-", "assign": "Piura", "searchIn": ["hostname"]},
                {"value": "-OPATO-", "assign": "Atocongo", "searchIn": ["hostname"]},
                {"value": "-OPLMA-", "assign": "La Marina", "searchIn": ["hostname"]},
                {"value": "-PMA-", "assign": "Manizales", "searchIn": ["hostname"]},
                {"value": "-PCG-", "assign": "Cartagena", "searchIn": ["hostname"]},
                {"value": "-NQS-", "assign": "NQS", "searchIn": ["hostname"]},
                {"value": "-PBQ-", "assign": "Barranquilla", "searchIn": ["hostname"]},
                {"value": "-PCL-", "assign": "Cali", "searchIn": ["hostname"]},
            ],
            "model": [],
            "country": [
                {"value": "PE-", "assign": "Perú", "searchIn": ["hostname"]},
                {"value": "CL-", "assign": "Chile", "searchIn": ["hostname"]},
                {"value": "CO-", "assign": "Colombia", "searchIn": ["hostname"]},
            ],
            "deviceType": [
                {"value": "-SW-", "assign": "Switch", "searchIn": ["hostname"]},
                {"value": "-RT-", "assign": "Router", "searchIn": ["hostname"]},
            ],
            "manufacturer": [
                {"value": "cisco", "assign": "Cisco", "searchIn": ["tags", "groups"]},
                {"value": "huawei", "assign": "Huawei", "searchIn": ["groups", "tags"]},
            ],
        }

        ClassificationRuleSet.objects.create(name="Mallplaza", rules=rules)

        ##########################
        ####                  ####
        ####  Super Usuario   ####
        ####                  ####
        ##########################
        if not UserSystem.objects.filter(username="admin").exists():
            UserSystem.objects.create_superuser(
                username="admin", email="admin@email.com", password="admin"
            )
            self.stdout.write(self.style.SUCCESS("✅ Superusuario admin creado"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Superusuario admin ya existe"))

        ##########################
        ####                  ####
        #### Backup Schedule  ####
        ####                  ####
        ##########################
        if not BackupSchedule.objects.exists():
            BackupSchedule.objects.create(
                scheduled_time=datetime.strptime('02:00', '%H:%M').time()
            )
            self.stdout.write(self.style.SUCCESS("✅ Horario de respaldo configurado para las 2:00 AM"))
        else:
            self.stdout.write(self.style.WARNING("⚠️  Ya existe una configuración de horario de respaldo"))

        self.stdout.write(
            self.style.SUCCESS("🎉 Datos iniciales cargados correctamente")
        )

