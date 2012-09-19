from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.http import  HttpResponseRedirect

from telepresence.core.forms import LoginForm

def index(request):
    return render_to_response('index.html', {
    }, context_instance=RequestContext(request))

def about(request):
    return render_to_response('about.html', {
    }, context_instance=RequestContext(request))

def login_user(request, template='index.html', redirect_url=None):

    def handle_login_error(login_error):
        form = LoginForm()
        return render_to_response(template, {
            'login_error' : login_error,
            'login_form' : form,
        }, context_instance=RequestContext(request))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            redirect_url = redirect_url or form.cleaned_data.get('redirect_url')
            user = authenticate(username=username, password=password)
            if user is not None:
                if user.is_active:
                    # Redirect to a success page.
                    login(request, user)
                    if redirect_url:
                        return HttpResponseRedirect(redirect_url)
                    else:
                        return render_to_response(template, {
                            'login_succeeded': True
                        }, context_instance=RequestContext(request))
                else:
                    # Return a 'disabled account' error message
                    error = u'Account disabled'
            else:
                # Return an 'invalid login' error message.
                error = u'Invalid login'
        else:
            error = u'Login form is invalid'
        return handle_login_error(error)

    else:
        form = LoginForm() # An unbound form
        form.fields['redirect_url'].initial = request.GET.get('next', '/')
        return render_to_response(template, {
            'login_error': "You must first login",
            'form': form
        }, context_instance=RequestContext(request))

def logout_user(request):
    logout(request)
    return HttpResponseRedirect('/')
