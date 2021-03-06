import requests
import sys
import datetime
from .forms import *
from django.shortcuts import render
from django.shortcuts import redirect
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import Distance
from geopy.distance import distance as geopy_distance
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.gis.measure import D
from django.http import HttpResponse
from django import template
from nominatim import Nominatim
from geopy.geocoders import Nominatim as geonom
import random
import os
import re
from base64 import b64decode
from django.core.files.base import ContentFile
nom = Nominatim()


def handle_uploaded_file(f, category_name):
    category_name = category_name.replace(' ', '-')
    fname = '{}_{}'.format(random.randint(0, 100), str(f))
    directory = 'media/supermarket_crawlers/{}/images'.format(category_name)
    dest = '{}/{}'.format(directory, fname)
    os.system('mkdir -p {}'.format(os.path.join(settings.MEDIA_ROOT, directory)))
    with open(os.path.join(settings.MEDIA_ROOT, dest), 'wb+') as g:
        g.write(f.read())

    return dest


def default_map(request):
    return render(request, 'map_default.html', {})


def privacy(request):
    return render(request, 'privacy.html', {})


def index(request):
    request.session['categories'] = list(Category.objects.all().values())

    return render(request, 'index.html', {})


def product(request):

    product_id = int(request.GET.get('productId', 0))
    lat = request.session.get('lat', 37.979034) # With Chrome it doesn't work
    lon = request.session.get('lon', 23.782915)
    client_loc = Point(lon, lat, srid=4326)

    registration = Registration.objects.get(pk=product_id)
    product_info = registration.registration_info

    if request.method == 'POST':
        h = FavoritesForm(request.POST)
        f = ReviewForm(request.POST)
        q = QuestionForm(request.POST)
        if f.is_valid():
            if request.user.is_anonymous:
                return redirect('/signin')
            stars = f.cleaned_data['stars']
            rate_explanation = f.cleaned_data['rate_explanation']

            rating = Rating(
                stars=stars,
                rate_explanation=rate_explanation,
                registration=registration,
                volunteer=request.user,
                validity_of_this_rate=0
            )

            rating.save()
            messages.success(
                request, 'Καταχωρήθηκε η κριτική!')
        elif q.is_valid():
            if request.user.is_anonymous:
                return redirect('/signin')
            question_text = q.cleaned_data['question']


            question = Question(
                question_text=question_text,
                registration=registration,
                volunteer=request.user
            )

            question.save()

        elif h.is_valid():
            if request.user.is_anonymous:
                return redirect('/signin')
            if (Favorite.objects.filter(volunteer=request.user, registration=registration).count() == 0):
                fav = Favorite(
                volunteer=request.user,
                registration=registration
                )
                fav.save()

        return redirect('/product/?productId={}'.format(product_id))
    else:
        f = ReviewForm()
        q = QuestionForm()
        h = FavoritesForm()

    prices = registration.prices
    distances = [distance(client_loc, x.shop.location) for x in prices]

    annotated_prices = zip(prices, distances)

    return render(request, 'product.html', {
        'lat': lat,
        'lon': lon,
        'product': registration,
        'form' : f,
        'qform' : q,
        'favform' : h,
        'annotated_prices' : annotated_prices
    })


def location(ip):
    g = GeoIP2()
    return g.geos(ip)



def distance(a, b):
    meters = geopy_distance(a, b).meters
    return Distance(m=meters).km


def order_by_distance(results):
    results.sort(key=lambda x: x[1])
    return results


def order_by_rating(results):
    results.sort(key=lambda x: 0 if x[0].stars is None else -x[0].stars)
    return results


def apply_search_filters(results, dmax, rmin):
    results = filter(lambda x: x[0].stars >= rmin, results)
    results = filter(lambda x: x[1] <= dmax, results)
    return list(results)


def infinite_scroll_paginator(paginator):
    for i in range(1, paginator.num_pages + 1):
        yield paginator.page(i)


@csrf_exempt
def search(request):
    if request.method == 'GET':

        category_id = request.GET.get('categoryId')
        orderby = 'price'
        dmax = sys.maxsize
        dmin = - sys.maxsize
        rmin = 0
        pmin = 0
        rmax = 5
        limit = 100
        pmax = sys.maxsize
        search_text = ''
        lat = request.session.get('lat', 37.979034)
        lon = request.session.get('lon', 23.782915)
        price_data = RegistrationPrice.objects.filter(
            registration__category__id=category_id)[:limit]
        client_loc = Point(lon, lat, srid=4326)
    else:
        search_text = request.POST.get('search')

        category = request.POST.get('category-select', 'Όλες')

        try:
            lat = float(request.POST.get('lat'))
            lon = float(request.POST.get('lon'))
            request.session['lat'] = lat
            request.session['lon'] = lon
        except ValueError:
            lat = 37.979034
            lon = 23.782915
        except TypeError:
            lat = 37.979034
            lon = 23.782915
        finally:
            client_loc = Point(lon, lat, srid=4326)

        try:
            orderby = request.POST.get('orderby')
        except ValueError:
            orderby = 'price'

        try:
            rmin = int(request.POST.get('rmin'))
        except ValueError:
            rmin = 0
        except TypeError:
            rmin = 0

        try:
            pmin = float(request.POST.get('pmin'))
        except ValueError:
            pmin = 0
        except TypeError:
            pmin = 0

        try:
            pmax = float(request.POST.get('pmax'))
        except ValueError:
            pmax = sys.maxsize
        except TypeError:
            pmax = sys.maxsize

        try:
            dmax = float(request.POST.get('dmax'))
        except ValueError:
            dmax = sys.maxsize
        except TypeError:
            dmax = sys.maxsize

        try:
            limit = float(request.POST.get('limit'))
        except ValueError:
            limit = -1
        except TypeError:
            limit = -1

        today = datetime.datetime.today().strftime('%Y-%m-%d')

        price_data = RegistrationPrice.objects.filter(
            registration__name__contains=search_text,
            price__gte=pmin,
            price__lte=pmax,
            date_to__gte=today)

        if category != 'Όλες':
            price_data = price_data.filter(registration__category__category_name=category)

        if limit > 0:
            price_data = price_data[:limit]

        if orderby == 'price':
            price_data = price_data.order_by('price')

    distances = [distance(p.location, client_loc) for p in price_data]
    reg_data_all = [p.registration for p in price_data]
    results = [(r, d, p) for r, d, p in zip(reg_data_all, distances, price_data)]

    if orderby == 'rating':
        results = order_by_rating(results)
    elif orderby == 'distance':
        results = order_by_distance(results)

    # apply search filters
    if request.method == 'POST':
        results = apply_search_filters(results, dmax=dmax, rmin=rmin)

    num_results = len(results)
    # paginate
    paginator = Paginator(results, 20)

    return render(request, 'search.html', {
        'rmin': rmin,
        'pmin': pmin,
        'pmax': pmax,
        'dmax': dmax,
        'num_results': num_results,
        'num_pages': paginator.num_pages,
        'pages': infinite_scroll_paginator(paginator),
        'search_text': search_text,
        'lat': lat,
        'lon': lon
    })


@login_required(login_url='/signin')
def report(request):
    product_id = request.GET.get('productId', 1)

    if request.method == 'POST':
        f = AnswerForm(request.POST)
        if f.is_valid():
            report_text = f.cleaned_data['answer']
            report = Report(
                report_text=report_text,
                volunteer=request.user
                )

            report.save()
            messages.success(
                request, 'Καταχωρήθηκε αναφορά')
            return redirect('/product/?productId={}'.format(product_id))
    else:
        f = AnswerForm()
    return render(request, 'report.html', {'form': f})


@login_required(login_url='/signin')
def remove_favorite(request):
    fav_id = request.GET.get('favId')
    favorite = Favorite.objects.get(pk=int(fav_id))
    favorite.delete()
    return redirect('/profile')

def decode_base64(data, altchars=b'+/'):
    """Decode base64, padding being optional.

    :param data: Base64 data as an ASCII byte string
    :returns: The decoded byte string.

    """
    data = re.sub(rb'[^a-zA-Z0-9%s]+' % altchars, b'', data)  # normalize
    missing_padding = len(data) % 4
    if missing_padding:
        data += b'='* (4 - missing_padding)
    return b64decode(data, altchars)


@login_required(login_url='/signin')
def addproduct(request):
    if request.method == 'POST':
        f = AddProductForm(request.POST, request.FILES)
        if f.is_valid():
            name = f.cleaned_data['name']
            product_description = f.cleaned_data['description']
            # Handle tags input
            tags_string = f.cleaned_data['tags']
            tags_list = tags_string.replace(" ","").split(",")
            tags = json.dumps(tags_list,ensure_ascii=False)

            price = f.cleaned_data['price']
            new_shop_name = f.cleaned_data['new_shop_name']
            new_shop_city = f.cleaned_data['new_shop_city']
            new_shop_street = f.cleaned_data['new_shop_street']
            new_shop_number = f.cleaned_data['new_shop_number']
            category = f.cleaned_data['category']
            date_of_registration = datetime.datetime.today()

            image_url = handle_uploaded_file(request.FILES['img'], category.category_name)

            # Check if a new shop was added
            if len(new_shop_name) > 0:
                print('Adding a new shop named', new_shop_name)
                geolocator = geonom(user_agent="cheapiesgr")
                location = geolocator.geocode(new_shop_street+" "+new_shop_number+" "+new_shop_city)
                if str(type(location)) == "<class 'NoneType'>":
                    print('Μη έγκυρη διεύθυνση.')
                    return render(request, 'addproduct.html',{'form':f, 'correct_address': False})
                shop = Shop(
                    name=new_shop_name,
                    address=new_shop_street+" "+new_shop_number,
                    city=new_shop_city,
                    location='POINT({} {})'.format(location.longitude, location.latitude),
                )
                shop.save()
            else:
                shop = f.cleaned_data['location']
                if str(shop)=="None":
                    return render(request, 'addproduct.html',{'form':f, 'given_shop': False})


            new_product = Registration(
                name=name,
                product_description=product_description,
                image_url=image_url,
                date_of_registration=date_of_registration,
                volunteer=request.user,
                category=category,
                withdrawn=False,
                tags=tags
            )
            new_product.save()


            new_price = RegistrationPrice(
                price=price,
                date_from = date_of_registration.strftime('%Y-%m-%d'),
                date_to = date_of_registration.replace(year = date_of_registration.year + 1).strftime('%Y-%m-%d'),
                shop=shop,
                registration=new_product,
                volunteer=request.user
            )
            new_price.save()

            messages.success(request, 'Η καταχώρηση ήταν επιτυχής')
            return render(request, 'index.html', {})
    else:
        f = AddProductForm()
    return render(request, 'addproduct.html', {'form': f})

@login_required(login_url='/signin')
def updateproduct(request):
    product_id = int(request.GET.get('productId'))
    registration_model = Registration.objects.get(pk=product_id)

    if request.user != registration_model.volunteer:
        return redirect('/index')

    if request.method == 'POST':
        f = UpdateProductForm(request.POST, request.FILES)
        f.initial['name'] = registration_model.name
        f.initial['description'] = registration_model.product_description
        f.initial['category'] = registration_model.category
        f.initial['tags'] = ', '.join(json.loads(registration_model.tags))
        f.initial['withdrawn'] = registration_model.withdrawn

        if f.is_valid():
            registration_model.name = f.cleaned_data['name']
            registration_model.product_description = f.cleaned_data['description']
            # Handle tags input
            tags_string = f.cleaned_data['tags']
            tags_list = tags_string.replace(" ","").split(",")
            registration_model.tags = json.dumps(tags_list,ensure_ascii=False)
            registration_model.withdrawn = f.cleaned_data['withdrawn']
            registration_model.category = f.cleaned_data['category']


            registration_model.save()
            messages.success(request, 'Η καταχώρηση ήταν επιτυχής')
            return render(request, 'index.html', {})
    else:
        f = UpdateProductForm()
        f.initial['name'] = registration_model.name
        f.initial['description'] = registration_model.product_description
        f.initial['category'] = registration_model.category
        f.initial['tags'] = ', '.join(json.loads(registration_model.tags))
        f.initial['withdrawn'] = registration_model.withdrawn
    return render(request, 'update_product.html', {'form': f})


@login_required(login_url='/signin')
def addprice(request):
    product_id = request.GET.get('productId', 1)
    product = Registration.objects.get(pk=int(product_id))
    if request.method == 'POST':
        f = AddPriceForm(request.POST, request.FILES)
        if f.is_valid():

            price = f.cleaned_data['price']
            new_shop_name = f.cleaned_data['new_shop_name']
            new_shop_city = f.cleaned_data['new_shop_city']
            new_shop_street = f.cleaned_data['new_shop_street']
            new_shop_number = f.cleaned_data['new_shop_number']
            date_of_registration = datetime.datetime.today()

            # Check if a new shop was added
            if len(new_shop_name) > 0:
                print('Adding a new shop named', new_shop_name)
                geolocator = geonom(user_agent="cheapiesgr")
                location = geolocator.geocode(new_shop_street+" "+new_shop_number+" "+new_shop_city)
                if str(type(location)) == "<class 'NoneType'>":
                    print('Μη έγκυρη διεύθυνση.')
                    return render(request, 'addprice.html',{'form':f, 'correct_address': False})
                shop = Shop(
                    name=new_shop_name,
                    address=new_shop_street+" "+new_shop_number,
                    city=new_shop_city,
                    location='POINT({} {})'.format(location.longitude, location.latitude),
                )
                shop.save()
            else:
                shop = f.cleaned_data['location']

            new_price = RegistrationPrice(
                price=price,
                date_from = date_of_registration.strftime('%Y-%m-%d'),
                date_to = date_of_registration.replace(year = date_of_registration.year + 1).strftime('%Y-%m-%d'),
                shop=shop,
                registration=product,
                volunteer=request.user
            )
            new_price.save()

            messages.success(request, 'Η καταχώρηση ήταν επιτυχής')
            return render(request, 'index.html', {})
    else:
        f = AddPriceForm()
    return render(request, 'addprice.html', {'form': f})

@login_required(login_url='/signin')
def updateprice(request):

    print('price')
    price_id = int(request.GET.get('priceId'))
    price_model = RegistrationPrice.objects.get(pk=price_id)


    if price_model.volunteer != request.user:
        return redirect('/index')

    if request.method == 'POST':
        f = AddPriceForm(request.POST, request.FILES)
        f.initial['price'] = price_model.price
        f.initial['location'] = price_model.shop
        if f.is_valid():
            price = f.cleaned_data['price']
            new_shop_name = f.cleaned_data['new_shop_name']
            new_shop_city = f.cleaned_data['new_shop_city']
            new_shop_street = f.cleaned_data['new_shop_street']
            new_shop_number = f.cleaned_data['new_shop_number']
            date_of_registration = datetime.datetime.today()

            # Check if a new shop was added
            if len(new_shop_name) > 0:
                print('Adding a new shop named', new_shop_name)
                geolocator = geonom(user_agent="cheapiesgr")
                location = geolocator.geocode(new_shop_street+" "+new_shop_number+" "+new_shop_city)
                if str(type(location)) == "<class 'NoneType'>":
                    print('Μη έγκυρη διεύθυνση.')
                    return render(request, 'addprice.html',{'form':f, 'correct_address': False})
                shop = Shop(
                    name=new_shop_name,
                    address=new_shop_street+" "+new_shop_number,
                    city=new_shop_city,
                    location='POINT({} {})'.format(location.longitude, location.latitude),
                )
                shop.save()
            else:
                shop = f.cleaned_data['location']

            price_model.price = price
            price_model.shop = shop

            price_model.save()

            messages.success(request, 'Η καταχώρηση ήταν επιτυχής')
            return render(request, 'index.html', {})
    else:
        f = AddPriceForm()
        f.initial['price'] = price_model.price
        f.initial['location'] = price_model.shop
    return render(request, 'update_price.html', {'form': f})


def user_auth(request):
    return render(request, 'user_auth.html', {})

@login_required(login_url='/signin')
def answer(request):
    question_id = request.GET.get('questionId', 1)
    product_id = request.GET.get('productId', 1)
    question = Question.objects.get(pk=int(question_id))

    if request.method == 'POST':
        f = AnswerForm(request.POST)
        if f.is_valid():
            answer_text = f.cleaned_data['answer']
            answer = Answer(
                answer_text=answer_text,
                volunteer=request.user,
                question=question
            )

            answer.save()
            messages.success(
                request, 'Ο λογαριασμός δημιουργήθηκε με επιτυχία!')
            return redirect('/product/?productId={}'.format(product_id))
    else:
        f = AnswerForm()
    return render(request, 'answer.html', {'form': f})


def signup(request):
    if request.method == 'POST':
        f = UserRegistrationForm(request.POST)
        if f.is_valid():
            f.save()
            messages.success(
                request, 'Ο λογαριασμός δημιουργήθηκε με επιτυχία!')
            return render(request, 'index.html', {})
    else:
        f = UserRegistrationForm()
    return render(request, 'signup.html', {'form': f})


def signout(request):
    logout(request)
    return render(request, 'index.html', {})


def signin(request):
    if request.method == 'POST':
        f = UserLoginForm(request.POST)
        if f.is_valid():
            username = f.cleaned_data['user']
            password = f.cleaned_data['password']

            user = authenticate(username=username, password=password)

            if user is not None:
                print('login sucess')
                if user.is_active:
                    login(request, user)
                    messages.success(request, 'Συνδεθήκατε με επιτυχία!')
                    return render(request, 'index.html', {})
            else:
                print('login failed')
    else:
        f = UserLoginForm()
    return render(request, 'signin.html', {'form': f})


def profile(request):
    user = request.user
    registered_products =  user.registrationprice_set.all()
    user_questions =  user.question_set.all()
    user_answers = user.answer_set.all()
    user_favorites = user.favorite_set.all()
    user_prices = user.registrationprice_set.all()
    if request.method == 'POST':
        f = UserProfileForm(request.POST, username = user.username)
        if f.is_valid():
            username = user.username
            old_password = f.cleaned_data['old_password']
            new_password = f.cleaned_data['new_password']
            new_password_repeat = f.cleaned_data['new_password_repeat']
            u = authenticate(username=username, password=old_password)
            if u is not None:
                u.set_password(new_password)
                u.save()
                login(request, u)
                messages.success(request, 'H αλλαγή πραγματοποιήθηκε με επιτυχία!')
                return render(request, 'index.html', {})
            else:
                print("Authentication failed")


    else:
        f = UserProfileForm(username = user.username)
    return render(request, 'profile.html', {'form': f, 'user': user,
                                            'products' : registered_products,
                                            'questions' : user_questions,
                                            'answers' : user_answers,
                                            'favorites' : user_favorites,
                                            'prices' : user_prices
                                            })
