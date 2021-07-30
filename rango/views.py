from django.shortcuts import render
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rango.models import Category
from rango.models import Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

# each function is a view
def index(request):
    # Query the database for a list of ALL categories currently stored.
    # Order the categories by the number of likes in descending order.
    # Retrieve the top 5 only -- or all if less than 5.
    # Place the list in our context_dict dictionary (with our boldmessage!) 
    # that will be passed to the template engine.
    category_list = Category.objects.order_by('-likes')[:5]
    # order the pages by the number of views in descending order.
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {}
    context_dict['boldmessage'] = 'Crunchy, creamy, cookie, candy, cupcake!'
    context_dict['categories'] = category_list
    # add pages list to the context_dict
    context_dict['pages'] = page_list 

    # Render the response and send it to the client. 
    # Note that the first parameter is the template we wish to use.
    return render(request, 'rango/index.html', context=context_dict)

def about(request):
    return render(request, 'rango/about.html')

def show_category(request, category_name_slug):
    # Create a context dictionary which we can pass to the template rendering engine.
    context_dict = {}

    try:
        # Can we find a category name slug with the given name?
        # If we can't, the .get() method raises a DoesNotExist exception.
        # The .get() method returns one model instance or raises an exception.
        category = Category.objects.get(slug=category_name_slug)

        # Retrieve all of the associated pages.
        # The filter() will return a list of page objects or an empty list.
        pages = Page.objects.filter(category=category)

        # Adds our results list to the template context under name pages.
        context_dict['pages'] = pages
        # We also add the category object from the database to the context dictionary.
        # We'll use this in the template to verify that the category exists.
        context_dict['category'] = category
    
    except  Category.DoesNotExist:
        # We get here if we didn't find the specified category.
        # Don't do anything, the template will display the "no category" message for us.
        context_dict['category'] = None
        context_dict['pages'] = None

    # Render the response and send it to the client. 
    return render(request, 'rango/category.html', context=context_dict)

@login_required
def add_category(request):
    form = CategoryForm()

    # A HTTP POST?
    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            # save the new category to the database.
            form.save(commit=True)
            # redirect the user back to the index view.
            return redirect(reverse('rango:index'))
        else:
            # The supplied form contained errors, print to the terminal
            print(form.errors)
    
    # Render the form with error messages (if any).
    return render(request, 'rango/add_category.html', {'form': form})

@login_required
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    # You cannot add a page to a Category that does not exist...
    if category is None:
        return redirect(reverse('rango:index'))

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()

                return redirect(reverse('rango:show_category', kwargs={'category_name_slug':category_name_slug}))
        
        else:
            print(form.errors)
    
    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context=context_dict)

def register(request):
    # A boolean value for telling the template whether the registration was successful.
    registered = False

    if request.method == 'POST':
        # Attempt to grab information from the raw form information.
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            # save the user's form data to the database.
            user = user_form.save()

            # Now we hash the password with the set_password method.
            user.set_password(user.password)
            user.save()

            # Since we need to set the user attribute ourselves, we set commit=False. 
            # This delays saving the model until we're ready to avoid integrity problems.
            profile = profile_form.save(commit=False)
            profile.user = user
            
            # If user proviede a profile picture, we need to get it from the input form 
            # and put it in the UserProfile model.
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            # Now we save the UserProfile model instance.
            profile.save()

            # Update our variable to indicate that the template registration was successful.
            registered = True
        else:
            # print problems to the terminal
            print(user_form.errors, profile_form.errors)
    else:
        # Not a HTTP POST, so we render our form using two ModelForm instances. 
        # These forms will be blank, ready for user input.
        user_form = UserForm()
        profile_form = UserProfileForm()
    
    # Render the template depending on the context.
    context_dict = {'user_form': user_form, 'profile_form': profile_form, 'registered': registered}
    return render(request, 'rango/register.html', context=context_dict)

def user_login(request):
    if request.method == 'POST':
        # Gather the username and password provided by the user.
        # This information is obtained from the login form.
        # We use request.POST.get('<variable>') as opposed to request.POST['<variable>'],
        username = request.POST.get('username')
        password = request.POST.get('password')

        # A User object is returned if username/password combination is valid.
        user = authenticate(username=username, password=password)

        # If we have a User object, the details are correct.
        # If None, no user # with matching credentials was found.
        if user:
            # Is the account active? It could have been disabled.
            if user.is_active:
                # log the user in, send the user back to the homepage
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                # no logging in
                return HttpResponse("Your Rango account is disabled.")
        else:
            # Bad login details were provided. So we can't log the user in.
            print(f"Invalid login details: {username}, {password}")
            return HttpResponse("Invalid login details supplied.")
    # The request is not a HTTP POST, so display the login form.
    # This scenario would most likely be a HTTP GET.
    else:
        # No context variables to pass to the template system, hence the blank dictionary object...
        return render(request, 'rango/login.html')

@login_required
def restricted(request):
    return render(request, 'rango/restricted.html')

# Use the login_required() decorator to ensure only those logged in can access the view.
@login_required
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))