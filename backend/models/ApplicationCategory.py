from django.db import models

class ApplicationCategory(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
    @classmethod
    def create_category(cls, name):
        category, created = cls.objects.get_or_create(name=name)
        return category
        
    @classmethod
    def get_categories(cls):
        return cls.objects.all()
    
    @classmethod
    def get_category_by_name(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            return None

