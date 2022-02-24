from django.contrib import admin
from .models import Product, Article, Tag  #import Product model here

# Register your models here.

admin.site.register(Product)
admin.site.register(Article)
admin.site.register(Tag)