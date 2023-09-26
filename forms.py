from django import forms
from django.forms import modelformset_factory
from django.contrib.auth.models import User
from .models import FactoryOwner, Operator, Client, Remission
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from .models import CostSimulation
from .models import ProfitSimulation
from .models import CuttingTable
from .models import GarmentPart, GarmentType
from django.forms import inlineformset_factory
from .models import Size
from .models import Operation, OperationGroup
from django.views.generic import ListView, DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.db.models import Q
from .models import FabricType
from django.forms import modelformset_factory
from .models import RemissionSizeQuantity, DistinctiveFeature, ColorFeature
from .models import Batch
from .models import DistinctiveFeature
from .models import CuttingService
from bootstrap4.widgets import RadioSelectButtonGroup




class CustomUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label=_('Contraseña'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Confirmar contraseña'), widget=forms.PasswordInput)
    email = forms.EmailField(required=True, help_text=_("Requerido, ingrese un correo electrónico válido."))

    class Meta:
        model = User
        fields = ['username', 'email']
        labels = {
            'username': _('Nombre de usuario'),
        }
        help_texts = {
            'username': _('Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ solamente.'),
        }

    def clean_password2(self):
        # Verificar que las dos contraseñas coincidan
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(_("Las contraseñas no coinciden"))
        return password2

    # (el resto del código sigue igual)


    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class OperationForm(forms.ModelForm):
    class Meta:
        model = Operation
        fields = ['name', 'value_COP']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'value_COP': forms.NumberInput(attrs={'class': 'form-control'}),
        }

        

class OperationGroupForm(forms.ModelForm):
    class Meta:
        model = OperationGroup
        fields = ['operation', 'garment_type', 'sequence_number']
        

class OperatorForm(forms.ModelForm):    
    best_operation = forms.ModelChoiceField(
        queryset=Operation.objects.none(),  # Inicialmente establecido a none
        required=False, 
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Mejor operación"
    )

    def __init__(self, *args, **kwargs):
        factory_owner = kwargs.pop('factory_owner', None)
        super().__init__(*args, **kwargs)
        
        # Establece las etiquetas de los campos
        self.fields['name'].label = 'Nombre'
        self.fields['id_number'].label = 'Identificación'
        self.fields['email'].label = 'Email'
        self.fields['phone'].label = 'Telefono'
        self.fields['address'].label = 'Dirección'       
        self.fields['is_active'].label = 'Activo' 
        self.fields['is_active'].widget = forms.CheckboxInput(attrs={'class': 'form-check-input'})
        
        # Filtra las operaciones disponibles según el factory_owner
        if factory_owner:
            self.fields['best_operation'].queryset = Operation.objects.filter(factory_owner=factory_owner)
        else:
            self.fields['best_operation'].queryset = Operation.objects.none()
        
    class Meta:
        model = Operator  # Asegúrate de especificar el modelo correcto aquí
        fields = ['name', 'id_number', 'best_operation', 'email', 'phone', 'address', 'is_active']  # Reemplaza con los nombres reales de tus campos
        
        
class ClientForm(forms.ModelForm):
    email = forms.EmailField(
        max_length=255, 
        required=True, 
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Client
        fields = ['name', 'NIT', 'email', 'address', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'NIT': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
        }

class RemissionSizeQuantityForm(forms.ModelForm):
    DELETE = forms.BooleanField(
        required=False,
        initial=False,  # Aquí faltaba una coma
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='Marcar para eliminar'
    )
    color_feature = forms.ModelChoiceField(queryset=ColorFeature.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    
    class Meta:
        model = RemissionSizeQuantity
        fields = ['size', 'quantity', 'color_feature']
        widgets = {
            'size': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class BatchForm(forms.ModelForm):
    class Meta:
        model = Batch
        fields = ['number', 'description']
        widgets = {
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        
class RemissionForm(forms.ModelForm):
    class Meta:
        model = Remission
        fields = [
            'number', 
            'garment_type', 
            'client', 
            'unit_value', 
            'total_value',
            'batch',  # Añade el campo de tanda aquí
        ]
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'garment_type': forms.Select(attrs={'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'unit_value': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'total_value': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'batch': forms.Select(attrs={'class': 'form-control'}),# Define un widget para el campo de tanda
        }


RemissionSizeQuantityFormSet = forms.modelformset_factory(
    RemissionSizeQuantity, 
    fields=('size', 'quantity', 'color_feature'), 
    extra=1, 
    can_delete=True,
    widgets = {
        'size': forms.Select(attrs={'class': 'form-control'}),
        'quantity': forms.NumberInput(attrs={'class': 'form-control'}),
        'color_feature': forms.Select(attrs={'class': 'form-control'}),
    }
)


class ColorFeatureForm(forms.ModelForm):
    class Meta:
        model = ColorFeature
        fields = ['name', 'factory_owner', 'garment_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'factory_owner': forms.Select(attrs={'class': 'form-control'}),
            'garment_type': forms.Select(attrs={'class': 'form-control'}),
        }
        


        
class CostSimulationForm(forms.ModelForm):
    class Meta:
        model = CostSimulation
        fields = [
            'start_date', 'end_date', 'remission_number', 
            'total_revenues_COP', 'total_expenses_COP', 'net_profit_COP'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'remission_number': forms.Select(attrs={'class': 'form-control'}),
            'total_revenues_COP': forms.NumberInput(attrs={'class': 'form-control'}),
            'total_expenses_COP': forms.NumberInput(attrs={'class': 'form-control'}),
            'net_profit_COP': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class ProfitSimulationForm(forms.ModelForm):
    class Meta:
        model = ProfitSimulation
        fields = [
            'garment_type', 'factory_owner', 'quantity', 
            'material_cost_COP', 'labor_cost_COP', 'overhead_cost_COP', 
            'selling_price_COP', 'comments'
        ]

class CuttingTableForm(forms.ModelForm):
    class Meta:
        model = CuttingTable
        fields = ['length_m', 'width_m', 'factory_owner']

    
class GarmentTypeForm(forms.ModelForm):
    new_distinctive_features = forms.CharField(
        required=False, 
        widget=forms.Textarea(attrs={
            'rows': 5, 
            'placeholder': 'Ingrese nuevas características distintivas separadas por comas',
            'class': 'form-control',  # Aplicando clase de Bootstrap
        })
    )

    class Meta:
        model = GarmentType
        fields = ['name', 'description', 'product_code', 'base_price_COP', 'fabric_type', 'distinctive_features', 'operations']
        widgets = {
            'distinctive_features': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),  # Aplicando clase de Bootstrap
            'operations': forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),  # Aplicando clase de Bootstrap
            'name': forms.TextInput(attrs={'class': 'form-control'}),  # Aplicando clase de Bootstrap
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),  # Aplicando clase de Bootstrap
            'product_code': forms.TextInput(attrs={'class': 'form-control'}),  # Aplicando clase de Bootstrap
            'base_price_COP': forms.NumberInput(attrs={'class': 'form-control'}),  # Aplicando clase de Bootstrap
            'fabric_type': forms.Select(attrs={'class': 'form-control'}),  # Aplicando clase de Bootstrap
        }


GarmentPartFormSet = inlineformset_factory(
    GarmentType, 
    GarmentPart, 
    fields=('name', 'area_m2'), 
    extra=1, 
    can_delete=True
)

class SizeForm(forms.ModelForm):
    class Meta:
        model = Size
        fields = ['name', 'factory_owner', 'garment_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'factory_owner': forms.Select(attrs={'class': 'form-control'}),
            'garment_type': forms.Select(attrs={'class': 'form-control'}),
        }
        


class FabricTypeForm(forms.ModelForm):
    class Meta:
        model = FabricType
        fields = ['name', 'description', 'gramaje']  # Añade aquí todos los campos que quieres que aparezcan en el formulario


class DistinctiveFeatureForm(forms.ModelForm):
    class Meta:
        model = DistinctiveFeature
        fields = ['name']
        
class CuttingServiceForm(forms.ModelForm):
    class Meta:
        model = CuttingService
        fields = '__all__'  # Lista todos los campos del modelo, ajusta esto según tus necesidades.
        widgets = {
            'date_requested': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'date_completed': forms.TextInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            # ... (añade otros campos y widgets según sea necesario)
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})