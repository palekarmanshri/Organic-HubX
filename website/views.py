from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from .utils import generate_invoice_pdf, send_order_email
from .models import Profile, Product, Order,Contact,Category,Wishlist,OrderItem
from django.db.models import Sum, F


# =========================
# HOME & STATIC PAGES
# =========================

def home(request):
    profile = getattr(request.user, 'profile', None) if request.user.is_authenticated else None
    return render(request, 'website/home.html', {'profile': profile})


def about(request):
    return render(request, 'website/about.html')


def track_order(request):
    order = None
    if request.method == "POST":
        order_id = request.POST.get("order_id")
        order = Order.objects.filter(order_id=order_id).first()

    return render(request, 'website/track_order.html', {'order': order})



# =========================
# REGISTRATION
# =========================
def register(request):
    if request.method == "POST":
        role = request.POST.get("role")
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        address = request.POST.get("address")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        photo = request.FILES.get("photo")

        # Check passwords
        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        # Check if email already exists
        if User.objects.filter(username=email).exists():
            messages.error(request, "Email already registered")
            return redirect("register")

        # Create user
        user = User.objects.create_user(
            username=email,  # Django stores email as username
            email=email,
            password=password,
            first_name=name
        )

        # Create profile
        Profile.objects.create(
            user=user,
            role=role,
            phone=phone,
            address=address,
            photo=photo
        )

        messages.success(request, "Registered successfully! Please login.")
        return redirect("login")

    return render(request, "website/register.html")


# =========================
# LOGIN / LOGOUT
# =========================
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        # Authenticate using email as username
        user = authenticate(request, username=email, password=password)

        if user:
            login(request, user)

            # Redirect based on role
            if hasattr(user, 'profile') and user.profile.role == "farmer":
                return redirect("farmer_dashboard")
            else:
                return redirect("products")

        messages.error(request, "Invalid credentials")
        return redirect("login")

    return render(request, "website/login.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# =========================
# FARMER DASHBOARD
# =========================
@login_required
def farmer_dashboard(request):
    # 1. Security Check
    if not hasattr(request.user, 'profile') or request.user.profile.role != "farmer":
        messages.error(request, "Access denied")
        return redirect("home")

    categories = Category.objects.all()

    # 2. Handle Form Submission
    if request.method == "POST":
        Product.objects.create(
            farmer=request.user,
            category_id=request.POST.get("category"), # Uses the ID from the <select>
            name=request.POST.get("name"),
            description=request.POST.get("description"),
            price=request.POST.get("price"),
            quantity=request.POST.get("quantity"),
            unit=request.POST.get('unit'),
            image=request.FILES.get("image")
        )
        messages.success(request, "Product added successfully")
        return redirect("farmer_dashboard")

    # 3. Fetch data for the GET request
    # Make sure to filter products by the logged-in farmer
    products = Product.objects.filter(farmer=request.user)
    
    # 4. Pass EVERYTHING to the template
    return render(request, "website/farmer_dashboard.html", {
        "categories": categories,
        "products": products  # <--- This was missing!
    })


@login_required
def edit_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.name = request.POST['name']
        product.description = request.POST['description']
        product.price = request.POST['price']
        product.quantity = request.POST['quantity']
        product.unit = request.POST['unit']

        if 'image' in request.FILES:
            product.image = request.FILES['image']

        product.save()
        return redirect('farmer_dashboard')

    return render(request, 'website/edit_product.html', {'product': product})


@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)

    if request.method == "POST":
        product.delete()
        return redirect('farmer_dashboard') 


# =========================
# USER PRODUCTS
# =========================
def products(request):
    categories = Category.objects.all()
    products = Product.objects.select_related("farmer", "category")

    category_id = request.GET.get("category")
    if category_id:
        products = products.filter(category_id=category_id)

    return render(request, "website/products.html", {
        "categories": categories,
        "products": products
    })

@login_required
def add_to_cart(request, product_id):
    if request.method == "POST":
        cart = request.session.get('cart', {})
        product_id = str(product_id)

        if product_id in cart:
            cart[product_id]['qty'] += 1
        else:
            cart[product_id] = {'qty': 1}

        request.session['cart'] = cart
        request.session.modified = True

        return JsonResponse({
            'status': 'ok',
            'product_id': product_id,
            'qty': cart[product_id]['qty']
        })

    return JsonResponse({'status': 'error'}, status=400)

@login_required
def update_cart(request):
    product_id = request.POST.get("product_id")
    change = int(request.POST.get("change"))

    item = Wishlist.objects.filter(
        user=request.user,
        product_id=product_id
    ).first()

    if not item:
        return JsonResponse({"success": False, "error": "Item not found"})

    item.qty += change

    if item.qty < 1:
        item.qty = 1

    item.save()
    print("UPDATE CART HIT")
    return JsonResponse({"success": True, "qty": item.qty})

@login_required
def wishlist_sidebar(request):
    cart = request.session.get("cart", {})
    items = []
    total_price = Decimal("0.00")

    for pid, item in cart.items():
        product = Product.objects.get(id=int(pid))
        qty = item["qty"]
        total_price += product.price * qty
        items.append({
            "product": product,
            "qty": qty,
        })

    return render(request, "website/sidebar_wishlist.html", {"items": items,"total_price": total_price,})

@login_required
def remove_wishlist_item(request, product_id):
    # Get the wishlist from session
    wishlist = request.session.get("wishlist", {})

    # Remove the item if it exists
    if str(product_id) in wishlist:
        del wishlist[str(product_id)]

    # Save back to session
    request.session["wishlist"] = wishlist
    request.session.modified = True

    # Recalculate total price
    total_price = 0
    for pid, item in wishlist.items():
        try:
            product = Product.objects.get(id=int(pid))
            total_price += product.price * item.get("qty", 1)
        except Product.DoesNotExist:
            continue  # skip if product was deleted from DB

    # Return success response with updated total
    return JsonResponse({
        "success": True,
        "total_price": total_price
    })


@login_required
def sidebar_profile(request):
    return render(request, "website/sidebar_profile.html")

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    total = sum(
        product.price * cart[str(product.id)]['qty']
        for product in products
    )

    if request.method == "POST":
        order = Order.objects.create(
            user=request.user,
            total_amount=total,
            status="PENDING"
        )

        for product in products:
            OrderItem.objects.create(
                order=order,
                product=product,
                farmer=product.farmer,   # ✅ FIX IS HERE
                qty=cart[str(product.id)]['qty'],
                price=product.price
            )

        request.session['cart'] = {}  # clear cart
        return redirect('payment', order_id=order.id)

    return render(request, 'website/checkout.html', {
        'products': products,
        'cart': cart,
        'total': total
    })


from django.http import JsonResponse

def update_cart_qty(request):
    if request.method == "POST":
        product_id = str(request.POST.get("product_id"))
        change = int(request.POST.get("change"))

        cart = request.session.get("cart", {})

        if product_id in cart:
            cart[product_id]["qty"] += change

            if cart[product_id]["qty"] <= 0:
                del cart[product_id]

        request.session["cart"] = cart
        request.session.modified = True

        return JsonResponse({"success": True})

    return JsonResponse({"success": False})

# =========================
# FARMER ORDERS
# =========================
@login_required
def farmer_orders(request):
    farmer = request.user

    order_items = OrderItem.objects.filter(farmer=farmer)

    total_revenue = order_items.aggregate(
        total=Sum(F('price') * F('qty'))
    )['total'] or 0

    return render(request, 'website/farmer_orders.html', {
        'order_items': order_items,
        'total_revenue': total_revenue
    })


def contact(request):
    if request.method == "POST":
        Contact.objects.create(
            name=request.POST.get("name"),
            email=request.POST.get("email"),
            subject=request.POST.get("subject"),
            message=request.POST.get("message")
        )

        messages.success(request, "Message sent successfully!")
        return redirect("contact")

    return render(request, "website/contact.html")

@login_required
def payment(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == "POST":
        order.status = "PAID"
        order.save()
        return redirect('track_order')

    return render(request, 'website/payment.html', {
        'order': order
    })

@login_required
def payment_success(request, order_id):
    order = get_object_or_404(Order, order_id=order_id)

    if order.status != "CONFIRMED":
        order.status = "CONFIRMED"
        order.save()

        pdf_buffer = generate_invoice_pdf(order)
        send_order_email(order, pdf_buffer)

        request.session['cart'] = {}
        request.session.modified = True

    return render(request, "website/payment_success.html", {"order": order})

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "website/my_orders.html", {"orders": orders})

def place_order(request):
    cart = request.session.get('cart', {})

    order = Order.objects.create(
        user=request.user,
        is_paid=True
    )

    for pid, item in cart.items():
        product = Product.objects.get(id=pid)

        OrderItem.objects.create(
            order=order,
            product=product,
            farmer=product.farmer,
            quantity=item['quantity'],
            price=product.price
        )

    request.session['cart'] = {}
    return redirect('order_success')
