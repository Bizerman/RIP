
from django.db import connection
from django.shortcuts import render, redirect
from django.utils import timezone

from gateway.models import Gateway_el, gateway_element_and_mission
from gateway.models import Gateway_mission
from django.contrib.auth.models import User
def gateway_products_page_render(request):
    gateway_mission = get_draft_mission()
    if gateway_mission != None:
        el_quantity = len(gateway_mission.get_elements())
    else:
        el_quantity = 0
    if (request.GET.get('gateway_el') != None): search_gateway_el = str(request.GET.get('gateway_el'))
    else: search_gateway_el = ''
    filtered_gateway_el = [
        product for product in Gateway_el.objects.all()
        if search_gateway_el.lower() in product.title.lower()
        ]
    return render(request, 'gateway_products.html', {'data' : {'gateway_el' : filtered_gateway_el, 'mission' : gateway_mission, 'quantity':el_quantity, 'search':search_gateway_el}})
def gateway_product_page_render(request,id):
    element = next((item for item in Gateway_el.objects.all() if item.id == id), None)
    return render(request, 'gateway_product.html', {'product': element})
def mission_page_render(request, id):
    if not Gateway_mission.objects.filter(pk=id).exists():
        return render(request,"404.html")
    mission = Gateway_mission.objects.get(id=id)
    if mission.status == 5:
        return render(request, "404.html")

    return render(request, 'mission.html', {'mission': mission})
def add_to_mission(request,el_id):
    el_name = request.POST.get("title")
    redirect_url = f"/?el_name={el_name}" if el_name else "/"
    gateway_el = Gateway_el.objects.get(pk=el_id)
    draft_mission = get_draft_mission()
    if draft_mission is None:
        draft_mission = Gateway_mission.objects.create()
        draft_mission.creator = get_current_user()
        draft_mission.create_datetime = timezone.now()
        draft_mission.save()
    if gateway_element_and_mission.objects.filter(mission=draft_mission,element=gateway_el).exists():
        return redirect(redirect_url)
    item = gateway_element_and_mission(
        mission=draft_mission,
        element=gateway_el
    )
    item.save()
    return redirect(redirect_url)
def del_mission(request,id):
    if not Gateway_mission.objects.filter(pk=id).exists():
        return redirect("/")
    with connection.cursor() as cursor:
        cursor.execute("UPDATE gateway_missions SET status=5 WHERE id=%s",[id])
    return redirect("/")
def get_draft_mission():
    return  Gateway_mission.objects.filter(status=1).first()
def get_current_user():
    return User.objects.filter().first()