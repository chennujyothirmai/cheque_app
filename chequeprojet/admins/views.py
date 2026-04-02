from django.shortcuts import render, redirect
from django.contrib import messages

# ================================
# ADMIN LOGIN VIEW
# ================================
def adminlogin(request):
    print("🔐 Admin login page accessed")

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        print("➡ Submitted Username:", username)
        print("➡ Submitted Password:", password)

        if username == "admin" and password == "admin":
            request.session['admin_logged_in'] = True
            messages.success(request, "Admin login successful!")
            print("✅ Admin authenticated")
            return redirect("adminhome")
        else:
            messages.error(request, "Invalid admin credentials!")
            print("❌ Invalid admin credentials")

    return render(request, "adminlogin.html")


# ================================
# ADMIN HOME VIEW
# ================================
def adminhome(request):
    print("🏠 Admin home accessed")

    if not request.session.get('admin_logged_in'):
        messages.warning(request, "Please login as admin first!")
        print("⚠ Unauthorized admin access")
        return redirect("adminlogin")

    return render(request, "adminhome.html")


# ================================
# ADMIN LOGOUT
# ================================
def adminlogout(request):
    print("🚪 Admin logout")

    request.session.flush()
    messages.success(request, "Admin logged out successfully!")
    return redirect("adminlogin")



from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from users.models import UserAccount


# ================================
# USERS LIST
# ================================
def admin_users_list(request):
    if not request.session.get('admin_logged_in'):
        messages.warning(request, "Admin login required!")
        return redirect('adminlogin')

    users = UserAccount.objects.all().order_by('-created_at')
    print("📋 Users fetched:", users.count())

    return render(request, "admin_users_list.html", {'users': users})


# ================================
# ACTIVATE USER
# ================================
def activate_user(request, user_id):
    user = get_object_or_404(UserAccount, id=user_id)
    user.status = 'activated'
    user.save()
    print(f"✅ User Activated: {user.username}")
    messages.success(request, f"{user.username} activated successfully!")
    return redirect('admin_users_list')


# ================================
# BLOCK USER
# ================================
def block_user(request, user_id):
    user = get_object_or_404(UserAccount, id=user_id)
    user.status = 'blocked'
    user.save()
    print(f"⛔ User Blocked: {user.username}")
    messages.warning(request, f"{user.username} blocked!")
    return redirect('admin_users_list')


# ================================
# UNBLOCK USER
# ================================
def unblock_user(request, user_id):
    user = get_object_or_404(UserAccount, id=user_id)
    user.status = 'activated'
    user.save()
    print(f"🔓 User Unblocked: {user.username}")
    messages.success(request, f"{user.username} unblocked!")
    return redirect('admin_users_list')


# ================================
# DELETE USER
# ================================
def delete_user(request, user_id):
    user = get_object_or_404(UserAccount, id=user_id)
    print(f"🗑 Deleting user: {user.username}")
    user.delete()
    messages.error(request, "User deleted permanently!")
    return redirect('admin_users_list')


