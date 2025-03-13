# import base64
# import json
# import os
# from io import BytesIO

# import face_recognition
# from django.conf import settings
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
# from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
# from django.templatetags.static import static
# from PIL import Image, ImageDraw, ImageFont

from .models import Face, User


# @login_required
# def index(request):
#     if request.method == "POST":
#         known_faces = Face.objects.filter(user=request.user)
#         known_face_encodings = []
#         known_face_names = []

#         for face in known_faces:
#             image_of_known_person = face_recognition.load_image_file(
#                 f"media/{face.face}"
#             )
#             known_person_encoding = face_recognition.face_encodings(
#                 image_of_known_person
#             )[0]

#             known_face_encodings.append(known_person_encoding)
#             known_face_names.append(face.name)

#         image = face_recognition.load_image_file(request.FILES["image"])

#         # Find faces in test image
#         face_locations = face_recognition.face_locations(image)
#         face_encodings = face_recognition.face_encodings(image, face_locations)

#         # Convert to PIL format
#         pil_image = Image.fromarray(image)

#         # Create a ImageDraw instance
#         draw = ImageDraw.Draw(pil_image)

#         # Loop through faces in image
#         for (top, right, bottom, left), face_encoding in zip(
#             face_locations, face_encodings
#         ):
#             matches = face_recognition.compare_faces(
#                 known_face_encodings, face_encoding
#             )

#             name = "Unknown Person"

#             # If match
#             if True in matches:
#                 first_match_index = matches.index(True)
#                 name = known_face_names[first_match_index]

#             # Draw box around face
#             draw.rectangle(((left, top), (right, bottom)), outline=(255, 0, 0))

#             # Draw label
#             font_path = os.path.join(settings.BASE_DIR, 'djangoface', 'static', 'djangoface', 'Oswald-Regular.ttf')
#             print(font_path)
            
#             font = ImageFont.truetype(font_path, 20)

#             # Change font size of font 
#             ascent, descent = font.getmetrics()
#             text_width = font.getmask(name).getbbox()[2]
#             text_height = font.getmask(name).getbbox()[3] + descent

#             # # Draw the text inside the box
#             draw.text((left, bottom - text_height), name, font=font, fill=(255, 0, 0, 255))
#         del draw

#         # Convert PIL image to bytes
#         buffered = BytesIO()
#         pil_image.save(buffered, format="JPEG")
#         img_bytes = buffered.getvalue()

#         # Encode image bytes to base64
#         img_base64 = base64.b64encode(img_bytes).decode("utf-8")

#         # Return image as base64 encoded string
#         return HttpResponse(
#             json.dumps({"image": img_base64}), content_type="application/json"
#         )

#     return render(request, "djangoface/index.html")


# @login_required
# def faces(request):
#     query = request.GET.get("q")

#     if request.method == "POST":
#         name = request.POST["name"]
#         image = request.FILES["image"]

#         Face.objects.create(user=request.user, name=name, face=image)

#         # Create new face
#         print(name)

#     if query:
#         faces = Face.objects.filter(user=request.user, name__icontains=query).order_by(
#             "name"
#         )
#     else:
#         faces = Face.objects.filter(user=request.user).order_by("name")

#     return render(request, "djangoface/faces.html", {"faces": faces})

import base64
import json
import os
from io import BytesIO

import face_recognition
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from PIL import Image, ImageDraw, ImageFont
import numpy as np

from .models import Face

from django.http import HttpResponseRedirect

@login_required
def index(request):
    if request.method == "POST":
        known_faces = Face.objects.filter(user=request.user)
        known_face_encodings = []
        known_face_names = []

        for face in known_faces:
            image_of_known_person = face_recognition.load_image_file(
                f"media/{face.face}"
            )
            known_person_encoding = face_recognition.face_encodings(
                image_of_known_person
            )[0]

            known_face_encodings.append(known_person_encoding)
            known_face_names.append(face.name)

        image = face_recognition.load_image_file(request.FILES["image"])

        # Find faces in test image
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        # Convert to PIL format
        pil_image = Image.fromarray(image)

        # Create an ImageDraw instance
        draw = ImageDraw.Draw(pil_image)

        # Font settings
        font_path = os.path.join(
            settings.BASE_DIR, "djangoface", "static", "djangoface", "Oswald-Regular.ttf"
        )
        font = ImageFont.truetype(font_path, 20)

        # Loop through faces in image
        for (top, right, bottom, left), face_encoding in zip(
            face_locations, face_encodings
        ):
            matches = face_recognition.compare_faces(
                known_face_encodings, face_encoding
            )
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            name = "Unknown Person"
            similarity = 0

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)  # Get best match
                if matches[best_match_index]:  # Check if it's a real match
                    name = known_face_names[best_match_index]
                    similarity = (1 - face_distances[best_match_index]) * 100  # Convert to percentage

            # Draw box around face
            draw.rectangle(((left, top), (right, bottom)), outline=(255, 0, 0), width=3)

            # Prepare label text
            label = f"{name} ({similarity:.2f}%)"

            # Get text size (fixed for Pillow 10+)
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]

            # Draw background rectangle for text
            draw.rectangle(
                [(left, bottom - text_height - 5), (left + text_width + 10, bottom)],
                fill=(255, 0, 0),
            )

            # Draw label text
            draw.text((left + 5, bottom - text_height - 3), label, font=font, fill=(255, 255, 255, 255))

        del draw

        # Convert PIL image to bytes
        buffered = BytesIO()
        pil_image.save(buffered, format="JPEG")
        img_bytes = buffered.getvalue()

        # Encode image bytes to base64
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")

        return HttpResponse(
            json.dumps({"image": img_base64}), content_type="application/json"
        )

    return render(request, "djangoface/index.html")


@login_required
def faces(request):
    query = request.GET.get("q")

    if request.method == "POST":
        name = request.POST["name"]
        image = request.FILES["image"]

        Face.objects.create(user=request.user, name=name, face=image)

    if query:
        faces = Face.objects.filter(user=request.user, name__icontains=query).order_by("name")
    else:
        faces = Face.objects.filter(user=request.user).order_by("name")

    return render(request, "djangoface/faces.html", {"faces": faces})

@login_required
def delete_face(request, id):
    face = Face.objects.filter(pk=id).first()

    if request.user == face.user:
        face.delete()

    return HttpResponseRedirect(reverse("faces"))
from django.contrib.auth import logout,authenticate,login


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(
                request,
                "djangoface/login.html",
                {"message": "Invalid username and/or password."},
            )
    else:
        return render(request, "djangoface/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(
                request,
                "djangoface/register.html",
                {"message": "Passwords must match."},
            )

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(
                request,
                "djangoface/register.html",
                {"message": "Username already taken."},
            )
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "djangoface/register.html")
    
def mypage(request):
    return render(request, "djangoface/mypage.html")


def about(request):
    return render(request,'djangoface/about.html')

def contact(request):
    return render(request,'djangoface\contact.html')
import base64
from io import BytesIO
import face_recognition
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from PIL import Image, ImageDraw

@csrf_exempt  # ⚠️ For testing only. Use CSRF token in production.
def capture_image(request):
    if request.method == "POST":
        try:
            image_data = request.POST.get("image")  # Get base64 image

            if not image_data:
                return JsonResponse({"error": "No image data received"}, status=400)

            # Decode base64 image
            format, imgstr = image_data.split(";base64,")  
            image_bytes = base64.b64decode(imgstr)

            # Load image with PIL
            pil_image = Image.open(BytesIO(image_bytes))

            # Convert PIL image to numpy array for face detection
            image = face_recognition.load_image_file(BytesIO(image_bytes))

            # Detect faces
            face_locations = face_recognition.face_locations(image)

            if not face_locations:
                return JsonResponse({"message": "No face found.", "faces_detected": 0})

            cropped_faces = []
            
            # Loop through detected faces and crop them
            for (top, right, bottom, left) in face_locations:
                face = pil_image.crop((left, top, right, bottom))  # Crop face

                # Convert cropped face to base64
                buffered = BytesIO()
                face.save(buffered, format="JPEG")
                img_base64 = base64.b64encode(buffered.getvalue()).decode()

                cropped_faces.append(img_base64)

            return JsonResponse({
                "message": "Face detected!",
                "faces_detected": len(face_locations),
                "faces": cropped_faces  # Return list of cropped face images
            })

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    return render(request, "djangoface/upload.html")
