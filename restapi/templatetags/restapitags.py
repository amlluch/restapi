from __future__ import absolute_import, unicode_literals

from django import template
from pdudbapp.models import Users as Userpdu
from pdudbapp.models import Idata
from django.utils.html import escape, format_html
from django.urls import reverse


register = template.Library()

@register.simple_tag
def userslist():
    usuarios = Userpdu.objects.using('pdudb').all()
    snipet = '<ul class="dropdown-menu">'
    for usuario in usuarios:
        snipet += '<li><a href="' + reverse('usersRest', args=(usuario.user,)) +'">' + usuario.user + '</a></li>'
    snipet += '</ul>'
    return format_html(snipet)

@register.simple_tag
def outletslist():
    outlets = Idata.objects.using('pdudb').all()
    snipet = '<ul class="dropdown-menu">'
    for outlet in outlets:
        snipet += ('<li><a style="white-space: inherit ! important;" href ="' + 
                   reverse('outletRest', args=(outlet.posicion,)) +
                   '">{pos} {user}<span id="{glifo}" class ="glyphicon glyphicon glyphicon-off pull-right"/></a>').format(
                       pos = outlet.posicion,
                       user = outlet.nombre[:10],
                       glifo = 'poff' if outlet.estado == "0" else'pon'
                       )
    snipet += '</ul>'
    return format_html(snipet)