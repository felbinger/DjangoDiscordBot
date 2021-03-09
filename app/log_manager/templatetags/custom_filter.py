import re

from django.template.defaultfilters import register
from markdown import Markdown
from markupsafe import Markup


@register.filter(name='regexr')
def strike(s):
    return re.sub(r'~~(.*?)~~', r'<strike>\1</strike>', s)


@register.filter(name='markdown')
def markdown(s):
    return Markup(Markdown(extensions=['meta']).convert(s))
