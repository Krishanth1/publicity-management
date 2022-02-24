from .models import Tag

def menu(request):
    tags = Tag.objects.all()
    return { 'nav_menu' : tags,
    }
    

    