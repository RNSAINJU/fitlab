from loyalty.services import get_balance


def points_balance(request):
    if request.user.is_authenticated:
        return {"tfl_points_balance": get_balance(request.user)}
    return {"tfl_points_balance": 0}
