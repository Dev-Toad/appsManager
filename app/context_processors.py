from flask_login import current_user


def inject_user_data():
    if current_user.is_authenticated:
        display_name = current_user.full_name or current_user.username
    else:
        display_name = None

    return dict(current_user_name=display_name)
