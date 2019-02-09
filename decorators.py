from django.contrib.auth.decorators import user_passes_test

def group_required(*group_names):
    """
     Requires user membership in at least one of the groups passed in, or is_superuser or is_staff

    Example: @group_required('admins','engineers')

    :param group_names: allowable groups
    :return: boolean
    """
    def in_groups(u):
        if u.is_authenticated and (u.is_staff | u.is_superuser | u.groups.filter(name__in=group_names).exists()):
            return True
        else:
            return False
    return user_passes_test(in_groups)
