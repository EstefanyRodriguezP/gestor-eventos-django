from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from eventos.models import Evento

class Command(BaseCommand):
    help = 'Crea grupos y asigna permisos para el sistema de eventos'

    def handle(self, *args, **kwargs):
        # Crear grupos
        admin_group, _ = Group.objects.get_or_create(name='Administradores')
        organizador_group, _ = Group.objects.get_or_create(name='Organizadores')
        asistente_group, _ = Group.objects.get_or_create(name='Asistentes')

        # Obtener permisos del modelo Evento
        content_type = ContentType.objects.get_for_model(Evento)
        permisos = Permission.objects.filter(content_type=content_type)

        # Permisos para Administradores (todo)
        for permiso in permisos:
            admin_group.permissions.add(permiso)

        # Permisos para Organizadores (crear y cambiar)
        permisos_organizadores = permisos.filter(codename__in=['add_evento', 'change_evento'])
        for permiso in permisos_organizadores:
            organizador_group.permissions.add(permiso)

        # Asistentes no tienen permisos especiales sobre eventos
        # Pueden ver la lista pero no crear/editar/eliminar eventos

        self.stdout.write(self.style.SUCCESS('Grupos y permisos creados/actualizados con éxito'))
