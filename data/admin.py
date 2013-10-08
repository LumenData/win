from django.contrib import admin 
from .models import DataFrame 

class DataFrameAdmin(admin.ModelAdmin):
	date_hierarchy = "created_at"
	fields = ("name", "slug", "db_table_name")
	list_display = ["name", "slug", "db_table_name", "updated_at"]
	#list_display_links = ["title"]
	#list_editable = ["published"]
	#list_filter = ["published", "updated_at", "author"]
	#prepopulated_fields = {"slug": ("title",)}
	#search_fields = ["title", "content"]
	
admin.site.register(DataFrame, DataFrameAdmin)