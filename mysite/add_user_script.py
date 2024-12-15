## run py manage.py shell then copy and paste this below to add a new admin user


from django.contrib.auth.models import User, Permission

# Replace 'zaid' with the actual username of the user you want to grant admin permissions
username = 'zaid'

try:
    user = User.objects.get(username=username)
    permission = Permission.objects.get(codename='is_admin')
    user.user_permissions.add(permission)
    print(f"Added 'Is Admin' permission to user: {username}")
except User.DoesNotExist:
    print(f"User with username '{username}' does not exist.")
except Permission.DoesNotExist:
    print("Permission 'is_admin' does not exist.")
