# Importaciones de Django
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import render, redirect
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.core.mail import send_mail  
from django.shortcuts import get_object_or_404
from django.contrib.auth import logout
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from django.contrib.auth.models import User
from django.http import Http404
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from datetime import datetime
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.views import generic
from django import forms

# Importaciones locales
from .forms import CustomUserCreationForm
from .models import FactoryOwner
from .models import Operator
from .models import Plan
from .forms import OperatorForm
from .forms import ClientForm
from .models import Remission
from .models import Client
from .forms import RemissionForm, BatchForm  
from datetime import datetime
from .forms import GarmentTypeForm
from .models import GarmentType, DistinctiveFeature  
from .forms import CostSimulationForm  
from .models import CostSimulation
from .models import ProfitSimulation
from .forms import ProfitSimulationForm
from .models import CuttingTable
from .forms import CuttingTableForm
from .models import GarmentPart
from .forms import GarmentPartFormSet
from .models import Size
from .forms import SizeForm
from .models import Operation
from .forms import OperationForm
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import FabricType
from .forms import FabricTypeForm
from .forms import RemissionSizeQuantityFormSet
from .models import RemissionSizeQuantity
from .forms import RemissionSizeQuantityForm
from .decorators import factory_owner_required  # Ajusta la ruta de importación según sea necesario
from rest_framework import viewsets
from .serializers import OperationSerializer, FabricTypeSerializer, DistinctiveFeatureSerializer, GarmentTypeSerializer
from .forms import DistinctiveFeatureForm
from .models import DistinctiveFeature
from .forms import CuttingServiceForm
from .models import CuttingService


#VIEWS SET
class OperationViewSet(viewsets.ModelViewSet):
    queryset = Operation.objects.all()
    serializer_class = OperationSerializer

class FabricTypeViewSet(viewsets.ModelViewSet):
    queryset = FabricType.objects.all()
    serializer_class = FabricTypeSerializer

class DistinctiveFeatureViewSet(viewsets.ModelViewSet):
    queryset = DistinctiveFeature.objects.all()
    serializer_class = DistinctiveFeatureSerializer

class GarmentTypeViewSet(viewsets.ModelViewSet):
    queryset = GarmentType.objects.all()
    serializer_class = GarmentTypeSerializer
#VIEWS SET FINISH


class ErrorView(TemplateView):
    template_name = "error_page.html"
    
    
def home_view(request):
    return render(request, 'inicio.html')


def email_confirm_view(request, token):
    User = get_user_model()
    
    try:
        user = User.objects.get(factory_owner__confirmation_token=token)
    except User.DoesNotExist:
        # Si no se encuentra ningún usuario con el token proporcionado, mostramos un mensaje de error
        messages.error(request, "Token de confirmación no válido o expirado.")
        return redirect('inicio')  # reemplaza 'inicio' con el nombre de la URL de tu página de inicio
    else:
        # Si encontramos un usuario con el token proporcionado, activamos su cuenta
        if user.is_active:
            messages.info(request, 'Tu correo electrónico ya ha sido confirmado anteriormente.')
        else:
            user.is_active = True
            user.factory_owner.confirmation_token = ''
            user.factory_owner.save()
            messages.success(request, 'Tu correo electrónico ha sido confirmado.')
    
    return redirect('inicio')  # reemplaza 'inicio' con el nombre de la URL de tu página de inicio

    
# Vista de Registro
def register_view(request):
    plan_id = request.GET.get('plan_id', None)
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Añade commit=False para evitar guardar el usuario por ahora
            user.email = form.cleaned_data.get('email')  # Obtén el email del formulario
            user.set_password(form.cleaned_data.get('password1'))  # Obtén la contraseña del formulario
            
            # Verifica si el correo electrónico ya está en uso
            if FactoryOwner.objects.filter(email=user.email).exists():
                messages.error(request, 'Esta dirección de correo electrónico ya está siendo utilizada por otro usuario.')
                return render(request, 'registro.html', {'form': form})
            
            user.save()
            
            # Aquí, el plan debería ser obtenido usando el plan_id de una manera segura
            try:
                plan = Plan.objects.get(id=plan_id)
            except Plan.DoesNotExist:
                plan = None  # o establece un plan predeterminado
            
            factory_owner = FactoryOwner.objects.create(user=user, plan=plan)  # Aquí asignamos el plan y guardamos la referencia al objeto creado
            
            # Generar un token único
            token = default_token_generator.make_token(user)
            
            # Guardar el token en la base de datos (Asegúrate de agregar el campo 'confirmation_token' en tu modelo)
            factory_owner.confirmation_token = token
            factory_owner.save()
            
            # Construir URL de confirmación
            confirm_url = request.build_absolute_uri(reverse('email_confirm', args=[token]))
            
            # Enviar correo electrónico de confirmación
            send_mail(
                'Confirmación de correo electrónico',
                f'Haga clic en el siguiente enlace para confirmar su correo electrónico: {confirm_url}',
                'noreply@tusitio.com',
                [user.email],
                fail_silently=False,
            )
            
            # Mensaje de éxito y redirección dependiendo del plan
            if factory_owner.plan and factory_owner.plan.name == 'Plan Estándar':
                messages.success(request, 'Registro exitoso. Por favor revisa tu correo para confirmar tu cuenta.')
                login(request, user)
                return redirect('dashboard_estandar_fo')  # Redirecciona al dashboard estándar
            else:
                messages.success(request, 'Registro exitoso. Por favor revisa tu correo para confirmar tu cuenta.')
                login(request, user)
                return redirect('inicio')  # Redirecciona al inicio para otros casos
        else:
            messages.error(request, 'Ocurrió un error en el registro.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registro.html', {'form': form})




  
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)  # Aquí usamos simplemente 'login'

            # Verificar el tipo de usuario y redirigirlo a su dashboard específico
            try:
                factory_owner = FactoryOwner.objects.get(user=user)  # Asegúrate de que 'user' está correctamente definido en tu modelo FactoryOwner
                print(f"Factory owner retrieved: {factory_owner}")  # <-- Nueva línea de diagnóstico
                print(f"Factory owner plan name: {factory_owner.plan.name}")  # <-- Nueva línea de diagnóstico
            except FactoryOwner.DoesNotExist:
                factory_owner = None

            if factory_owner and factory_owner.plan.name == 'Plan Estándar':
                messages.success(request, "Has iniciado sesión exitosamente como Factory Owner Estándar!")  # Mensaje de éxito
                return redirect('dashboard_estandar_fo')  # Asegúrate de que 'dashboard_estandar_fo' está definido en tu archivo urls.py
            else:
                messages.error(request, "Ha ocurrido un error con tu plan. Por favor, contacta al soporte.")  
                return redirect('inicio')  
        else:
            messages.success(request, "Has iniciado sesión exitosamente!")  
            return redirect('inicio')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})



# Vista de Cierre de Sesion
def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado la sesión exitosamente.')  # Mensaje de éxito
    return redirect('inicio')
    
# Vista de Cambio de Contraseña
@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            # Actualizar la sesión de autenticación para evitar que el usuario sea desconectado
            update_session_auth_hash(request, user)

            # Determina el tipo de usuario y redirige al perfil correspondiente
            if FactoryOwner.objects.filter(user=request.user).exists():
                return redirect('factoryowner_perfil')
            elif Operator.objects.filter(user=request.user).exists():
                return redirect('operator_perfil')
            else:
                messages.success(request, 'Registro exitoso. Bienvenido!')
                # En caso de que el usuario no tenga un perfil asociado, redirige a 'nombre_url_inicio'
                return redirect('nombre_url_inicio')

    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'cambio_contrasena.html', {'form': form})

# Vista de Restablecimiento de Contraseña (Solicitud)
@login_required
def password_reset_request_view(request):
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Se ha enviado un correo electrónico con instrucciones para restablecer su contraseña.')
            return redirect('password_reset_done')  # Suponiendo que 'password_reset_done' es el nombre de la URL de la página de confirmación
    else:
        form = PasswordResetForm()
    return render(request, "restablecer_contrasena_solicitud.html", {"form": form})

# Vista para Restablecimiento de Contraseña (Confirmación)
@login_required
def password_reset_confirm_view(request, uidb64, token):
    User = get_user_model()
    try:
        # Decodifica el uidb64 para obtener el ID del usuario
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Comprueba que el token es válido
    if user is not None and default_token_generator.check_token(user, token):
        if request.method == "POST":
            form = SetPasswordForm(user=user, data=request.POST)
            if form.is_valid():
                form.save()
                return redirect('login')
        else:
            form = SetPasswordForm(user=user)
        return render(request, "restablecer_contrasena_confirmacion.html", {"form": form})
    else:
        messages.success(request, 'Tu cambio de contraseña ha sido exitoso!')
        # Maneja el caso en el que el token no es válido, como mostrar un mensaje de error
        return render(request, "restablecer_contrasena_invalido.html")
    
@login_required
@factory_owner_required
def factoryowner_profile_view(request):
    try:
        # Intenta obtener el perfil del usuario
        profile = FactoryOwner.objects.get(user=request.user)
        plan = profile.plan  # Obtener el plan del usuario

        # Si todo va bien, renderiza la plantilla con el perfil del usuario y su plan
        return render(request, 'profile/factoryowner/factoryowner_profile.html', {'profile': profile, 'plan': plan})
    except FactoryOwner.DoesNotExist:
        # Si el perfil no existe, maneja la excepción
        messages.error(request, 'Perfil no encontrado.')
        return redirect('inicio')



@login_required
def operator_profile_view(request):
    try:
        # Intenta obtener el perfil del usuario
        profile = Operator.objects.get(user=request.user)
        # Si todo va bien, renderiza la plantilla con el perfil del usuario
        return render(request, 'profile/operator/operator_profile.html', {'profile': profile})
    except Operator.DoesNotExist:
        # Si el perfil no existe, maneja la excepción
        messages.error(request, 'Perfil no encontrado.')
        return redirect('inicio')  # o a cualquier otra página que consideres apropiada

def perfil_view(request):
    if FactoryOwner.objects.filter(id=request.user.id).exists():
        return redirect('factoryowner_perfil')
    elif Operator.objects.filter(id=request.user.id).exists():
        return redirect('operator_perfil')
    else:
        messages.error(request, 'Perfil no encontrado.')
        return redirect('inicio')


@login_required
def editar_perfil_view(request):
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            messages.success(request, 'Tu perfil ha sido actualizado exitosamente!')
            return redirect('perfil')  # o redirige a donde quieras después de editar el perfil
    else:
        form = UserChangeForm(instance=request.user)

    return render(request, 'editar_perfil.html', {'form': form})

def show_plans_view(request):
    active_plans = Plan.objects.filter(is_active=True).order_by('display_order')
    return render(request, 'plans.html', {'plans': active_plans})

@login_required
@factory_owner_required
def add_operator_view(request):
    # Asumiendo que tienes una relación ForeignKey de FactoryOwner a User
    factory_owner = FactoryOwner.objects.get(user=request.user)

    # Verifica si ha alcanzado el límite de operadores
    if factory_owner.operators.count() >= factory_owner.plan.max_operators:
        messages.error(request, 'Has alcanzado el límite máximo de operadores para tu plan.')
        return redirect('operator_list')  # Redirecciona a la página que muestra la lista de operadores

    if request.method == 'POST':
        form = OperatorForm(factory_owner=factory_owner, data=request.POST)  # Pasando factory_owner aquí
        if form.is_valid():
            operator = form.save(commit=False)
            operator.factory_owner = factory_owner  # Asumiendo que Operator tiene una ForeignKey a FactoryOwner
            operator.save()
            messages.success(request, 'Operador agregado exitosamente.')
            return redirect('operator_list')  # Redirecciona a la página que muestra la lista de operadores
    else:
        form = OperatorForm(factory_owner=factory_owner)  # Pasando factory_owner aquí también

    return render(request, 'add_operator.html', {'form': form})

@login_required
@factory_owner_required
def operator_list(request):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    operators = factory_owner.operators.all()
    
    # Obtén la fecha actual y la fecha de inicio del período (15 días antes)
    now = timezone.now()
    start_date = now - timedelta(days=15)
    
    for operator in operators:
        operator.arrangements_count = operator.arrangements.filter(created_at__gte=start_date, created_at__lte=now).count()
    
    context = {'operators': operators}
    return render(request, 'operator_list.html', context)

    
@login_required
@factory_owner_required
def edit_operator_view(request, operator_id):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    operator = get_object_or_404(Operator, id=operator_id, factory_owner=factory_owner)

    if request.method == 'POST':
        form = OperatorForm(request.POST, instance=operator, factory_owner=factory_owner)
        if form.is_valid():
            form.save()
            messages.success(request, 'Operador actualizado exitosamente.')
            return redirect('operator_list')
    else:
        form = OperatorForm(instance=operator, factory_owner=factory_owner)

    return render(request, 'edit_operator.html', {'form': form})

    
@login_required
@factory_owner_required
def delete_operator_view(request, operator_id):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    operator = get_object_or_404(Operator, id=operator_id, factory_owner=factory_owner)

    if request.method == 'POST':
        operator.delete()
        messages.success(request, 'Operador eliminado exitosamente.')
        return redirect('operator_list')

    return render(request, 'delete_operator.html', {'operator': operator})


@login_required
@factory_owner_required
def add_client_view(request):
    factory_owner = FactoryOwner.objects.get(user=request.user)

    # Verificación del límite de clientes según el plan del factory_owner
    if request.user.clients.count() >= factory_owner.plan.max_clients:
        return JsonResponse({'message': 'Has alcanzado el límite máximo de clientes para tu plan.'}, status=400)

    if request.method == 'POST':
        form = ClientForm(request.POST)
        if form.is_valid():
            nit = form.cleaned_data.get('NIT')
            email = form.cleaned_data.get('email')
            
            # Verificar si el cliente ya está asociado con el factory_owner actual
            existing_client = request.user.clients.filter(Q(NIT=nit) | Q(email=email)).first()
            
            if existing_client:
                return JsonResponse({'message': 'El cliente ya está asociado con tu cuenta.', 'name': existing_client.name, 'id': existing_client.id}, status=200)

            # Si no está asociado, verificar si el cliente ya existe en la base de datos
            existing_client_in_db = Client.objects.filter(Q(NIT=nit) | Q(email=email)).first()
            
            if existing_client_in_db:
                existing_client_in_db.factory_owners.add(request.user)
                return JsonResponse({'message': 'Cliente existente agregado exitosamente.', 'name': existing_client_in_db.name, 'id': existing_client_in_db.id}, status=200)
            else:
                # Crear un nuevo cliente
                client = Client(
                    name=form.cleaned_data.get('name'),
                    NIT=nit,
                    email=email,
                    address=form.cleaned_data.get('address'),
                    phone_number=form.cleaned_data.get('phone_number'),
                )
                client.save()
                client.factory_owners.add(request.user)
                return JsonResponse({'message': 'Cliente agregado exitosamente.', 'name': client.name, 'id': client.id}, status=200)
        else:
            # Incluyendo los errores específicos del formulario en la respuesta
            return JsonResponse({'message': 'Error al crear el cliente.', 'errors': form.errors}, status=400)
    else:  # Esto manejará solicitudes GET
        form = ClientForm()  # Crea una instancia del formulario vacío
        return render(request, 'add_client.html', {'form': form})  # Renderiza una plantilla con el formulario





@login_required   
@factory_owner_required 
def client_list_view(request):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    clients = Client.objects.filter(factory_owners=request.user)
    
    context = {'clients': clients}
    return render(request, 'client_list.html', context)


@login_required
@factory_owner_required
def edit_client_view(request, client_id):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    client = get_object_or_404(Client, id=client_id)
    if not client.factory_owners.filter(id=factory_owner.user.id).exists():
        raise Http404("No Client matches the given query.")


    if request.method == 'POST':
        form = ClientForm(request.POST, instance=client)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado exitosamente.')
            return redirect('client_list')
    else:
        form = ClientForm(instance=client)

    return render(request, 'edit_client.html', {'form': form})


@login_required
@factory_owner_required
def delete_client_view(request, client_id):
    factory_owner = FactoryOwner.objects.get(user=request.user)

    try:
        client = Client.objects.get(id=client_id)
    except Client.DoesNotExist:
        raise Http404("Cliente no encontrado.")

    if not client.factory_owners.filter(id=factory_owner.user.id).exists():
        raise Http404("No tienes permiso para eliminar este cliente.")

    if request.method == 'POST':
        client.factory_owners.remove(factory_owner.user)
        if not client.factory_owners.exists():
            client.delete()
        messages.success(request, 'Cliente eliminado exitosamente.')
        return redirect('client_list')

    return render(request, 'delete_client.html', {'client': client})


from datetime import datetime
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
# Asegúrate de importar todos los modelos y formularios necesarios aquí

@login_required
@factory_owner_required
def add_remission_view(request):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    current_month_remissions = factory_owner.remissions.filter(created_at__month=datetime.now().month).count()

    if current_month_remissions >= factory_owner.plan.max_remissions_per_month:
        messages.error(request, 'Has alcanzado el límite de remisiones para este mes según tu plan.')
        return redirect('remission_list')

    garment_type_form = GarmentTypeForm()
    client_form = ClientForm()
     # Obtén solo los FabricType asociados con el FactoryOwner logueado
    fabric_types = FabricType.objects.filter(factory_owner=factory_owner)
    operations = Operation.objects.filter(factory_owner=factory_owner)  # Mueve esta línea aquí
    clients = Client.objects.filter(factory_owners=request.user)
    if request.method == "POST":
        form = RemissionForm(request.POST)
        formset = RemissionSizeQuantityFormSet(request.POST, prefix='rsq')
        batch_form = BatchForm(request.POST)

        # ... (código para manejar la creación de nuevos tipos de prenda y nuevos clientes)

        # Manejar la creación de una nueva remisión
        if form.is_valid() and formset.is_valid() and batch_form.is_valid():
            remission = form.save(commit=False)
            remission.factory_owner = factory_owner

            # Antes de guardar la remisión, obtenemos los datos de los formularios validados
            remission_number = form.cleaned_data.get('number')
            batch_number = batch_form.cleaned_data.get('batch_number')


            if not remission_number or not batch_number:
                messages.error(request, 'Número de remisión o número de lote no proporcionado.')
                return render(request, 'add_remission.html', context)

            # Crear o obtener una tanda existente
            batch, created = Batch.objects.get_or_create(number=batch_number)
            remission.batch = batch
            remission.number = remission_number  # Asegúrate de que tu modelo Remission tenga un campo llamado 'number' para almacenar el número de remisión
            remission.save()

            for instance_form in formset:
                if instance_form.is_valid():
                    instance = instance_form.save(commit=False)
                    instance.remission = remission

                    try:
                        existing_instance = RemissionSizeQuantity.objects.get(
                            remission=remission, size=instance.size)
                        existing_instance.quantity += instance.quantity
                        existing_instance.save()
                    except RemissionSizeQuantity.DoesNotExist:
                        instance.save()


            # Calcular y guardar el total de la cantidad y el valor total
            remission.total_value = remission.total_value_COP()
            remission.save()

            messages.success(request, 'Remisión añadida con éxito.')
            return redirect('remission_list')
        else:
            if not form.is_valid():
                messages.error(request, 'Formulario de remisión no válido.')
            if not formset.is_valid():
                messages.error(request, 'Formset no válido.')
            if not batch_form.is_valid():
                messages.error(request, 'Formulario de lote no válido.')


    else:  # Este bloque else manejará las solicitudes GET
        form = RemissionForm()
        formset = RemissionSizeQuantityFormSet(queryset=RemissionSizeQuantity.objects.none(), prefix='rsq')
        batch_form = BatchForm()

    context = {
        'form': form,
        'formset': formset,
        'batch_form': batch_form,
        'garment_type_form': garment_type_form,
        'client_form': client_form,
        'operations': operations,
        'clients': clients,
        'fabric_types': fabric_types,
    }
    return render(request, 'add_remission.html', context)


    

@login_required    
@factory_owner_required
def remission_list_view(request):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    remissions = factory_owner.remissions.all()

    context = {'remissions': remissions}
    return render(request, 'remission_list.html', context)
    
@login_required
@factory_owner_required
def update_remission_view(request, remission_id):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    remission = get_object_or_404(Remission, id=remission_id, factory_owner=factory_owner)

    RemissionSizeQuantityFormSet = modelformset_factory(RemissionSizeQuantity, fields=('size', 'quantity'), extra=1)

    if request.method == "POST":
        form = RemissionForm(request.POST, instance=remission)
        formset = RemissionSizeQuantityFormSet(request.POST, queryset=RemissionSizeQuantity.objects.filter(remission=remission))
        if form.is_valid() and formset.is_valid():
            remission = form.save()
            instances = formset.save(commit=False)
            for instance in instances:
                instance.remission = remission
                instance.save()
            formset.save_m2m()
            messages.success(request, 'Remisión actualizada con éxito.')
            return redirect('remission_list')
    else:
        form = RemissionForm(instance=remission)
        formset = RemissionSizeQuantityFormSet(queryset=RemissionSizeQuantity.objects.filter(remission=remission))

    context = {'form': form, 'formset': formset, 'remission': remission}
    return render(request, 'update_remission.html', context)



@login_required
@factory_owner_required
def remission_detail_view(request, remission_id):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    remission = get_object_or_404(Remission, id=remission_id, factory_owner=factory_owner)

    context = {'remission': remission}
    return render(request, 'remission_detail.html', context)


@login_required    
@factory_owner_required
def delete_remission_view(request, remission_id):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    remission = get_object_or_404(Remission, id=remission_id, factory_owner=factory_owner)

    if request.method == "POST":
        remission.delete()
        messages.success(request, 'Remisión eliminada con éxito.')
        return redirect('remission_list')

    context = {'remission': remission}
    return render(request, 'delete_ .html', context)
    
@login_required
@factory_owner_required
def gestion_remisiones_view(request):
    return render(request, 'gestion_remisiones.html')    


@login_required
@factory_owner_required
def add_factory_admin_view(request):
    # Asumiendo que tienes una relación ForeignKey de FactoryOwner a User
    factory_owner = FactoryOwner.objects.get(user=request.user)

    # Verifica si ha alcanzado el límite de administradores
    if factory_owner.factory_admins.count() >= factory_owner.plan.max_admins:
        messages.error(request, 'Has alcanzado el límite máximo de administradores para tu plan.')
        return redirect('factory_admin_list')  # Redirecciona a la página que muestra la lista de administradores

    if request.method == 'POST':
        form = FactoryAdminForm(request.POST)  # Asumiendo que tienes un formulario llamado FactoryAdminForm
        if form.is_valid():
            admin = form.save(commit=False)
            admin.factory_owner = factory_owner  # Asumiendo que FactoryAdmin tiene una ForeignKey a FactoryOwner
            admin.save()
            messages.success(request, 'Administrador agregado exitosamente.')
            return redirect('factory_admin_list')  # Redirecciona a la página que muestra la lista de administradores
    else:
        form = FactoryAdminForm()

    return render(request, 'add_factory_admin.html', {'form': form})

@login_required
@factory_owner_required
def factory_admin_list_view(request):
    # Asegurarte de que el usuario actual es un FactoryOwner
    factory_owner = FactoryOwner.objects.get(user=request.user)

    # Obtener todos los administradores de fábrica asociados con este FactoryOwner
    factory_admins = factory_owner.factory_admins.all()

    return render(request, 'factory_admin_list.html', {'factory_admins': factory_admins})
    
    

@login_required
def add_garment_type_view(request):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    
    # Verifica si ha alcanzado el límite de tipos de prendas
    if factory_owner.garment_types.count() >= factory_owner.plan.max_garment_types:
        return JsonResponse({'message': 'Has alcanzado el límite máximo de tipos de prendas para tu plan.'}, status=400)
    
    if request.method == "POST":
        print(request.POST)  # Imprime los datos enviados para depuración

        form = GarmentTypeForm(request.POST)
        if form.is_valid():
            garment_type = form.save(commit=False)
            garment_type.factory_owner = factory_owner
            default_client_id = get_default_client_id()  # Asegúrate de haber definido esta función
            if not garment_type.client_id:
                garment_type.client_id = default_client_id
            garment_type.save()

            # Añadir las operaciones seleccionadas
            selected_operations_ids = request.POST.getlist('operations')
            print("Selected operations IDs:", selected_operations_ids)  # Para depuración



            for operation_id in selected_operations_ids:
                try:
                    operation = Operation.objects.get(id=operation_id)
                    garment_type.operations.add(operation)
                except Operation.DoesNotExist:
                    return JsonResponse({'message': f'Operación con ID {operation_id} no encontrada.'}, status=400)  # Manejo de error mejorado


            # Manejo de nuevas características distintivas
            new_features = request.POST.getlist('distinctive_features[]')
            for feature_name in new_features:
                feature_name = feature_name.strip()
                if feature_name:  # Asegúrate de que el nombre no esté vacío
                    feature, created = DistinctiveFeature.objects.get_or_create(
                        name=feature_name, 
                        factory_owner=factory_owner
                    )
                    garment_type.distinctive_features.add(feature)

            garment_type.save()  # Guarda el objeto después de añadir todas las relaciones

            return JsonResponse({'message': 'Tipo de prenda añadido exitosamente.', 'id': garment_type.id, 'name': str(garment_type)}, status=200)
        else:
            return JsonResponse({'message': 'Error al crear el tipo de prenda.', 'errors': form.errors}, status=400)
    else:
        return JsonResponse({'message': 'Método no permitido.'}, status=405)



def get_default_client_id():
    # Define la lógica para obtener el client_id predeterminado
    # Por ahora, estoy devolviendo 1 como un valor de marcador de posición
    # Deberías reemplazar esto con tu propia lógica
    return 1



def get_unit_price(request, garment_type_id):
    try:
        garment_type = GarmentType.objects.get(id=garment_type_id)
        unit_price = garment_type.base_price_COP  # Asume que este es el nombre del campo para el precio unitario
        fabric_type = garment_type.fabric_type  # Asume que este es el nombre del campo para el tipo de tela
        operations = garment_type.operations.values_list('name', flat=True)
        print("Operations:", operations)  # Añade esta línea para depurar
        response_data = {
            "unit_price": unit_price,
            "fabric_type": str(fabric_type),
            'operations': list(operations),
    }

        return JsonResponse(response_data)
    except GarmentType.DoesNotExist:
        return JsonResponse({"error": "GarmentType not found"}, status=404)

@login_required
@factory_owner_required
def garment_type_list_view(request):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    garment_types = factory_owner.garment_types.all()
    
    return render(request, 'garment_type_list.html', {'garment_types': garment_types})


@login_required
@factory_owner_required
def gestion_prendas_view(request):
    return render(request, 'gestion_prendas.html')
    

@login_required
@factory_owner_required
def dashboard_estandar_fo_view(request):
    # Obtén el objeto FactoryOwner asociado con el usuario actual
    try:
        factory_owner = FactoryOwner.objects.get(user=request.user)
    except FactoryOwner.DoesNotExist:
        factory_owner = None

    # Si el usuario no es un FactoryOwner, redirígelos a una página diferente (por ejemplo, la página de inicio)
    if not factory_owner:
        return redirect('inicio')  # Reemplaza 'inicio' con la URL que deseas usar

    # Aquí puedes obtener cualquier dato que quieras enviar a tu template
    # Por ejemplo, el número total de operarios, clientes, etc.
    operators = Operator.objects.filter(factory_owner=factory_owner)
    clientes = Client.objects.filter(factory_owners=request.user)  # Nota: 'factory_owners' en lugar de 'factory_owner'
    garment_types = GarmentType.objects.filter(factory_owner=factory_owner)  # Asegúrate de que 'GarmentType' sea el nombre correcto del modelo
    remissions = Remission.objects.filter(factory_owner=factory_owner)  # Asegúrate de que 'Remission' sea el nombre correcto del modelo

    context = {
        'factory_owner': factory_owner,
        'num_operators': operators.count(),
        'num_clientes': clientes.count(),
        'num_garment_types': garment_types.count(),
        'num_remisions': remissions.count(),
        # ... (cualquier otro dato que quieras incluir)
    }

    return render(request, 'dashboard_estandar_fo.html', context)
    

@login_required
@factory_owner_required
def add_cost_simulation_view(request):
    if request.method == 'POST':
        form = CostSimulationForm(request.POST)
        if form.is_valid():
            cost_simulation = form.save(commit=False)
            # Aquí puedes añadir cualquier otro campo que necesite ser llenado antes de guardar el objeto
            cost_simulation.save()
            messages.success(request, 'Simulación de costos creada exitosamente.')
            return redirect('cost_simulation_list')  # redirecciona a la lista de simulaciones de costos
    else:
        form = CostSimulationForm()

    context = {'form': form}
    return render(request, 'add_cost_simulation.html', context)


@login_required
@factory_owner_required
def cost_simulation_detail_view(request, pk):
    factory_owner = request.user.factoryowner
    cost_simulation = get_object_or_404(CostSimulation, pk=pk, factory_owner=factory_owner)
    return render(request, 'cost_simulation_detail.html', {'cost_simulation': cost_simulation})


@login_required
@factory_owner_required
def update_cost_simulation_view(request, id):
    cost_simulation = get_object_or_404(CostSimulation, id=id)

    if request.method == 'POST':
        form = CostSimulationForm(request.POST, instance=cost_simulation)
        if form.is_valid():
            form.save()
            messages.success(request, 'Simulación de costos actualizada exitosamente.')
            return redirect('cost_simulation_detail', id=id)
    else:
        form = CostSimulationForm(instance=cost_simulation)

    return render(request, 'update_cost_simulation.html', {'form': form})

@login_required
@factory_owner_required
def delete_cost_simulation_view(request, id):
    cost_simulation = get_object_or_404(CostSimulation, id=id)

    if request.method == 'POST':
        cost_simulation.delete()
        messages.success(request, 'Simulación de costos eliminada exitosamente.')
        return redirect('cost_simulation_list')

    return render(request, 'delete_cost_simulation.html', {'cost_simulation': cost_simulation})
    

@login_required
@factory_owner_required
def cost_simulation_list_view(request):
    # Obtén todas las simulaciones de costo
    cost_simulations = CostSimulation.objects.all()

    # Renderiza el template con las simulaciones de costo como contexto
    return render(request, 'list_cost_simulation.html', {'cost_simulations': cost_simulations})


@login_required
@factory_owner_required
def add_profit_simulation_view(request):
    if request.method == 'POST':
        form = ProfitSimulationForm(request.POST)
        if form.is_valid():
            profit_simulation = form.save(commit=False)
            profit_simulation.save()
            messages.success(request, 'Simulación de ganancias creada exitosamente.')
            return redirect('profit_simulation_list')
    else:
        form = ProfitSimulationForm()

    context = {'form': form}
    return render(request, 'add_profit_simulation.html', context)
    
@login_required    
@factory_owner_required
def profit_simulation_list_view(request):
    simulations = ProfitSimulation.objects.all()
    return render(request, 'profit_simulation_list.html', {'simulations': simulations})
    
@method_decorator(login_required, name='dispatch')
class CuttingServiceCreateView(generic.CreateView):
    model = CuttingService
    form_class = CuttingServiceForm
    template_name = 'cutting_service_form.html'

    def form_valid(self, form):
        factory_owner = FactoryOwner.objects.get(user=self.request.user)
        form.instance.factory_owner = factory_owner
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('cutting_service_detail', kwargs={'pk': self.object.pk})
        

class CuttingServiceDetailView(generic.DetailView):
    model = CuttingService
    template_name = 'cutting_service_detail.html'


class CuttingServiceUpdateView(generic.UpdateView):
    model = CuttingService
    form_class = CuttingServiceForm
    template_name = 'cutting_service_form.html'

    def get_success_url(self):
        return reverse_lazy('cutting_service_detail', kwargs={'pk': self.object.pk})



class CuttingServiceDeleteView(generic.DeleteView):
    model = CuttingService
    template_name = 'cutting_service_confirm_delete.html'
    success_url = reverse_lazy('cutting_service_list')


class CuttingServiceListView(generic.ListView):
    model = CuttingService
    template_name = 'cutting_service_list.html'
    context_object_name = 'cutting_services'



class CuttingServiceForm(forms.Form):
    cutting_service = forms.ChoiceField(
        choices=[('yes', 'Con servicio de corte'), ('no', 'Sin servicio de corte')],
        widget=forms.RadioSelect,
        initial='no'
    )


@login_required
@factory_owner_required
def add_remission_step2_view(request):
    factory_owner = FactoryOwner.objects.get(user=request.user)
    if request.method == "POST":
        form = CuttingServiceForm(request.POST)
        if form.is_valid():
            cutting_service = form.cleaned_data['cutting_service']
            if cutting_service == 'yes':
                # ... (código para manejar la opción de servicio de corte) ...
                pass
            elif cutting_service == 'no':
                # ... (código para manejar la opción sin servicio de corte) ...
                pass
            # ... (código adicional si es necesario) ...
            return redirect('some_view')  # reemplaza 'some_view' con la vista a la que deseas redirigir
        else:
            # El formulario no es válido, vuelve a renderizar la página con el formulario y los errores
            return render(request, 'add_remission2.html', {'form': form})
    else:
        form = CuttingServiceForm()
    return render(request, 'add_remission2.html', {'form': form})


@login_required   
def cutting_table_list_view(request):
    tables = CuttingTable.objects.all()
    return render(request, 'cutting_table_list.html', {'tables': tables})
    
@login_required
@factory_owner_required
def add_cutting_table_view(request):
    if request.method == 'POST':
        form = CuttingTableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cutting_table_list')
    else:
        form = CuttingTableForm()
    return render(request, 'add_cutting_table.html', {'form': form})

@login_required    
@factory_owner_required
def garment_part_create_view(request):
    if request.method == 'POST':
        form = GarmentPartForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('garment_part_list')
    else:
        form = GarmentPartForm()
    return render(request, 'garment_part_create.html', {'form': form})

@login_required    
@factory_owner_required
def garment_part_list_view(request, garment_type_id):
    garment_type = get_object_or_404(GarmentType, id=garment_type_id)
    garment_parts = GarmentPart.objects.filter(garment_type=garment_type)
    return render(request, 'garment_part_list.html', {'garment_parts': garment_parts, 'garment_type': garment_type})

@login_required   
@factory_owner_required 
def create_garment_type_with_parts(request):
    if request.method == "POST":
        form = GarmentTypeForm(request.POST)
        formset = GarmentPartFormSet(request.POST, prefix='garmentpart')
        
        if form.is_valid() and formset.is_valid():
            garment_type = form.save()
            formset.instance = garment_type
            formset.save()
            return redirect('garment_type_detail', garment_type_id=garment_type.id)
    else:
        form = GarmentTypeForm()
        formset = GarmentPartFormSet(prefix='garmentpart')
    
    return render(request, 'create_garment_type_with_parts.html', {'form': form, 'formset': formset})
    
    
#size views
#List a Size
@login_required
@factory_owner_required
def size_list(request):
    sizes = Size.objects.all()
    print(sizes) 
    return render(request, 'size_list.html', {'sizes': sizes})
    
    
#Create a Size
@login_required
@factory_owner_required
def size_create(request):
    if request.method == "POST":
        form = SizeForm(request.POST)
        if form.is_valid():
            size = form.save(commit=False)
            size.save()
            return redirect('size_detail', pk=size.pk)
    else:
        form = SizeForm()
    return render(request, 'size_edit.html', {'form': form})
    
    
#Detail a Size
@login_required
@factory_owner_required
def size_detail(request, pk):
    size = get_object_or_404(Size, pk=pk)
    return render(request, 'size_detail.html', {'size': size})
    
    
#Edit a Size
@login_required
@factory_owner_required
def size_edit(request, pk):
    size = get_object_or_404(Size, pk=pk)
    if request.method == "POST":
        form = SizeForm(request.POST, instance=size)
        if form.is_valid():
            size = form.save(commit=False)
            size.save()
            return redirect('size_detail', pk=size.pk)
    else:
        form = SizeForm(instance=size)
    return render(request, 'size_edit.html', {'form': form})
    
    
#Delete a Size
@login_required
@factory_owner_required
def size_delete(request, pk):
    size = get_object_or_404(Size, pk=pk)
    size.delete()
    return redirect('size_list')
        
# Lista de Operaciones  
@method_decorator(login_required, name='dispatch')
class OperationListView(ListView):
    model = Operation
    template_name = 'operation_list.html'

    def get_queryset(self):
        factory_owner = self.request.user.factory_owner
        return Operation.objects.filter(factory_owner=factory_owner)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        factory_owner = self.request.user.factory_owner  # Define factory_owner aquí
        operations = self.get_queryset()
        for operation in operations:
            operation.update_productivity_level()  # Cambio de nombre del método  # Esto llama a average_daily_volume y actualiza productivity
        context['operations'] = Operation.objects.filter(factory_owner=factory_owner)
        return context

def update_productivity_level_view(request, pk):
    operation = get_object_or_404(Operation, pk=pk)
    operation.update_productivity_level()
    return redirect('operation_list')  # reemplazar con el nombre de tu URL


# Detalle de una operación
@method_decorator(login_required, name='dispatch')
class OperationDetailView(DetailView):
    model = Operation
    template_name = 'operation_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        operation = self.get_object()
        context['complexity_display'] = operation.get_complexity_display()
        context['average_work_volume'] = operation.average_work_volume()
        return context

@method_decorator(login_required, name='dispatch')
class OperationCreateView(CreateView):
    model = Operation
    form_class = OperationForm
    template_name = 'operation_create.html'
    
    def form_valid(self, form):
        try:
            form.instance.factory_owner = self.request.user.factory_owner
            form.save()
            
            # Verificar si la solicitud es AJAX
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success', 'message': 'Operación creada con éxito.'})
            
            return super().form_valid(form)
        except Exception as e:
            if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)})
            return super().form_invalid(form)

    def form_invalid(self, form):
        # Verificar si la solicitud es AJAX
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': 'Error al crear la operación.'})
        
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('operation_list')

# Editar una operación existente
@method_decorator(login_required, name='dispatch')
class OperationUpdateView(UpdateView):
    model = Operation
    template_name = 'operation_edit.html'  # Reemplaza con la ruta a tu plantilla
    fields = ['name', 'value_COP']  # Reemplaza con los campos de tu modelo que quieres actualizar

    def get_success_url(self):
        return reverse_lazy('operation_list')

# Eliminar una operación
@method_decorator(login_required, name='dispatch')
class OperationDeleteView(DeleteView):
    model = Operation
    template_name = 'operation_delete.html'
    success_url = reverse_lazy('operation_list')
    
    
# FabricType
@method_decorator(csrf_exempt, name='dispatch')
class FabricTypeCreateView(CreateView):
    model = FabricType
    form_class = FabricTypeForm
    template_name = 'fabric_type_create.html'
    # fields = ['name', 'description']  # Elimina esta línea

    def form_valid(self, form):
        try:
            form.instance.factory_owner = self.request.user.factory_owner
        except FactoryOwner.DoesNotExist:
            return JsonResponse({'error': 'El usuario no tiene un FactoryOwner asociado'}, status=400)
        
        # Guarda el objeto y devuelve una respuesta JSON de éxito
        form.save()
        return JsonResponse({'message': 'Tipo de tela creado exitosamente'}, status=200)

    def form_invalid(self, form):
        # Devuelve una respuesta JSON con los errores del formulario
        print(form.errors)
        errors = form.errors.as_json()
        return JsonResponse({'error': errors}, status=400)


def fabric_type_list_view(request):
    fabric_types = FabricType.objects.all()
    return render(request, 'fabric_type_list.html', {'fabric_types': fabric_types})



class FabricTypeUpdateView(UpdateView):
    model = FabricType
    template_name = 'fabric_type_create.html'
    fields = ['name', 'description']  # añade aquí todos los campos que quieras incluir en el formulario
    def form_valid(self, form):
        try:
            form.instance.factory_owner = self.request.user.factory_owner
        except FactoryOwner.DoesNotExist:
        # manejar el caso donde el usuario no tiene una instancia de FactoryOwner asociada
        # podría ser redirigiendo a otra página o mostrando un mensaje de error
            return HttpResponseRedirect(reverse('error_page'))
        return super().form_valid(form)

class FabricTypeDeleteView(DeleteView):
    model = FabricType
    template_name = 'fabric_type_create.html'
    success_url = reverse_lazy('fabric_type_list')
    def form_valid(self, form):
        try:
            form.instance.factory_owner = self.request.user.factory_owner
        except FactoryOwner.DoesNotExist:
        # manejar el caso donde el usuario no tiene una instancia de FactoryOwner asociada
        # podría ser redirigiendo a otra página o mostrando un mensaje de error
            return HttpResponseRedirect(reverse('error_page'))
        return super().form_valid(form)
        
def add_distinctive_feature(request):
    if request.method == 'POST':
        form = DistinctiveFeatureForm(request.POST)
        if form.is_valid():
            distinctive_feature = form.save(commit=False)
            distinctive_feature.factory_owner = request.user  # Asumiendo que el usuario está autenticado
            distinctive_feature.save()
            return redirect('distinctive_feature_list')  # Reemplaza con el nombre de tu URL para listar las características
    else:
        form = DistinctiveFeatureForm()
    return render(request, 'add_distinctive_feature.html', {'form': form})       
