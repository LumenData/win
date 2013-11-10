from django.contrib import admin 
from .models import DataFile, DataFrame

class DataFileAdmin(admin.ModelAdmin):
	date_hierarchy = "created_at"
	fields = ("name", "slug", "owner", "file")
	list_display = ["name", "slug", "owner"]
	#list_display_links = ["title"]
	#list_editable = ["published"]
	#list_filter = ["published", "updated_at", "author"]
	prepopulated_fields = {"slug": ("name",)}
	#search_fields = ["title", "content"]


admin.site.register(DataFile, DataFileAdmin)

admin.site.register(DataFrame, admin.ModelAdmin)


class DataColumnAdmin(admin.ModelAdmin):
	date_hierarchy = "created_at"
	fields = ("name", "slug", "db_column_name", "parent_file")
	list_display = ["name", "slug", "db_column_name", "updated_at", "parent_file"]
	#list_display_links = ["title"]
	#list_editable = ["published"]
	#list_filter = ["published", "updated_at", "author"]
	prepopulated_fields = {"slug": ("name",)}
	#search_fields = ["title", "content"]
