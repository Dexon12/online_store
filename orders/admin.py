import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem


def export_to_csv(modeladmin, request, queryset): 
    opts = modeladmin.model._meta # дает доступ к матаданным модели OrderAdmin
    content_disposition = f'attachment; filename={opts.verbose_name}.csv' # Формирует зголовок Content-Disposition для HTTP-ответа, указывая браузеру что ог должен предложить файл для скачивания с указаннным именем
    response = HttpResponse(content_type='text/csv') # Создается объект HttpResponse с типом контента text/csv
    response['Content-Disposition'] = content_disposition # Устанавливам ключ значение
    writer = csv.writer(response) # Создается объект csv.writer для записи данных в объект response.
    fields = [field for field in opts.get_fields() if not \
              field.many_to_many and not field.one_to_many] # Создается список полей, которые будут экспортированы в CSV. Исключаются поля типа many-to-many и one-to-many, так как они могут быть сложными для экспорта в плоский формат CSV.
    # Write a first row with header information
    writer.writerow([field.verbose_name for field in fields])
    # Write data rows
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = 'Export to CSV' # Устанавливается отображаемое имя действия 


class OrderItemInline(admin.TabularInline): # admin.TabularInline используется, когда вы хотите представить связанные объекты в виде таблицы (табличной формы) прямо в форме родительского объекта.
    model = OrderItem
    raw_id_fields = ['product']


def order_payment(obj): 
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>' # Если stripe_id существует, создается HTML-строка, представляющая ссылку. Ссылка открывается в новой вкладке (target="_blank"), и текст ссылки - это значение stripe_id.
        return mark_safe(html) # Используется mark_safe для указания Django, что строка html является безопасной и не должна быть эскейпирована при отображении в шаблоне. Это важно, когда вы вставляете HTML-код в текст страницы.
    return ''
order_payment.short_description = 'Stripe payment'

def order_detail(obj): # Why is it func?
    url = reverse('orders:admin_order_detail', args=[obj.id]) # Этот код использует функцию reverse для создания URL-адреса для просмотра деталей заказа. Он использует именованный URL-путь 'orders:admin_order_detail' и передает аргумент obj.id в качестве параметра.
    return mark_safe(f'<a href="{url}">View</a>')



@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'first_name', 'last_name', 'email',
                    'address', 'postal_code', 'city', 'paid',
                    order_payment, 'created', 'updated',
                    order_detail]
    list_filter = ['paid', 'created', 'updated']
    inlines = [OrderItemInline]
    actions = [export_to_csv]