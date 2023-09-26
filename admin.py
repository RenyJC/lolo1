from django.contrib import admin
from .models import (
    BaseUser, Admin, Plan, 
    FactoryOwner, FactoryAdmin, Client, Period, GarmentType, Size, Operation, OperationGroup, 
    RemissionSizeQuantity, Remission, Operator, OperatorLog, RemissionDelivery, Invoice, WastedGarment, 
    OperatorAdditionalOperation, OperatorReport, Payment, Advance, Bonus, ExpenseType, Expense, 
    AccountReceivable, AccountPayable, CostSimulation, ProfitSimulation, CuttingTable, GarmentPart, CuttingPattern, Arrangement, 
    DailyWorkVolume, FabricType, Batch
)


@admin.register(Admin)
class AdminAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_superuser')
    search_fields = ('email', 'first_name', 'last_name')


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'is_active', 'billing_frequency')
    search_fields = ('name',)


@admin.register(FactoryOwner)
class FactoryOwnerAdmin(admin.ModelAdmin):
    list_display = ('email', 'identification_type', 'identification_number', 'date_joined')
    search_fields = ('email', 'identification_number', 'identification_type')


@admin.register(FactoryAdmin)
class FactoryAdminAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_joined', 'is_active')
    search_fields = ('email',)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('name', 'NIT', 'email')
    search_fields = ('name', 'NIT', 'email')


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
    list_display = ('start_date', 'end_date', 'factory_owner')
    search_fields = ('start_date', 'end_date', 'factory_owner__email')

@admin.register(GarmentType)
class GarmentTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_code', 'base_price_COP', 'factory_owner', 'client')
    search_fields = ('name', 'product_code', 'factory_owner__email', 'client__name')

@admin.register(FabricType)
class FabricTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']

@admin.register(Size)
class SizeAdmin(admin.ModelAdmin):
    list_display = ('name', 'garment_type')
    search_fields = ('name', 'garment_type__name')

@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ('name', 'value_COP', 'productivity_level', 'factory_owner')
    search_fields = ('name', 'factory_owner__email')

@admin.register(OperationGroup)
class OperationGroupAdmin(admin.ModelAdmin):
    list_display = ('operation', 'garment_type', 'sequence_number')
    search_fields = ('operation__name', 'garment_type__name')

@admin.register(RemissionSizeQuantity)
class RemissionSizeQuantityAdmin(admin.ModelAdmin):
    list_display = ('remission', 'size', 'quantity')
    search_fields = ('remission__number', 'size__name')

@admin.register(Remission)
class RemissionAdmin(admin.ModelAdmin):
    list_display = ('number', 'garment_type', 'client', 'unit_value', 'total_value') # Asegúrate de que los campos aquí existen en tu modelo
    search_fields = ('number', 'garment_type__name', 'client__name', 'factory_owner__email')

@admin.register(Operator)
class OperatorAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'factory_owner', 'is_active', 'best_operation')
    search_fields = ('name', 'email', 'factory_owner__email', 'best_operation__name')

@admin.register(OperatorLog)
class OperatorLogAdmin(admin.ModelAdmin):
    list_display = ('operator', 'action', 'timestamp')
    search_fields = ('operator__name', 'action')
    
@admin.register(Arrangement)
class ArrangementAdmin(admin.ModelAdmin):
    list_display = ('operation', 'operator', 'remission', 'client', 'garment_count', 'created_at')    
    search_fields = ('remission__number', 'client__name', 'operator__name')


@admin.register(RemissionDelivery)
class RemissionDeliveryAdmin(admin.ModelAdmin):
    list_display = ('remission', 'total_quantity', 'total_value_COP', 'client', 'factory_owner')
    search_fields = ('remission__number', 'client__name', 'factory_owner__email')
    

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'remission_delivery', 'client', 'factory_owner')
    search_fields = ('id', 'remission_delivery__id', 'client__name', 'factory_owner__email')

@admin.register(WastedGarment)
class WastedGarmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'remission_delivery', 'operator', 'quantity', 'value_COP', 'retail_value_COP', 'date')
    search_fields = ('id', 'remission_delivery__id', 'operator__name')

@admin.register(OperatorAdditionalOperation)
class OperatorAdditionalOperationAdmin(admin.ModelAdmin):
    list_display = ('operator', 'operation')
    search_fields = ('operator__name', 'operation__name')

@admin.register(OperatorReport)
class OperatorReportAdmin(admin.ModelAdmin):
    list_display = ('operator', 'period', 'remission', 'client', 'garment_type', 'operation', 'total_operations', 'total_value_COP')
    search_fields = ('operator__name', 'period__start_date', 'remission__number', 'client__name', 'garment_type__name', 'operation__name')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('operator', 'total_value_COP', 'payment_date', 'period')
    search_fields = ('operator__name', 'payment_date', 'period__start_date')
    

@admin.register(Advance)
class AdvanceAdmin(admin.ModelAdmin):
    list_display = ['operator', 'amount_COP', 'request_date', 'description']

@admin.register(Bonus)
class BonusAdmin(admin.ModelAdmin):
    list_display = ['operator', 'amount_COP', 'grant_date', 'reason']

@admin.register(ExpenseType)
class ExpenseTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'factory_owner']

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['type', 'value_COP', 'date_incurred', 'description', 'factory_owner', 'client']

@admin.register(AccountReceivable)
class AccountReceivableAdmin(admin.ModelAdmin):
    list_display = ['remission_delivery', 'amount_due', 'due_date', 'is_paid', 'date_paid']

@admin.register(AccountPayable)
class AccountPayableAdmin(admin.ModelAdmin):
    list_display = ['expense', 'amount_due', 'due_date', 'is_paid', 'date_paid']

@admin.register(CostSimulation)
class CostSimulationAdmin(admin.ModelAdmin):
    list_display = ['start_date', 'end_date', 'remission_number', 'total_revenues_COP', 'total_expenses_COP', 'net_profit_COP']

@admin.register(ProfitSimulation)
class ProfitSimulationAdmin(admin.ModelAdmin):
    list_display = ['garment_type', 'factory_owner', 'quantity', 'material_cost_COP', 'labor_cost_COP', 'overhead_cost_COP', 'selling_price_COP', 'total_cost_COP', 'projected_profit_COP', 'is_profitable']

@admin.register(CuttingTable)
class CuttingTableAdmin(admin.ModelAdmin):
    list_display = ['length_m', 'width_m', 'factory_owner', 'total_area_m2']

@admin.register(GarmentPart)
class GarmentPartAdmin(admin.ModelAdmin):
    list_display = ['name', 'area_m2', 'garment_type']

@admin.register(CuttingPattern)
class CuttingPatternAdmin(admin.ModelAdmin):
    list_display = ['name', 'garment_type', 'efficiency']
    
@admin.register(DailyWorkVolume)
class DailyWorkVolumeAdmin(admin.ModelAdmin):
    list_display = ('operator', 'client', 'remission', 'date', 'volume')
    search_fields = ('operator__name', 'client__name', 'remission__number', 'date')
    list_filter = ('date', 'operator', 'client', 'remission')

@admin.register(Batch)
class BatchAdmin(admin.ModelAdmin):
    list_display = ('id', 'number', 'description')  # Añade los campos que quieres mostrar