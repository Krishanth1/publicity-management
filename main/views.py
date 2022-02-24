from django.shortcuts import render, redirect
from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.db.models.query_utils import Q
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.contrib import messages
from .models import Product, Article, Tag
from django.core.paginator import Paginator
from .forms import NewUserForm, UserForm, ProfileForm, VoteForm
from django.contrib.auth import login, authenticate, logout
# from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.
def password_reset_request(request):
	if request.method == "POST":
		password_reset_form = PasswordResetForm(request.POST)
		if password_reset_form.is_valid():
			data = password_reset_form.cleaned_data['email']
			associated_users = User.objects.filter(Q(email=data))
			if associated_users.exists():
				for user in associated_users:
					subject = "Password Reset Requested"
					email_template_name = "main/password/password_reset_email.txt"
					c = {
					"email":user.email,
					'domain':'airquill.pythonanywhere.com',
					'site_name': 'Droid serv',
					"uid": urlsafe_base64_encode(force_bytes(user.pk)),
					'token': default_token_generator.make_token(user),
					'protocol': 'https',
					}
					email = render_to_string(email_template_name, c)
					try:
						send_mail(subject, email, 'airquillla@gmail.com', [user.email], fail_silently=False)
					except BadHeaderError:

						return HttpResponse('Invalid header found.')

					messages.success(request, 'A message with reset password instructions has been sent to your inbox.')
					return redirect ("main:homepage")
			messages.error(request, 'An invalid email has been entered.')
	password_reset_form = PasswordResetForm()
	return render(request=request, template_name="main/password/password_reset.html", context={"password_reset_form":password_reset_form})

def homepage(request):
	if request.method == "POST":
		product_id = request.POST.get('product_pk')
		product = Product.objects.get(id = product_id)
		request.user.profile.products.add(product)
		messages.success(request,(f'{product} added to wishlist.'))
		return redirect ('main:homepage')
	product = Product.objects.all()[:4]
	new_posts = Article.objects.all().order_by('-article_published')[:4]
	featured = Article.objects.filter(article_tags__tag_name='Featured')[:3]
	most_recent = new_posts.first()
	return render(request=request, template_name="main/home.html", context={'product':product, 'most_recent':most_recent, "new_posts":new_posts, "featured":featured})

def products(request):
	if request.method == "POST":
		if "score_submit" in request.POST:
			vote_form = VoteForm(request.POST)
			if vote_form.is_valid():
				form = vote_form.save(commit=False)
				form.profile = request.user.profile
				product_id = request.POST.get("product")
				form.product = Product.objects.get(id=product_id)
				form.save()
				form.calculate_averages()  #add this
				messages.success(request,(f'{form.product} product score submitted.'))
				return redirect ("main:products")
			messages.error(request,('Form is invalid.'))
			return redirect ("main:products")
		product_id = request.POST.get("product_pk")
		product = Product.objects.get(id = product_id)
		request.user.profile.products.add(product)
		messages.success(request,(f'{product} added to wishlist.'))
		return redirect ('main:products')
	product = Product.objects.all()
	paginator = Paginator(product, 18)
	page_number = request.GET.get('page')
	page_obj = paginator.get_page(page_number)
	vote_form = VoteForm()
	return render(request = request, template_name="main/products.html", context = {"product":product, "page_obj":page_obj, "vote_form":vote_form})

def register(request):
	if request.method == "POST":
		form = NewUserForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("main:homepage")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = NewUserForm
	return render (request=request, template_name="main/register.html", context={"form":form})

def login_request(request):
	if request.method == "POST":
		form = AuthenticationForm(request, data=request.POST)
		if form.is_valid():
			username = form.cleaned_data.get('username')
			password = form.cleaned_data.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				login(request, user)
				messages.info(request, f"You are now logged in as {username}.")
				return redirect("main:homepage")
			else:
				messages.error(request,"Invalid username or password.")
		else:
			messages.error(request,"Invalid username or password.")
	form = AuthenticationForm()
	return render(request=request, template_name="main/login.html", context={"form":form})

def logout_request(request):
	logout(request)
	messages.info(request, "You have successfully logged out.")
	return redirect("main:homepage")

def blog(request, tag_page):
	if tag_page == 'articles':
		tag =''
		blog = Article.objects.all().order_by('-article_published')
	else:
		tag = Tag.objects.get(tag_slug=tag_page)
		blog = Article.objects.filter(article_tags=tag).order_by('-article_published')
	paginator = Paginator(blog, 25)
	page_number = request.GET.get('page')
	blog_obj = paginator.get_page(page_number)
	return render(request=request, template_name="main/blog.html", context={"blog":blog_obj, "tag":tag})

def article(request, article_page):
    article = Article.objects.get(article_slug=article_page)
    return render(request=request, template_name='main/article.html', context={"article": article})

def userpage(request):
	if request.method == "POST":
		user_form = UserForm(request.POST, instance=request.user)
		profile_form = ProfileForm(request.POST, instance=request.user.profile)
		if user_form.is_valid():
		    user_form.save()
		    messages.success(request,('Your profile was successfully updated!'))
		elif profile_form.is_valid():
		    profile_form.save()
		    messages.success(request,('Your wishlist was successfully updated!'))
		else:
		    messages.error(request,('Please correct the error below.'))
		return redirect ("main:userpage")
	user_form = UserForm(instance=request.user)
	profile_form = ProfileForm(instance=request.user.profile)
	return render(request = request, template_name ="main/user.html", context = {"user":request.user,
		"user_form": user_form, "profile_form": profile_form })




