from import_export import fields, resources
from import_export.widgets import ForeignKeyWidget
from base.models import *

class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category


class SubCategoryResource(resources.ModelResource):
    category = fields.Field(column_name='category', attribute='category', widget=ForeignKeyWidget(Category, field='main_category'))

    class Meta:
        model = Sub_category
        fields = (
            'id',
            'category',
            'sub_category',
        )
