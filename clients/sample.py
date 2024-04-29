# import requests
# from urllib.parse import urlparse, parse_qs
# from models import Client, ScormAsset, ClientUser, UserScormMapping

# # Parse the URL
# url = "https://xxxxx.com/v1/course_enrollments/play?id=ID&learner_id=LEARNER_ID&name=LEARNER_FNAME&referringurl=REFERRING_URL"
# parsed_url = urlparse(url)
# params = parse_qs(parsed_url.query)

# # Get the parameters
# referringurl = params['referringurl'][0]
# ID = params['id'][0]
# learner_id = params['learner_id'][0]

# # Parse the domain from the referringurl
# domain = urlparse(referringurl).netloc

# # Check if a Client object with that domain exists in the database
# client = Client.objects.filter(domain=domain).first()
# if not client:
#     return "Error: No client with this domain"

# # Decrypt the ID to get the client id
# client_id = decrypt(ID)

# # Check if a Client object with the decrypted id exists in the database
# client = Client.objects.filter(id=client_id).first()
# if not client:
#     return "Error: No client with this ID"

# # Check if a ScormAsset object with the scorm_id exists and is mapped to the Client object
# scorm_asset = ScormAsset.objects.filter(client=client).first()
# if not scorm_asset:
#     return "Error: No SCORM asset for this client"

# # Check the access period and remaining license count for the ScormAsset
# if not scorm_asset.within_access_period() or scorm_asset.remaining_license_count() <= 0:
#     return "Error: Access period is over or no remaining licenses"

# # Check if a ClientUser object with the learner_id exists and is mapped to the Client object
# client_user = ClientUser.objects.filter(id=learner_id, client=client).first()
# if not client_user:
#     # Create a new ClientUser object and save it to the database
#     client_user = ClientUser.objects.create(id=learner_id, client=client)

#     # Register the user
#     signup_url = "https://cloudscorm.cloudnuv.com/user/signup"
#     signup_data = {
#         "email": client_user.email,  # replace with the actual email
#         "website": client.domain,  # replace with the actual website
#         "website_user_id": client_user.id,  # replace with the actual website user id
#     }
#     signup_response = requests.post(signup_url, data=signup_data)
#     if signup_response.status_code != 200:
#         return "Error: Failed to register user"

#     # Call the SCORM API with the learner_id and insert the returned scorm_user_id into the scorm_user_id field of the ClientUser object
#     scorm_user_id = call_scorm_api(learner_id)
#     client_user.scorm_user_id = scorm_user_id
#     client_user.save()

# # Check if a UserScormMapping object exists with the scorm_id and user_id
# user_scorm_mapping = UserScormMapping.objects.filter(scorm_id=scorm_asset.id, user_id=client_user.id).first()
# if not user_scorm_mapping:
#     # Create a new UserScormMapping object and save it to the database
#     UserScormMapping.objects.create(scorm_id=scorm_asset.id, user_id=client_user.id)

# # Construct the SCORM course URL using the scorm_id and scorm_user_id
# launch_url = f"https://cloudscorm.cloudnuv.com/course/{scorm_asset.id}/{client_user.scorm_user_id}/online/0-0-0-0-0"

# # Redirect the user to the SCORM course URL
# window.location.href = launch_url
