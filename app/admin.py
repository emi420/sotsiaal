# -*- coding: utf-8 -*-
from app.models import User, Site, Category, Story, Msg, Reply, Relationship, Vote
from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    model = User
    verbose_name = "Usuario"
    verbose_name_plural = "Usuarios"

class SiteAdmin(admin.ModelAdmin):
    model = Site
    verbose_name = "Sitio"
    verbose_name_plural = "Sitios"

class CategoryAdmin(admin.ModelAdmin):
    model = Category
    verbose_name = "Categoría"
    verbose_name_plural = "Categorías"

class StoryAdmin(admin.ModelAdmin):
    model = Story
    verbose_name = "Historia"
    verbose_name_plural = "Historias"

class MsgAdmin(admin.ModelAdmin):
    model = Msg
    verbose_name = "Mensaje"
    verbose_name_plural = "Mensajes"

class ReplyAdmin(admin.ModelAdmin):
    model = Reply
    verbose_name = "Respuestas"
    verbose_name_plural = "Respuestas"
    
class RelationshipAdmin(admin.ModelAdmin):
    model = Relationship
    verbose_name = "Relación"
    verbose_name_plural = "Relaciones"

class VoteAdmin(admin.ModelAdmin):
    model = Vote
    verbose_name = "Voto"
    verbose_name_plural = "Votos"

admin.site.register(User, UserAdmin)
admin.site.register(Site, SiteAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Story, StoryAdmin)
admin.site.register(Msg, MsgAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(Relationship, RelationshipAdmin)
admin.site.register(Vote, VoteAdmin)


