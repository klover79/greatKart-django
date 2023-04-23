from django.contrib import admin
from .models import Product, Variation, ProductGallery
import admin_thumbnails

@admin_thumbnails.thumbnail('image')
class ProductGalleryInline(admin.TabularInline):
    model = ProductGallery
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    inlines = [ProductGalleryInline]

class VariationAdmin(admin.ModelAdmin):
    list_display = ('product',
                    'variation_category',
                    'variation_value',
                    'is_active',
                    'created_date',
                    'updated_date')
    list_editable = ('is_active',)
    list_filter = ('product', 'is_active','variation_category')
    list_per_page = 10



admin.site.register(Product,ProductAdmin )
admin.site.register(Variation,VariationAdmin)
admin.site.register(ProductGallery)
