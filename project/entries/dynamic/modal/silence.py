def is_supported(context, **kwargs):
    try:
        assert context.energy < 8
    except AssertionError:
        return False
    return True


def main(context, **kwargs):
    return
