import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

User = get_user_model()
user = User.objects.filter(username='sakkhar').first()

if not user:
    print("User 'sakkhar' not found.")
    sys.exit(1)

client = Client()
client.force_login(user)

response = client.get('/profile/')
print("STATUS CODE:", response.status_code)

output = response.content.decode('utf-8')
with open('debug_profile.html', 'w', encoding='utf-8') as f:
    f.write(output)

print("Saved rendered HTML to debug_profile.html.")

import re
matches = re.findall(r'\{\{.*?\}\}', output)
print("Any unrendered tags?", matches)
