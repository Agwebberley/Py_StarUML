from django.db import models


class Domains(models.Model):
    DomainID = models.IntegerField(primary_key=True)
    DomainName = models.CharField(max_length=255)
    Description = models.TextField()
    CreatedDate = models.DateTimeField()
    ModifiedDate = models.DateTimeField()
    IsActive = models.BooleanField()


class Entity(models.Model):
    EntityID = models.IntegerField(primary_key=True)
    EntityName = models.CharField(max_length=255)
    CreatedDate = models.DateTimeField()
    ModifiedDate = models.DateTimeField()
    IsActive = models.BooleanField()
    DomainID = models.ForeignKey('Domains', on_delete=models.CASCADE)


class Attributes(models.Model):
    AttributeID = models.IntegerField(primary_key=True)
    AttributeName = models.CharField(max_length=255)
    DataType = models.CharField(max_length=255)
    DefaultValue = models.CharField(max_length=255)
    IsRequired = models.BooleanField()
    IsUnique = models.BooleanField()
    EntityID = models.ForeignKey('Entity', on_delete=models.CASCADE)


class EntityRelationships(models.Model):
    EntityRelationshipID = models.IntegerField(primary_key=True)
    ParentEntityID = models.IntegerField()
    ChildEntityID = models.IntegerField()
    EntityID = models.ForeignKey('Entity', on_delete=models.CASCADE)
    RelationshipID = models.ForeignKey('Relationships', on_delete=models.CASCADE)


class Relationships(models.Model):
    RelationshipID = models.IntegerField(primary_key=True)
    ParentEntityID = models.IntegerField()
    ChildEntityID = models.IntegerField()
    RelationshipName = models.CharField(max_length=255)
    RelationshipType = models.CharField(max_length=50)
    Description = models.TextField()
