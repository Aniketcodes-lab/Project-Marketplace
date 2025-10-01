from django.db import models

class Technology(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Technologies"
    
    @classmethod
    def create_technology(cls, tech):
        technology, created = cls.objects.get_or_create(name=tech)
        return technology

    @classmethod
    def get_technologies(cls):
        return cls.objects.all()
    
    @classmethod
    def get_technology_by_name(cls, name):
        try:
            return cls.objects.get(name=name)
        except cls.DoesNotExist:
            return None