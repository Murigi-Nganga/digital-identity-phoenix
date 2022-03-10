import os
from uuid import uuid4
from .uploads.handle_file import upload
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from .models import Customers
from .biometrics.voice_auth import enroll as enroll_voice
from .biometrics.face_auth import verify as verify_face
from .biometrics.fingerprint_auth import verify as verify_fingerprint
from .biometrics.voice_auth import verify as verify_voice
from .biometrics.signature_auth import verify as verify_signature
from os.path import dirname

# Azure storage blob containers
container_names = ['photos', 'recordings', 'signatures', 'fingerprints']

check_path = dirname(dirname( __file__ ))

def enroll(request):
    if not request.user.is_authenticated:
        return redirect(to='login')
    
    cutomer_files_urls = []
    new_image_names = []
    messages = []
    
    if request.method == 'POST':
        m=0
        fs = FileSystemStorage()
        for item in request.FILES.items():
            myfile = request.FILES.get(item[0])
            
            image_name = str(str(uuid4())[:10] + '.' + myfile.name.split('.')[-1])
            new_image_names.append(image_name)
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            cutomer_files_urls.append(uploaded_file_url)
            
            if m != 1:
                upload(container_names[m], str(check_path + cutomer_files_urls[m]) , str(image_name))
                
            m += 1
            
            eq_customer_id = str(uuid4())
        
        if Customers.objects.create(
            customer_id = eq_customer_id,
            first_name = request.POST.get('first_name'),
            last_name = request.POST.get('last_name'),
            customer_photo = new_image_names[0],
            customer_recording = enroll_voice(check_path + '\\' + cutomer_files_urls[1])[1],
            customer_signature =  new_image_names[2],
            customer_fingerprint = new_image_names[3],
        ):
            messages.append(f'Customer Enrolled Successfully!\
                             Customer\'s ID Number is {eq_customer_id}')
        else:
            messages.append(f'Something went wrong. Please retry the enrollment!')
        
    return render(request, 'enroll.html', {'messages': messages})

def verify(request):
    if not request.user.is_authenticated:
        return redirect(to='login')
    
    customer_verify_urls = []
    messages = []
    
    if request.method == 'POST':
        fs = FileSystemStorage()
        for item in request.FILES.items():
            myfile = request.FILES.get(item[0])
            filename = fs.save(myfile.name, myfile)
            uploaded_file_url = fs.url(filename)
            customer_verify_urls.append(str(check_path + uploaded_file_url))
            
        customer_data = Customers.objects.get(pk=request.POST.get('customer_id'))
        if not customer_data:
            messages.warning(request, f"The Customer with the ID {request.POST.get('customer_id')} does not exist!")
        # print(customer_data)
        
        customer_photo = customer_data.customer_photo
        customer_recording = customer_data.customer_recording
        customer_fingerprint = customer_data.customer_fingerprint
        customer_signature = customer_data.customer_signature
        
        has_passed = [
            # face_verification
            verify_face(customer_photo, customer_verify_urls[0])[0],
            
            # voice_verification
            verify_voice(customer_recording, customer_verify_urls[1])[0],
            
            # signature
            verify_signature(customer_signature, customer_verify_urls[2])[0],
        
            # fingerprint
            verify_fingerprint(customer_fingerprint, customer_verify_urls[3])[0]
        ]
            
        if has_passed == [True, True, True, True]:
            messages.append('Verification successful. A match was found!')
            messages.append(f'Name: {customer_data.first_name} {customer_data.last_name}')
        else:
            messages.append('Verification was unsuccessful!')
            messages.append('No match was found!')
            
    return render(request, 'verify.html', {'messages': messages})