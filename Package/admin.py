from django.contrib import admin
from .models import Package
from django.forms import ModelForm


class PackageForm(ModelForm):
    def clean(self):
        ri = self.cleaned_data.get('recurring_interval')
        ru = self.cleaned_data.get('recurring_unit')
        if ri and ru is None:
            self.add_error('recurring_unit', 'The field is required')
        elif ri == 'year' and ru > 1:
            self.cleaned_data['recurring_unit'] = 1
        elif ri == 'month' and ru > 12:
            self.cleaned_data['recurring_unit'] = 12
        pass
    pass


@admin.register(Package)
class PackageModel(admin.ModelAdmin):
    form = PackageForm
    empty_value_display = 'N/A'
    list_display = ['name', 'amount', 'currency', 'is_hidden', 'recurring_unit', 'recurring_interval']

    fieldsets = (
        ('Package Details', {
            'description': 'Set name and description for the package',
            'fields': ('name', 'description', 'is_hidden')
        }),
        ('Amount Details', {
            'description': 'Set package amount and currency',
            'fields': ('amount', 'currency')
        }),
        ('Recurring Packages', {
            'classes': ('collapse', ),
            'description': 'Make this package to collect recurring donations',
            'fields': ('recurring_unit', 'recurring_interval')
        })
    )

    def save_model(self, request, obj, form, change):
        if change and not obj.recurring_interval:
            obj.recurring_unit = None
        return super(PackageModel, self).save_model(request, obj, form, change)
    pass
