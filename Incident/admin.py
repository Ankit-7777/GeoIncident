from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from Incident.models import CustomUser, Incident

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = (
        'id', 'first_name', 'last_name', 'email', 'phone_number',
        'is_staff', 'is_active'
    )
    list_filter = ('is_staff', 'is_active', 'is_superuser')
    search_fields = (
        'first_name', 'last_name', 'email',  'phone_number', 'fax_number', 
        'address', 'pin_code', 'city', 'state', 'country'
    )
    ordering = ('first_name', 'last_name',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        (None, {'fields': ('first_name', 'last_name', 'email', 'password')}),
        ('Personal info', {
            'fields': (
                 'phone_number', 'phone_isd_code', 'fax_number',
                'address', 'pin_code', 'city', 'state', 'country'
            )
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        }),
        ('Important dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'first_name', 'last_name', 'email',  'phone_number', 'phone_isd_code',
                'fax_number', 'address', 'pin_code', 'city', 'state', 'country',
                'password1', 'password2'
            ),
        }),
    )

    filter_horizontal = ()

admin.site.register(CustomUser, CustomUserAdmin)



class IncidentAdmin(admin.ModelAdmin):
    list_display = ('id','incident_id', 'reporter', 'details', 'reported_date', 'priority', 'status', 'entity_type')
    list_filter = ('priority', 'status', 'entity_type')
    search_fields = ('incident_id', 'details', 'reporter__username')
    ordering = ('-reported_date',)
    readonly_fields = ('incident_id', 'reported_date')

    def has_change_permission(self, request, obj=None):
        if obj and obj.status == 'Closed' and not request.user.is_superuser:
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        if obj and obj.status == 'Closed' and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

admin.site.register(Incident, IncidentAdmin)

