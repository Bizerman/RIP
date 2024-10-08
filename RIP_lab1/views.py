from django.shortcuts import render
products = [{'title': 'Gateway cosmonaut figure', 'price': 3000, 'id': 1,
             'info':'• Масштаб 1:6\n'
                    ' • 13,5 дюйма в высоту с основанием\n'
                    ' • 1400 грамм'
             },
        {'title': 'Gateway mission patch', 'price': 400,'id': 2,'info':''},
        {'title': 'Gateway mission T-shirt','price': 1500, 'id': 3,
         'info' : 'Размеры - S-XXL\n'
                  'Состав - Хлопок 60% / Полиэстр 40%'},]
def main_page_render(request):
    return render(request, 'products.html', {'data' : {'products' : products}})
def product_page_render(request,id):
    product = next((item for item in products if item['id'] == id), None)
    return render(request, 'product.html',{'product':product})
