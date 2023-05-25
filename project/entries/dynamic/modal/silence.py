def is_supported(context, **kwargs):
    try:
        assert context.energy >= 0
    except AssertionError:
        return False
    return True


def main(context, **kwargs):
    return
