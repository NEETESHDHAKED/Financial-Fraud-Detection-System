from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
import joblib, os, pandas as pd
from.models import Prediction
import pathlib
import random

BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "fraud_model.pkl"

if  not MODEL_PATH.exists():
   MODEL_PATH = BASE_DIR / "detector" / "fraud_model.pkl"
def get_model():
    return joblib.load(MODEL_PATH)

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if not User.objects.filter(username=username).exists():
         user = User.objects.create_user(username=username, password=password)
         return redirect('login')
    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user :
            login(request, user)
            return redirect('home')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def home(request):
    result = None
    risk = 0
    status = ""
    if request.method == 'POST':
     try:
        amount = float(request.POST.get('amount', 0))
        if amount > 15000:
           risk = 98.75
           prob = 0.9875
           result = "Fraud"
           status = "Transaction Blocked"
           return render(request, 'home.html', {'risk': risk, 'result': result, 'status': status, 'amount': amount, 'prob': prob})
        elif amount > 2000 and amount <= 15000:
            otp = random.randint(100000,999999)
            request.session['real_otp'] = otp
            print(f"*** Your OTP IS: {otp}***")
            return render(request, 'otp.html', {'otp': otp, 'amount': amount})
        else:
            prob = 0.02
            risk = 2.0
            result = "Safe"
            status = "Transaction Approved"
        
          
        Prediction.objects.create(user=request.user, amount=amount, risk_score=prob, result=result)
     except Exception as e:
        result = f"Error: {str(e)}"
    return render(request, 'home.html', {'risk': risk, 'result': result, 'status': status})

@login_required
def history_view(request):
    rows = Prediction.objects.filter(user=request.user).order_by('-id')[:20]
    return render(request, 'history.html', {'rows': rows})

def verify_otp(request):
    if request.method == 'POST':
        user_otp = request.POST.get('otp')
        real_otp = request.session.get('real_otp')  
        if user_otp == str(real_otp):
            del request.session['real_otp'] 
            return render(request, 'home.html', {'result': 'Safe', 'status': 'Payment Successful - OTP Verified', 'risk': 2.0})
        else:
            import random
            new_otp = random.randint(100000, 999999)
            request.session['real_otp'] = new_otp
            print(f"*** Your New OTP IS: {new_otp}***")
            return render(request, 'otp.html', {'otp': new_otp})
    return redirect('home')
