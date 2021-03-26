from django.shortcuts import render,redirect
# from django.http import HttpResponse
from .models import *
from .form import OrderForm,CustomerForm,CreateUserForm
from itertools import islice
from django.forms import inlineformset_factory
from .filters import OrderFilter
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user,allowed_users,admin_only
from django.contrib.auth.models import Group
# Create your views here.

@unauthenticated_user
def registerPage(request):
    # form = UserCreationForm()
    form = CreateUserForm()
    if(request.method == "POST"):
        form = CreateUserForm(request.POST)
        if(form.is_valid()):
            user = form.save()
            username = form.cleaned_data.get('username')

            group = Group.objects.get(name='customers')
            user.groups.add(group)

            messages.success(request,'Account was created for ' + username)
            return redirect('/login')
    context={'form':form}
    return render(request, 'accounts/register.html',context)

@unauthenticated_user
def loginPage(request):
    context={}
    if(request.method == "POST"):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, "Username OR Password is incorrect")
        
    return render(request, 'accounts/login.html',context)

@login_required(login_url='login')
def logoutUser(request):
    logout(request)
    return render(request,'accounts/login.html')

# @login_required(login_url='login')
# @allowed_users(allowed_roles=['admin'])
# @admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()
    total_customers = customers.count()
    total_orders = orders.count()
    Delivered = orders.filter(status="Delivered").count()
    Pending = orders.filter(status="Pending").count()
    # Last 5 order
    lastorders = list(islice(reversed(orders), 0, total_orders))
    # lastorders.reverse()
    context = {'customers'  :customers,'orders' :lastorders[:5],'Pending':Pending,'Delivered':Delivered,'total_orders':total_orders} 
    return render(request,'accounts/dashboard.html',context=context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def products(request):
    context = {'products':Product.objects.all()}
    return render(request,'accounts/products.html',context=context)

@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def customer(request,pk):
    customer = Customer.objects.get(id=pk)
    orders = customer.order_set.all()
    total_orders = orders.count()
    myFilter = OrderFilter(request.GET, queryset=orders)
    orders = myFilter.qs
    context = {'customer':customer, 'orders':orders,'total_orders':total_orders, 'myFilter':myFilter}
    return render(request,'accounts/customer.html',context=context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createOrder(request,pk):
    OrderFromSet = inlineformset_factory(Customer, Order, fields=('product', 'status'))
    customer = Customer.objects.get(id=pk)
    # form = OrderForm(initial={'customer':customer})
    formset = OrderFromSet(queryset=Order.objects.none(), instance=customer)
    if(request.method == 'POST'):
        # form = OrderForm(request.POST)
        formset = OrderFromSet(request.POST,instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('/')   
    # context = {'form':form}
    context = {'formset':formset}
    return render(request, 'accounts/order_form.html',context=context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def updateOrder(request,pk):
    order = Order.objects.get(id=pk)
    form = OrderForm(instance=order) #old data
    if(request.method=='POST'):
        form = OrderForm(request.POST,instance=order) # new data
        if(form.is_valid()):
            form.save()
            return redirect('/')
    context = {'form':form}
    return render(request, 'accounts/order_form.html',context=context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def deleteOrder(request,pk):
    orderToDelete = Order.objects.get(id=pk)
    if(request.method == 'POST'):
        orderToDelete.delete()
        return redirect('/')
    context = {'item':orderToDelete}
    return render(request, 'accounts/delete.html',context=context)
@login_required(login_url='login')
@allowed_users(allowed_roles=['admin'])
def createCustomer(request):   
    form = CustomerForm()
    if(request.method == 'POST'):
        form = CustomerForm(request.POST)
        if(form.is_valid()):
            form.save()
            return redirect('/')
    context = {'form':form}
    return render(request, 'accounts/customer_form.html',context=context)

def userPage(request):
    context={}
    return render(request, 'accounts/user.html',context)