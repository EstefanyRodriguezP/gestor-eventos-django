from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import Evento
from .forms import EventoForm
from django.urls import reverse_lazy

# Create your views here.

# Lista eventos, asistentes solo ven eventos públicos
class ListaEventosView(LoginRequiredMixin, ListView):
    model = Evento
    template_name = 'eventos/lista_eventos.html'
    context_object_name = 'eventos'

    def get_queryset(self):
        user = self.request.user
        # Administradores pueden ver todos
        if user.is_superuser or user.groups.filter(name='Administradores').exists():
            return Evento.objects.all()
        # Organizadores ven todos los eventos (pero solo pueden editar los suyos)
        if user.groups.filter(name='Organizadores').exists():
            return Evento.objects.all()
        # Asistentes solo ven eventos públicos
        if user.groups.filter(name='Asistentes').exists():
            return Evento.objects.filter(privado=False)
        # En caso de que no esté en ningún grupo
        return Evento.objects.none()

# Crear evento
class CrearEventoView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Evento
    form_class = EventoForm
    template_name = 'eventos/evento_form.html'
    success_url = reverse_lazy('eventos:lista_eventos')
    permission_required = 'eventos.add_evento'

    def form_valid(self, form):
        form.instance.creador = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Crear Evento"
        context['button_text'] = "Crear"
        return context

# Editar evento
class EditarEventoView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Evento
    form_class = EventoForm
    template_name = 'eventos/evento_form.html'
    success_url = reverse_lazy('eventos:lista_eventos')
    permission_required = 'eventos.change_evento'

    def dispatch(self, request, *args, **kwargs):
        evento = self.get_object()
        # Solo creador o admin pueden editar
        if evento.creador != request.user and not (request.user.groups.filter(name='Administradores').exists() or request.user.is_superuser):
            messages.error(request, "No tienes permisos para editar este evento.")
            return redirect('eventos:lista_eventos')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Editar Evento"
        context['button_text'] = "Guardar"
        return context

# Eliminar evento
class EliminarEventoView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Evento
    template_name = 'eventos/evento_confirm_delete.html'
    success_url = '/eventos/'
    permission_required = 'eventos.delete_evento'

# Ver detalle del evento
class DetalleEventoView(LoginRequiredMixin, DetailView):
    model = Evento
    template_name = 'eventos/detalle_evento.html'

    def get(self, request, *args, **kwargs):
        evento = self.get_object()
        if evento.privado and request.user.groups.filter(name='Asistentes').exists():
            messages.error(request, "No tienes permiso para ver este evento privado.")
            return redirect('eventos:lista_eventos')
        return super().get(request, *args, **kwargs)

# Registro de usuarios con asignación automática a grupo Asistentes
def registro(request):
    if request.method == 'POST':
        print("POST data:", request.POST)  # Para ver datos recibidos
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            grupo_asistente = Group.objects.get(name='Asistentes')
            user.groups.add(grupo_asistente)
            messages.success(request, 'Usuario registrado correctamente.')
            return redirect('login')
        else:
            print("Form errors:", form.errors)  # Para ver errores del formulario
    else:
        form = UserCreationForm()
    return render(request, 'eventos/registro.html', {'form': form})

# Vista para acceso denegado (handler 403)
def permiso_denegado(request, exception=None):
    messages.error(request, "No tienes permiso para acceder a esta página.")
    return redirect('eventos:lista_eventos')

# Agregar vista para registrarse a un evento
@login_required
def registrar_asistencia(request, pk):
    evento = get_object_or_404(Evento, pk=pk)
    
    if request.user.groups.filter(name='Asistentes').exists():
        evento.asistentes.add(request.user)
        messages.success(request, "Te has registrado al evento correctamente.")
    else:
        messages.error(request, "Solo los asistentes pueden registrarse a eventos.")
    
    return redirect('eventos:detalle_evento', pk=pk)