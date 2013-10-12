from django.contrib import admin 
from .models import DataFrame, DataColumn, Document

class DataFrameAdmin(admin.ModelAdmin):
	date_hierarchy = "created_at"
	fields = ("name", "slug", "db_table_name", "owner", "docfile")
	list_display = ["name", "slug", "db_table_name", "updated_at", "owner"]
	#list_display_links = ["title"]
	#list_editable = ["published"]
	#list_filter = ["published", "updated_at", "author"]
	prepopulated_fields = {"slug": ("name",)}
	#search_fields = ["title", "content"]
	
admin.site.register(DataFrame, DataFrameAdmin)

class DataColumnAdmin(admin.ModelAdmin):
	date_hierarchy = "created_at"
	fields = ("name", "slug", "db_column_name", "parent_frame")
	list_display = ["name", "slug", "db_column_name", "updated_at", "parent_frame"]
	#list_display_links = ["title"]
	#list_editable = ["published"]
	#list_filter = ["published", "updated_at", "author"]
	prepopulated_fields = {"slug": ("name",)}
	#search_fields = ["title", "content"]
	
admin.site.register(Document, admin.ModelAdmin)

