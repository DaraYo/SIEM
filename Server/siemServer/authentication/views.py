from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils import timezone
from datetime import datetime,timedelta
from .models import Attempts

# Create your views here.
def predfLogin(request):
    now= timezone.now()
    username = request.POST.get('username') or ""
    password = request.POST.get('password') or ""
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        try:
            last_attempt = Attempts.objects.get(uname=username)
        except:
            last_attempt= None
        print(last_attempt)
        if last_attempt is not None and last_attempt.blockDate is not None and last_attempt.blockDate>=now:
            return render(request, 'registration/login.html', {'errors': "Try again in few minutes"})
        else:
            user2 = authenticate(request, username=username, password=password)
            if user2 is not None:
                login(request, user2)
                print(user2)
                if last_attempt is not None:
                    last_attempt.counter=0
                    last_attempt.blockDate= None
                    last_attempt.save()
                return redirect('/api/allAlarms')
            else:
                if last_attempt is None:
                    last_attempt= Attempts.objects.create(counter=1, lastAttempt= now, uname= user.username)
                    last_attempt.save()
                else:
                    nowLess= now- timedelta(minutes=5)
                    la= last_attempt.lastAttempt
                    if last_attempt.lastAttempt>=nowLess:
                        last_attempt.counter+=1
                        last_attempt.save()
                    else:
                        last_attempt.counter=1
                        last_attempt.save()
                if last_attempt.counter==5:
                    last_attempt.blockDate= now+ timedelta(minutes=5)
                last_attempt.lastAttempt= now
                last_attempt.save()
                return render(request, 'registration/login.html', {'errors': "Wrong username or password"})

    return render(request, 'registration/login.html', {'errors': "Wrong username or password"})