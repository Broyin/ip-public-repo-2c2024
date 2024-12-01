# capa de vista/presentación

from django.shortcuts import redirect, render
from app.layers.services.services import getAllImages #se completan los campos que faltaban y se importa la funcion correspondiente
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login
from app.layers.transport.transport import fetch_characters
from django.contrib import messages
from django.contrib.auth.models import User
from app.models import Favourite

def index_page(request):
    return render(request, 'index.html')

# esta función obtiene 2 listados que corresponden a las imágenes de la API y los favoritos del usuario, y los usa para dibujar el correspondiente template.
# si el opcional de favoritos no está desarrollado, devuelve un listado vacío.
def home(request):
    # Llamamos a getAllImages para obtener las imágenes.
    images = getAllImages()

    # Si tienes un parámetro de búsqueda (input), asegúrate de pasarlo a la vista.
    search_input = request.GET.get('search', None)

    if search_input:
        # Filtramos las imágenes si se proporciona un parámetro de búsqueda.
        images = [img for img in images if search_input.lower() in img.name.lower()]

    # También puedes pasar los favoritos si es necesario.
    favourite_list = []
    if request.user.is_authenticated: favourite_list = Favourite.objects.filter(user=request.user) # Obtener favoritos del usuario

    return render(request, 'home.html', { 'images': images, 'favourite_list': favourite_list })

def search(request):
    ##Aqui comienza modificacion de buscador
    
    if request.method == 'POST': ## debe cumplir esta condicion de method
        
        search_msg = request.POST.get('query', '') 
        if search_msg:
            # Redirigimos a home con el parámetro de búsqueda.   
            return redirect(f'/home?search={search_msg}') ##devuelve parametro de busqueda
        else:
            # Si no hay mensaje de búsqueda, redirigimos a home.
            return redirect('home')
    else:
        # Si la solicitud no es POST, redirigimos a home.
        return redirect('home')
    ##Aqui finaliza modificacion..
## Funcion de registro
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            if User.objects.filter(username=username).exists():
                messages.error(request, 'El nombre de usuario ya está en uso')
            elif User.objects.filter(email=email).exists():
                messages.error(request, 'El correo electrónico ya está en uso')
            else:
                user = User.objects.create_user(username=username, email=email, password=password1)
                user.save()
                login(request, user)
                return redirect('home')
        else:
            messages.error(request, 'Las contraseñas no coinciden')
    return render(request, 'registration/register.html')

# Estas funciones se usan cuando el usuario está logueado en la aplicación.
@login_required
def getAllFavouritesByUser(request):
    favourite_list = Favourite.objects.filter(user=request.user)
    return render(request, 'favourites.html', { 'favourite_list': favourite_list })

@login_required
def saveFavourite(request):
    if request.method == 'POST':
        print("Solicitud POST recibida") # Agrega esto para depuración
        # Aquí puedes agregar la lógica para guardar el favorito
        # Por ejemplo, supongamos que tienes un modelo llamado Favourite
        name = request.POST.get('name')
        url = request.POST.get('url')
        status = request.POST.get('status')
        last_location = request.POST.get('last_location')
        first_seen = request.POST.get('first_seen')
        print(f"Datos recibidos: {name}, {url}, {status}, {last_location}, {first_seen}") # Depuración
        # Aquí deberías guardar estos datos en tu modelo de Favoritos
# Crear y guardar el nuevo favorito 
        favourite, created = Favourite.objects.get_or_create( 
            user=request.user, 
            url=url, name=name, 
            status=status, 
            last_location=last_location, 
            first_seen=first_seen 
            )
        print(f"Favorito creado: {created}, Favorito: {favourite}") # Depuración
            # Suponiendo que guardaste correctamente el favorito:
        if created: 
            messages.success(request, 'Añadido a favoritos') 
        else: 
            messages.success(request, 'Añadido a favoritos')
        return redirect('home')  # Redirige a la página de inicio o a donde consideres apropiado

    # Si no es una solicitud POST, redirige al usuario a la página de inicio
    return redirect('home')


@login_required
def deleteFavourite(request, favourite_id):
    try:
        favourite = Favourite.objects.get(id=favourite_id, user=request.user)
        favourite.delete()
        messages.success(request, 'Favorito eliminado')
    except Favourite.DoesNotExist:
        messages.error(request, 'No se pudo encontrar el favorito')
    return redirect('favoritos')


@login_required
def exit(request):
    logout(request) 
    return redirect('index-page')