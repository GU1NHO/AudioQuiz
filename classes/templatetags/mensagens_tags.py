from django import template

register = template.Library()

@register.inclusion_tag('classes/mural/mensagem_recursiva.html')
def render_respostas(mensagem, classe, user):
    """Renderiza uma mensagem e suas respostas recursivamente."""
    return {
        'mensagem': mensagem,
        'classe': classe,
        'user': user,
    }