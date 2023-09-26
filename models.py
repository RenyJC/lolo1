from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone
from datetime import datetime
from django.core.mail import send_mail
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.db.models import Avg, DateField
from django.db.models.functions import Cast
from django.core.validators import MinValueValidator
from decimal import Decimal

# Clase base abstracta
class BaseUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    # Campos adicionales comunes
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    # Campos de confirmación de email
    confirmation_token = models.CharField(max_length=100, unique=True, null=True)
    email_confirmed = models.BooleanField(default=False)
    password_reset_token = models.CharField(max_length=100, unique=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        abstract = True

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)
    
    def send_password_reset_email(self):
        # Lógica para enviar correo de restablecimiento de contraseña
        subject = "Restablecimiento de contraseña"
        message = "Instrucciones para restablecer tu contraseña..."
        self.email_user(subject, message)
    
    def confirm_email(self):
        # Lógica para confirmar dirección de email
        subject = "Confirma tu dirección de correo electrónico"
        message = "Haz clic en el enlace a continuación para confirmar tu correo electrónico..."
        self.email_user(subject, message)

# Administrador dueño del SaaS
class AdminManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class Admin(BaseUser):
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    objects = AdminManager()

    def __str__(self):
        return self.email or ''  # Representación en cadena del modelo

    # Aquí puedes agregar otros campos específicos de Admin si lo requieres
    
IDENTIFICATION_TYPE_CHOICES = (
    ('CC', 'Cédula de Ciudadanía'),
    ('CE', 'Cédula de Extranjería'),
    # ... otras opciones ...
)

# Modelo para el plan, que determina cuántos FactoryAdmin y Operarios puede tener un FactoryOwner
class Plan(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True)  # Precios en formato XXXXX.XX

    # Limitaciones del plan
    max_admins = models.IntegerField(null=True)
    max_clients = models.IntegerField(null=True)
    max_garment_types = models.IntegerField(null=True)
    max_operators = models.IntegerField(null=True)
    max_remissions_per_month = models.IntegerField(null=True)

    # Características detalladas de cada plan
    basic_reports = models.BooleanField(default=False)
    advanced_reports = models.BooleanField(default=False)
    premium_reports = models.BooleanField(default=False)
    
    basic_simulations = models.BooleanField(default=False)
    advanced_simulations = models.BooleanField(default=False)
    
    basic_financial_management = models.BooleanField(default=False)
    advanced_financial_management = models.BooleanField(default=False)
    
    basic_payroll_management = models.BooleanField(default=False)
    advanced_payroll_management = models.BooleanField(default=False)
    complete_payroll_management = models.BooleanField(default=False)
    
    inventory_management = models.BooleanField(default=False)
    
    production_management = models.BooleanField(default=False)
    
    basic_remission_management = models.BooleanField(default=False)
    advanced_remission_management = models.BooleanField(default=False)
    premium_remission_management = models.BooleanField(default=False)
    
    automations = models.BooleanField(default=False)
    
    basic_support = models.BooleanField(default=False)
    integral_support = models.BooleanField(default=False)
    priority_support = models.BooleanField(default=False)
    
    has_ai_dashboard = models.BooleanField(default=False)
    
    real_time_graphics = models.BooleanField(default=False)
    
    expense_management = models.BooleanField(default=False)
    
    invoice_generation = models.BooleanField(default=False)
    
    account_control = models.BooleanField(default=False)
    
    detailed_payment_registry = models.BooleanField(default=False)

    # Frecuencia de Pago
    BILLING_CHOICES = [
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
    ]
    billing_frequency = models.CharField(max_length=10, choices=BILLING_CHOICES, default='monthly')

    # Descuentos o Promociones
    discount_percentage = models.PositiveIntegerField(default=0)
    promotional_price = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)

    # Plan Activo o Inactivo
    is_active = models.BooleanField(default=True)

    # Orden de Visualización
    display_order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name



    
# Modelo de FactoryOwner
class FactoryOwner(BaseUser):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='factory_owner', null=True, blank=True)
    identification_type = models.CharField(max_length=20, choices=IDENTIFICATION_TYPE_CHOICES, default='CC')
    identification_number = models.CharField(max_length=50, unique=True, null=True)
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    email = models.EmailField(max_length=254, unique=True, null=True, blank=True)


    def __str__(self):
        return self.email or ''  # Representación en cadena del modelo

    # Aquí puedes agregar otros campos o métodos específicos de FactoryOwner si lo requieres

# Modelo de FactoryAdmin (No estaba en tu diseño original pero lo mencionaste anteriormente)
class FactoryAdmin(BaseUser):
    factory_owner = models.ForeignKey(FactoryOwner, on_delete=models.CASCADE, related_name='factory_admins')
    
    def __str__(self):
        return self.email or ''  # Representación en cadena del modelo
        
        
class OperatorManager(BaseUserManager):
    def create_user(self, email, factory_owner, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, factory_owner=factory_owner, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

#Este modelo representa a los operadores que trabajan en la fábrica y 
#están asociados con un propietario de fábrica específico (FactoryOwner)
class Operator(models.Model):
    factory_owner = models.ForeignKey('FactoryOwner', on_delete=models.CASCADE, related_name='operators')
    
    # Datos específicos del Operator
    name = models.CharField(max_length=255, verbose_name='Nombre')
    email = models.EmailField(max_length=255, null=True, blank=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    id_number = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)  # Indica si el operario está activo
    volume_per_day = models.IntegerField(default=0)
    best_operation = models.ForeignKey(
        'Operation', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='best_operators'
    )

    def __str__(self):
        return self.name

    def get_logs(self):
        """ 
        Get all logs associated with this operator.
        """
        return self.operatorlog_set.all()

class OperatorLog(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE)
    action = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    


        
# Client Model, Este modelo representa a los clientes que hacen negocios con la fábrica y 
#están asociados con un propietario de fábrica (FactoryOwner) específico.
class Client(models.Model):
    # Basic personal information
    name = models.CharField(max_length=255)
    
    # Unique Tax ID (NIT)
    NIT = models.CharField(max_length=255, unique=False)
    
    # Email for communication and invoicing
    email = models.EmailField(max_length=255)
    
    # Additional personal information
    address = models.CharField(max_length=500, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    
    # The factory owner this client is associated with
    factory_owners = models.ManyToManyField(User, related_name='clients')

    def __str__(self):
        return self.name
        
class Period(models.Model):
    start_date = models.DateField()  # Start date of the payment period
    end_date = models.DateField()  # End date of the payment period
    factory_owner = models.ForeignKey(
        FactoryOwner, on_delete=models.CASCADE, related_name='periods'
    )  # Relation to the Factory Owner who set this period
    
    def __str__(self):
        return f"{self.start_date} to {self.end_date}"

# Operation Model
class Operation(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Name of the operation (e.g., Cutting, Sewing)
    value_COP = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]  # Esto asegura que solo se puedan ingresar valores positivos
    )    # Cost of the operation in COP
    factory_owner = models.ForeignKey(
        FactoryOwner, on_delete=models.CASCADE, related_name='operations'
    )  # The Factory Owner who sets the value of this operation
    
    PRODUCTIVITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]
    productivity_level = models.CharField(max_length=10, choices=PRODUCTIVITY_CHOICES, default='low')
    
    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('operation_detail', args=[str(self.id)])
    
    @property
    def average_daily_volume(self):
        """Calcula el volumen promedio diario de operaciones reportadas para esta operación."""
        daily_volumes = OperatorReport.objects.filter(operation=self).values('period__start_date').annotate(
            daily_volume=models.Sum('total_operations')
        ).aggregate(
            avg_volume=models.Avg('daily_volume')
        )['avg_volume']
    
        return daily_volumes or 0

    def update_productivity_level(self):
        """Determina el nivel de productividad basado en el volumen promedio diario."""

        # Obtenga todas las combinaciones únicas de operario, cliente y tipo de prenda para esta operación
        combinations = OperatorReport.objects.filter(operation=self).values_list(
            'operator_id', 'remission__client_id', 'remission__garment_type_id'
        ).distinct()

            # Iterar sobre todas las combinaciones y calcular el volumen promedio diario para cada una
        for operator_id, client_id, garment_type_id in combinations:

            # Calcular el volumen promedio diario para esta combinación
            avg_volume = OperatorReport.objects.filter(
                operation=self,
                operator_id=operator_id,
                remission__client_id=client_id,
                remission__garment_type_id=garment_type_id
            ).values('date').annotate(
                daily_volume=models.Sum('total_operations')
            ).aggregate(
                avg_volume=models.Avg('daily_volume')
            )['avg_volume'] or 0

            # Actualizar la lógica para determinar la productividad
            if avg_volume > 2000:
                productivity_level = 'high'
            elif avg_volume > 1000:
                productivity_level = 'medium'
            else:
                productivity_level = 'low'
        
            self.productivity_level = productivity_level
            self.save()


            # Aquí, actualiza el nivel de productividad en tu base de datos
            # (Necesitarás determinar cómo quieres almacenar esta información)
            # Por ejemplo, podrías crear un nuevo modelo para almacenar el nivel de productividad para cada combinación


class OperationProductivity(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, blank=True)
    garment_type = models.ForeignKey('GarmentType', on_delete=models.CASCADE, null=True, blank=True)
    
    PRODUCTIVITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
    ]
    productivity_level = models.CharField(max_length=10, choices=PRODUCTIVITY_CHOICES, default='low')

    class Meta:
        unique_together = ('operation', 'operator', 'client', 'garment_type')


# OperationGroup Model
class OperationGroup(models.Model):
    """
    This model serves as a bridge between Operations and GarmentTypes.
    It helps to specify which operations are required to produce a specific type of garment.
    """
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='operation_groups')
    garment_type = models.ForeignKey('GarmentType', on_delete=models.CASCADE, related_name='operation_groups')
    sequence_number = models.IntegerField()  # To specify the order of operations
    
    class Meta:
        unique_together = ('operation', 'garment_type', 'sequence_number')


class FabricType(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Nombre del tipo de tela
    description = models.TextField(null=True, blank=True, help_text="Incluya detalles como las características, usos comunes, etc. de este tipo de tela.")  # Descripción opcional
    gramaje = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Gramaje de la Tela", null=True, blank=True)
    factory_owner = models.ForeignKey(
    FactoryOwner, 
    on_delete=models.SET_NULL,  # Esto establece el valor a NULL en caso de que el `FactoryOwner` relacionado sea eliminado
    related_name='fabric_types', 
    null=True,  # Esto permite valores NULL a nivel de base de datos
    blank=True,  # Esto permite que el campo esté vacío a nivel de formulario
)

    def __str__(self):
        return self.name

# Modelo para las caracteristicas de la prenda
class DistinctiveFeature(models.Model):
    name = models.CharField(max_length=100, unique=True)  # Nombre de la característica distintiva
    factory_owner = models.ForeignKey(
        FactoryOwner, on_delete=models.CASCADE, related_name='distinctive_features'
    )  # Relación con el propietario de la fábrica que creó esta característica

    def __str__(self):
        return self.name

def get_default_client_id():
    # Intenta obtener el primer cliente de la base de datos
    try:
        return Client.objects.first().id
    except AttributeError:
        # Si no hay ningún cliente en la base de datos, retorna None
        return None
      
# GarmentType Model
class GarmentType(models.Model):
    name = models.CharField(max_length=255, unique=True)  # Name of the garment type
    description = models.TextField(null=True, blank=True)  # Optional description of the garment type
    product_code = models.CharField(max_length=255, unique=True, help_text="Cree un código único para este tipo de prenda.")  # Unique product code for the garment type
    base_price_COP = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))]
    )  # Base price per unit in COP
    distinctive_features = models.ManyToManyField(
        DistinctiveFeature, 
        related_name='garment_types',
        blank=True,
    )  # Relación de muchos a muchos con DistinctiveFeature
    fabric_type = models.ForeignKey(
        FabricType, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='garment_types',
        help_text="Seleccione el tipo de tela principal utilizado para este tipo de prenda."
    )
    factory_owner = models.ForeignKey(
        FactoryOwner, on_delete=models.CASCADE, related_name='garment_types'
    )  # Relation to the Factory Owner who owns this garment type
    client = models.ForeignKey(Client, on_delete=models.CASCADE, default=get_default_client_id)  # Relation to the client who requests this garment type
    operations = models.ManyToManyField(
        Operation, 
        related_name='garment_types',
        blank=True,
    )

    def __str__(self):
        return self.name
        

# Modelo para el color de laprenda
class ColorFeature(models.Model):
    name = models.CharField(max_length=50)  # Nombre del color
    garment_type = models.ForeignKey(
        GarmentType, on_delete=models.CASCADE, related_name='color_features'        
    )  # Relación con el tipo de color    factory_owner = models.ForeignKey
    factory_owner = models.ForeignKey(
        FactoryOwner, on_delete=models.CASCADE, related_name='color_features'
    )  # Relación con el propietario de la fábrica que creó esta característica
    

    def __str__(self):
        return self.name        


# Modelo para las partes de una prenda
class GarmentPart(models.Model):
    name = models.CharField(max_length=255)  # Nombre de la parte (ej. "Manga", "Cuello")
    area_m2 = models.DecimalField(max_digits=10, decimal_places=2)  # Área en metros cuadrados para esta parte
    garment_type = models.ForeignKey(
        'GarmentType', on_delete=models.CASCADE, related_name='garment_parts'
    )  # Relación con el tipo de prenda a la que pertenece esta parte

    def __str__(self):
        return f"{self.name} for {self.garment_type.name}"


# Size Model
class Size(models.Model):
    name = models.CharField(max_length=255)  # Name of the size (e.g., S, M, L, XL)
    factory_owner = models.ForeignKey(
        FactoryOwner, on_delete=models.CASCADE, related_name='sizes'
    )  # Relation to the Factory Owner who owns this size
    garment_type = models.ForeignKey(
        GarmentType, on_delete=models.SET_NULL, null=True, blank=True, related_name='sizes'
    )  # Relation to the garment type that this size belongs to
    
    def __str__(self):
        return self.name

class Batch(models.Model):
    number = models.CharField(max_length=100)  # Establece un límite adecuado para el número de caracteres
    description = models.TextField(null=True, blank=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='batches')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.number

      

# RemissionSizeQuantity Model
class RemissionSizeQuantity(models.Model):
    remission = models.ForeignKey('Remission', on_delete=models.CASCADE, related_name='size_quantities')
    size = models.ForeignKey('Size', on_delete=models.CASCADE, related_name='size_quantities')
    color_feature = models.ForeignKey(
        ColorFeature, 
        on_delete=models.CASCADE, 
        null=True,
    )
    quantity = models.IntegerField()

    class Meta:
        unique_together = ('remission', 'size')

    def __str__(self):
        return f"{self.remission.number} - {self.size.name} - {self.quantity}"

# Remission Model
class Remission(models.Model):
    number = models.IntegerField(unique=True)  # Unique Remission Number
    garment_type = models.ForeignKey('GarmentType', on_delete=models.CASCADE, related_name='remissions')
    client = models.ForeignKey('Client', on_delete=models.CASCADE, related_name='remissions')
    unit_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Unitario', default=0.00)
    total_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Valor Total', default=0.00)
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, blank=True, null=True, related_name='remissions')
    color_feature = models.ForeignKey(
        ColorFeature, 
        on_delete=models.CASCADE, 
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    factory_owner = models.ForeignKey(
    FactoryOwner, on_delete=models.CASCADE, related_name='remissions', null=True, blank=True
    )  # Relation to the Factory Owner who created this remission
    
    def total_quantity(self):
        return sum(sq.quantity for sq in self.size_quantities.all())

    def total_value_COP(self):
        total_quantity = sum(sq.quantity for sq in self.size_quantities.all())
        return total_quantity * self.unit_value

    def save(self, *args, **kwargs):
        super(Remission, self).save(*args, **kwargs)

        
    def __str__(self):
        return f"Remission {self.number}"

        

class Arrangement(models.Model):
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='arrangements')
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='arrangements')
    remission = models.ForeignKey(Remission, on_delete=models.CASCADE, related_name='arrangements')  # Relación con la remisión
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='arrangements')  # Relación con el cliente
    garment_count = models.IntegerField(default=0)  # Cantidad de prendas arregladas
    details = models.TextField(null=True, blank=True)  # Detalles del arreglo
    created_at = models.DateTimeField(auto_now_add=True)  # Fecha y hora del arreglo

    def __str__(self):
        return f"Arreglo para el cliente {self.client.name} en remisión {self.remission.number}, Operación: {self.operation.name}"

class DailyWorkVolume(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='daily_work_volumes')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='daily_work_volumes')  # Relación con el cliente
    remission = models.ForeignKey(Remission, on_delete=models.CASCADE, related_name='daily_work_volumes')  # Relación con la remisión
    date = models.DateField()
    volume = models.IntegerField(default=0)  # Volumen de prendas manejadas por día

    def __str__(self):
        return f"Volumen de trabajo para {self.operator.name} - Cliente: {self.client.name} - Remisión: {self.remission.number} en {self.date}"



        
# RemissionDelivery Model
class RemissionDelivery(models.Model):
    # Este campo es una llave foránea que establece una relación con el modelo Remission.
    # Esto permite saber a qué remisión pertenece esta entrega.
    remission = models.ForeignKey(Remission, on_delete=models.CASCADE, related_name='remission_deliveries')
    
    # Este es un campo de relación de muchos a muchos con RemissionSizeQuantity.
    # Almacena la cantidad de prendas entregadas para cada talla.
    size_quantities = models.ManyToManyField(RemissionSizeQuantity, related_name='remission_deliveries')
    
    # Este campo almacena la cantidad total de prendas entregadas en esta remisión.
    total_quantity = models.IntegerField()
    
    # Este campo almacena el valor total en COP de las prendas entregadas en esta remisión.
    total_value_COP = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Este campo es una llave foránea que establece una relación con el modelo Client.
    # Esto permite saber a qué cliente se le hizo esta entrega.
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='remission_deliveries')
    
    batch = models.ForeignKey(Batch, on_delete=models.SET_NULL, blank=True, null=True, related_name='remission_deliveries')
    
    # Este campo es una llave foránea que establece una relación con e  l modelo FactoryOwner.
    # Esto permite saber qué FactoryOwner hizo esta entrega.
    factory_owner = models.ForeignKey(FactoryOwner, on_delete=models.CASCADE, related_name='remission_deliveries')

    # Método para calcular la cantidad total de prendas entregadas.
    def calculate_total_quantity(self):
        self.total_quantity = sum([sq.quantity for sq in self.size_quantities.all()])

    # Método para calcular el valor total en COP de las prendas entregadas.
    def calculate_total_value(self, base_price):
        self.total_value_COP = self.total_quantity * base_price
        
class Invoice(models.Model):
    remission_delivery = models.ForeignKey(RemissionDelivery, on_delete=models.CASCADE, related_name='invoices')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='invoices')
    factory_owner = models.ForeignKey(FactoryOwner, on_delete=models.CASCADE, related_name='invoices')

    # Puedes almacenar el PDF en un campo FileField si lo deseas
    pdf = models.FileField(upload_to='invoices/', null=True, blank=True, storage=FileSystemStorage(location='/media/'))

    def generate_pdf(self):
        # Aquí, podrías generar un PDF personalizado con la información de la factura.
        # Utilizarías los campos de 'self.factory_owner' para obtener detalles como el logo y el nombre de la empresa.
        pdf = generate_invoice_pdf(self)
        
        # Guardar el PDF en el campo FileField
        self.pdf.save('invoice_{}.pdf'.format(self.id), pdf)
        self.save()

    def send_invoice(self, method='email'):
        # Podrías generar el PDF aquí o hacerlo previamente y almacenarlo
        self.generate_pdf()

        if method == 'email':
            # Aquí, enviarías el PDF por correo electrónico
            send_invoice_email(self)
        elif method == 'whatsapp':
            # Aquí, enviarías el PDF por WhatsApp
            send_invoice_whatsapp(self)

    def __str__(self):
        return f"Invoice {self.id} for Remission Delivery {self.remission_delivery.id}"

# Aquí, debes implementar tus propias funciones para generar el PDF, enviar correos electrónicos y enviar mensajes de WhatsApp.
# def generate_invoice_pdf(invoice):
#     ...

# def send_invoice_email(invoice):
#     ...

# def send_invoice_whatsapp(invoice):
#     ...
class WastedGarment(models.Model):
    # ForeignKey to RemissionDelivery to identify which remission delivery this wasted garment belongs to
    remission_delivery = models.ForeignKey(RemissionDelivery, on_delete=models.CASCADE, related_name='wasted_garments')
    
    # ForeignKey to Operator to identify the operator responsible for this wasted garment
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='wasted_garments')
    
    # The number of garments wasted
    quantity = models.IntegerField()
    
    # The total value in COP of the wasted garments
    value_COP = models.DecimalField(max_digits=10, decimal_places=2)
    
    # The retail value in COP of the wasted garments
    retail_value_COP = models.DecimalField(max_digits=10, decimal_places=2)  # Nuevo campo
    
    # Optional field to describe the reason for the waste
    reason = models.TextField(null=True, blank=True)
    
    # Date when the garment was wasted
    date = models.DateTimeField(auto_now_add=True)

    # Este método podría ser llamado para actualizar el pago total del operario
    def update_operator_payment(self):
        # Aquí iría la lógica para actualizar el pago del operario en base al valor desperdiciado
        pass

    def __str__(self):
        return f"Prendas desperdiciadas en la entrega de remisión {self.remission_delivery.id}"

# Modelo para relacionar Operator con múltiples Operation
class OperatorAdditionalOperation(models.Model):
    operator = models.ForeignKey(
        Operator, 
        on_delete=models.CASCADE, 
        related_name='additional_operations'
    )  # Relation to the Operator
    operation = models.ForeignKey(
        Operation, 
        on_delete=models.CASCADE, 
        related_name='additional_operators'
    )  # Relation to the Operation

    def __str__(self):
        return f"{self.operator.name} - {self.operation.name}"

class OperatorReport(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='operator_reports')
    period = models.ForeignKey(Period, on_delete=models.CASCADE, related_name='operator_reports')
    remission = models.ForeignKey(Remission, on_delete=models.CASCADE, related_name='operator_reports')
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='operator_reports')  # New field
    garment_type = models.ForeignKey(GarmentType, on_delete=models.CASCADE, related_name='operator_reports')  # New field
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE, related_name='operator_reports')
    quantity_by_size = models.JSONField()  # Storing the quantity of operations performed for each size as JSON
    total_operations = models.IntegerField()  # Total number of operations performed
    total_value_COP = models.DecimalField(max_digits=10, decimal_places=2)  # Total value in COP
    date = models.DateField(default=timezone.now)  # Nuevo campo para almacenar la fecha de creación del reporte

    def clean(self):
        # Busca la entrega de remisión correspondiente a la remisión especificada
        remission_delivery = RemissionDelivery.objects.filter(remission=self.remission).first()

        if remission_delivery:
            # Verifica si el total de operaciones excede la cantidad total de prendas entregadas
            if self.total_operations > remission_delivery.total_quantity:   
                raise ValidationError('The total number of reported operations cannot exceed the total number of delivered garments.')
        else:
            # Si no hay una entrega de remisión correspondiente, genera un error.
            raise ValidationError('There is no remission delivery associated with the given remission.')

# Payment Model
class Payment(models.Model):
    # ForeignKey to Operator to identify the operator who is being paid
    operator = models.ForeignKey(
        'Operator', 
        on_delete=models.CASCADE, 
        related_name='payments'
    )
    
    # The total value in COP to be paid to the operator
    total_value_COP = models.DecimalField(
        max_digits=10, 
        decimal_places=2
    )
    
    # Optional field to specify the date the payment was made
    payment_date = models.DateField(
        null=True, 
        blank=True
    )
    
    # ForeignKey to Period to specify the payment period
    period = models.ForeignKey(
        'Period', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='payments'
    )
    
    # ... (otros métodos y propiedades)

    def __str__(self):
        return f"Payment to {self.operator.name} for {self.total_value_COP} COP"

class Advance(models.Model):
    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='advances')
    amount_COP = models.DecimalField(_("Advance Amount (COP)"), max_digits=10, decimal_places=2)
    request_date = models.DateField(_("Request Date"), auto_now_add=True)
    description = models.TextField(_("Description"), null=True, blank=True)

    class Meta:
        verbose_name = _("Advance")
        verbose_name_plural = _("Advances")

    def __str__(self):
        return f"{self.operator.name} - {self.amount_COP} COP ({self.request_date})"

class Bonus(models.Model):
    REASONS = [
        ('holiday', _('Holiday Worked')),
        ('outstanding', _('Outstanding Performance')),
        ('help', _('Helped with Heavy Lifting')),
        ('other', _('Other'))
    ]

    operator = models.ForeignKey(Operator, on_delete=models.CASCADE, related_name='bonuses')
    amount_COP = models.DecimalField(_("Bonus Amount (COP)"), max_digits=10, decimal_places=2)
    grant_date = models.DateField(_("Grant Date"), auto_now_add=True)
    reason = models.CharField(_("Reason"), max_length=50, choices=REASONS)

    class Meta:
        verbose_name = _("Bonus")
        verbose_name_plural = _("Bonuses")

    def __str__(self):
        return f"{self.operator.name} - {self.amount_COP} COP ({self.reason})"


def calculate_salary(period, operator):
    # Obtenemos el rango de fechas del objeto periodo
    start_date = period.start_date
    end_date = period.end_date

    # Calcula el total de pagos por las prendas producidas en el rango de fechas.
    total_payments = Payment.objects.filter(operator=operator, date__range=[start_date, end_date]).aggregate(total=models.Sum('total_value_COP'))['total'] or 0

    # Calcula el total de avances solicitados en el rango de fechas.
    total_advances = Advance.objects.filter(operator=operator, request_date__range=[start_date, end_date]).aggregate(total=models.Sum('amount_COP'))['total'] or 0

    # Calcula el total de prendas desperdiciadas (y su valor) en el rango de fechas.
    total_wastes = WastedGarment.objects.filter(operator=operator, date__range=[start_date, end_date]).aggregate(total=models.Sum('value_COP'))['total'] or 0

    # Calcula el total de bonos otorgados en el rango de fechas.
    total_bonuses = Bonus.objects.filter(operator=operator, grant_date__range=[start_date, end_date]).aggregate(total=models.Sum('amount_COP'))['total'] or 0

    # Calcula el salario neto.
    salary = total_payments - total_advances - total_wastes + total_bonuses

    # Opcional: crear un registro Payment con el salario calculado
    Payment.objects.create(operator=operator, total_value_COP=salary, date=end_date)

    return salary


# ExpenseType Model
class ExpenseType(models.Model):
    name = models.CharField(max_length=255)  # Nombre del tipo de gasto
    factory_owner = models.ForeignKey(
        FactoryOwner,
        on_delete=models.CASCADE,
        related_name='expense_types'  # nombre único para esta relación
    )
        
    def __str__(self):
        return self.name

# Expense Model
class Expense(models.Model):
    type = models.ForeignKey(ExpenseType, on_delete=models.CASCADE, related_name='expenses')  # Tipo de gasto
    value_COP = models.DecimalField(max_digits=10, decimal_places=2)  # Valor del gasto en COP
    date_incurred = models.DateField()  # Fecha en que se incurrió en el gasto
    description = models.TextField(null=True, blank=True)  # Descripción opcional del gasto
    factory_owner = models.ForeignKey(
        FactoryOwner, on_delete=models.CASCADE, related_name='expenses'
    )  # Relación con el propietario de la fábrica
    client = models.ForeignKey(
        Client, on_delete=models.CASCADE, related_name='client_expenses'
    )  # Relación con el cliente para gastos específicos
    
    # (Opcional) Campo para almacenar recibos o documentos relacionados
    receipt_document = models.FileField(upload_to='expenses/', null=True, blank=True)

    def __str__(self):
        return f"{self.type.name} - {self.value_COP} COP - {self.date_incurred}"

#Cuentas por cobrar
class AccountReceivable(models.Model):
    remission_delivery = models.OneToOneField(RemissionDelivery, on_delete=models.CASCADE, related_name='account_receivable')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    date_paid = models.DateField(null=True, blank=True)

#Cuentas por pagar
class AccountPayable(models.Model):
    expense = models.OneToOneField(Expense, on_delete=models.CASCADE, related_name='account_payable')
    amount_due = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    is_paid = models.BooleanField(default=False)
    date_paid = models.DateField(null=True, blank=True)

# CostSimulation Model

class CostSimulation(models.Model):
    start_date = models.DateField(null=True, blank=True)  # Fecha de inicio para el cálculo
    end_date = models.DateField(null=True, blank=True)    # Fecha de fin para el cálculo
    remission_number = models.ForeignKey(Remission, on_delete=models.CASCADE, null=True, blank=True)  # Referencia al modelo Remission
    total_revenues_COP = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Ingresos totales
    total_expenses_COP = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Gastos totales
    net_profit_COP = models.DecimalField(max_digits=12, decimal_places=2, default=0)      # Beneficio neto

    def calculate_total_revenues(self):
        if self.remission_number:
            deliveries = RemissionDelivery.objects.filter(remission=self.remission_number, has_been_charged=True)
        else:
            deliveries = RemissionDelivery.objects.filter(date__range=[self.start_date, self.end_date], has_been_charged=True)
        self.total_revenues_COP = sum(delivery.value_COP for delivery in deliveries)

    def calculate_total_expenses(self):
        if self.remission_number:
            payments = Payment.objects.filter(remission_delivery__remission=self.remission_number)
            expenses = Expense.objects.filter(remission_delivery__remission=self.remission_number)
        else:
            payments = Payment.objects.filter(date__range=[self.start_date, self.end_date])
            expenses = Expense.objects.filter(date__range=[self.start_date, self.end_date])
        self.total_expenses_COP = sum(payment.value_COP for payment in payments) + sum(expense.value_COP for expense in expenses)

    def calculate_net_profit(self):
        self.net_profit_COP = self.total_revenues_COP - self.total_expenses_COP

    def save(self, *args, **kwargs):
        self.calculate_total_revenues()
        self.calculate_total_expenses()
        self.calculate_net_profit()
        super().save(*args, **kwargs)


class ProfitSimulation(models.Model):
    # Identificadores únicos para la simulación
    garment_type = models.ForeignKey(GarmentType, on_delete=models.CASCADE, related_name='profit_simulations')
    factory_owner = models.ForeignKey(FactoryOwner, on_delete=models.CASCADE, related_name='profit_simulations')
    
    # Cantidad de prendas a producir
    quantity = models.IntegerField(verbose_name="Cantidad de Prendas")
    
    # Costos estimados (Estos podrían ser ingresados manualmente o calculados automáticamente)
    material_cost_COP = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo de Material en COP")
    labor_cost_COP = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo de Mano de Obra en COP")
    overhead_cost_COP = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Costo General en COP")
    
    # Precio de venta por prenda (esto podría ser extraído del modelo GarmentType)
    selling_price_COP = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio de Venta en COP")
    
    # Campos calculados automáticamente
    total_cost_COP = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="Costo Total en COP")
    projected_profit_COP = models.DecimalField(max_digits=10, decimal_places=2, editable=False, verbose_name="Ganancia Proyectada en COP")
    is_profitable = models.BooleanField(default=False, editable=False, verbose_name="¿Es Rentable?")
    
    # Comentarios adicionales o notas
    comments = models.TextField(null=True, blank=True, verbose_name="Comentarios o Notas")
    
    def save(self, *args, **kwargs):
        # Calculo del costo total
        self.total_cost_COP = self.material_cost_COP + self.labor_cost_COP + self.overhead_cost_COP
        
        # Calculo de la ganancia proyectada
        self.projected_profit_COP = (self.selling_price_COP - self.total_cost_COP) * self.quantity
        
        # Determinar si la simulación es rentable
        self.is_profitable = self.projected_profit_COP > 0

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Simulación de Rentabilidad para {self.garment_type.name}"

    def clean(self):
        """
        Método para realizar validaciones adicionales.
        """
        if self.quantity <= 0:
            raise ValidationError("La cantidad debe ser mayor que cero.")
        
        if self.material_cost_COP < 0 or self.labor_cost_COP < 0 or self.overhead_cost_COP < 0:
            raise ValidationError("Los costos no pueden ser negativos.")

# Modelo para la mesa de corte
class CuttingTable(models.Model):
    length_m = models.DecimalField(max_digits=5, decimal_places=2)  # Longitud de la mesa de corte en metros
    width_m = models.DecimalField(max_digits=5, decimal_places=2)  # Ancho de la mesa de corte en metros
    factory_owner = models.ForeignKey(
        'FactoryOwner', on_delete=models.CASCADE, related_name='cutting_tables'
    )  # Relación con el FactoryOwner que posee esta mesa de corte

    def total_area_m2(self):
        """Calcula el área total de la mesa en metros cuadrados."""
        return self.length_m * self.width_m

    def __str__(self):
        return f"Cutting Table {self.id} - {self.total_area_m2()} m^2"



        
# Modelo para el patrón de corte
class CuttingPattern(models.Model):
    name = models.CharField(max_length=255)  # Nombre del patrón de corte
    garment_type = models.ForeignKey(
        'GarmentType', on_delete=models.CASCADE, related_name='cutting_patterns'
    )  # Relación con el tipo de prenda para el que es este patrón
    efficiency = models.DecimalField(max_digits=5, decimal_places=2)  # Eficiencia en términos de utilización de tela

    def __str__(self):
        return f"{self.name} for {self.garment_type.name}"


class CuttingService(models.Model):
    remission = models.OneToOneField(
        'Remission', on_delete=models.CASCADE, related_name='cutting_service'
    )  # Relación uno a uno con la remisión asociada
    cutting_table = models.ForeignKey(
        'CuttingTable', on_delete=models.SET_NULL, null=True, blank=True, related_name='cutting_services'
    )  # Relación con la mesa de corte utilizada
    cutting_pattern = models.ForeignKey(
        'CuttingPattern', on_delete=models.SET_NULL, null=True, blank=True, related_name='cutting_services'
    )  # Relación con el patrón de corte utilizado
    client = models.ForeignKey(
        'Client', on_delete=models.SET_NULL, null=True, blank=True, related_name='cutting_services'
    )  # Relación con el cliente que solicitó el servicio de corte
    date_requested = models.DateTimeField(auto_now_add=True)  # Fecha y hora en que se solicitó el servicio de corte
    date_completed = models.DateTimeField(null=True, blank=True)  # Fecha y hora en que se completó el servicio de corte
    factory_owner = models.ForeignKey(
        FactoryOwner,
        on_delete=models.CASCADE,
        related_name='cutting_services'  # nombre único para esta relación
    )

    fabric_supplier = models.CharField(max_length=255)  # Proveedor de la tela
    cutting_number = models.CharField(max_length=255)  # Número de corte
    garment_type = models.ForeignKey(
        'GarmentType', on_delete=models.SET_NULL, null=True, blank=True, related_name='cutting_services'
    )  # Tipo de Prenda
    # Para la cantidad de prendas que salen por tallas, puedes necesitar un modelo relacionado o un campo JSON
    blocks_per_size = models.JSONField(null=True, blank=True)  # Bloques por talla
    bias_weight_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Peso del Sesgo en Kg
    color = models.ForeignKey(
        'ColorFeature', on_delete=models.SET_NULL, null=True, blank=True, related_name='cutting_services'
    )  # Color
    weight_kg = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Peso en Kg
    fabric_width_m = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Ancho de la tela en metros
    layer_count = models.PositiveIntegerField(null=True, blank=True)  # Cantidad de capas
    spread_length_m = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)  # Largo del Tendido en metros
    garment_count = models.PositiveIntegerField(null=True, blank=True)  # Cantidad de prendas
    # Promedio Final - se puede calcular con una función dentro del modelo
    cutter_name = models.CharField(max_length=255, null=True, blank=True)  # Nombre del cortador

    def __str__(self):
        return f"Cutting Service for Remission {self.remission.number}"

    def is_completed(self):
        """Determina si el servicio de corte ha sido completado."""
        return self.date_completed is not None

    def calculate_final_average(self):
        # Aquí puedes agregar la lógica para calcular el Promedio Final
        pass
        
    
