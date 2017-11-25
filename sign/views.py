from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from sign.models import Event, Guest
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

# 定义函数 index -
def index(request):
    # 通过 HttpResponse 类向客户端（浏览器）返回字符串“Hello Django!”
    # return HttpResponse("Hello Django!")
    # 使用Django的render函数 - request为请求对象，“index.html”为返回客户端的HTML页面。
    return render(request, "index.html")


# 登录动作
def login_action(request):
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)  # 登录
            response = HttpResponseRedirect('/event_manage/')
            request.session['user'] = username  # 将session 信息记录到浏览器
            return response
        else:
            return render(request, 'index.html', {'error': 'username or password error!'})


'''
        if username == 'admin' and password == 'admin':
            # return HttpResponse('login success!')
            # HttpResponseRedirect 对路径进行重定向，从而将登录成功之后的请求指向/event_manage/目录。
            # return HttpResponseRedirect("/event_manage/")
            response = HttpResponseRedirect('/event_manage/')
            # response.set_cookie('user', username, 3600)   # 添加浏览器cookie
            request.session['user'] = username  # 将session 信息记录到浏览器
            return response
        else:
            return render(request, 'index.html', {'error': 'username or password error!'})
    else:
        return render(request, 'index.html', {'error': 'username or password error!'})
'''


# 发布会管理
@login_required()
def event_manage(request):
    # username = request.COOKIES.get('user', '')   # 读取浏览器 cookie
    # print(username)
    event_list = Event.objects.all()
    username = request.session.get('user', '')  # 读取浏览器session
    return render(request, 'event_manage.html', {"user": username, "events": event_list})  # {"user": username} 把username赋值给user

# 发布会名称搜索
@login_required()
def search_name(request):
    username = request.session.get('user', '')
    search_name = request.GET.get("name", "")
    event_list = Event.objects.filter(name__contains = search_name)
    return render(request, "event_manage.html", {"user":username, "events":event_list})

# 嘉宾管理
@login_required
def guest_manage(request):
    username = request.session.get('user', '')
    guest_list = Guest.objects.all()
    paginator = Paginator(guest_list, 2)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range(e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, "guest_manage.html", {"user":username, "guests":contacts})

# 签到页面
@login_required
def sign_index(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    return render(request, 'sign_index.html', {'event': event})

# 签到动作
@login_required
def sign_index_action(request, eid):
    event = get_object_or_404(Event, id=eid)
    phone = request.POST.get('phone', '')
    print(phone)

    result = Guest.objects.filter(phone=phone)
    if not result:
        return render(request, 'sign_index.html', {'event': event, 'hint': 'phone error.'})

    result = Guest.objects.filter(phone=phone, event_id=eid)
    if not result:
        return render(request, 'sign_index.html', {'event': event, 'hint': 'event_id or phone error.'})

    # assert isinstance(eid, object)
    result = Guest.objects.get(phone=phone, event_id=eid)
    if result.sign:
        return render(request, 'sign_index.html', {'event': event, 'hint': 'user has sign in.'})
    else:
        Guest.objects.filter(phone=phone, event_id=eid).update(sign='1')
        return  render(request, 'sign_index.html', {'event': event, 'hint': 'sign in success.', 'guest': result})

# 退出登录
@login_required
def logout(request):
    auth.logout(request)    # 退出登录
    response = HttpResponseRedirect('/index/')
    return response