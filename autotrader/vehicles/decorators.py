from django.shortcuts import redirect

def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('admin_user'):
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return wrapper
