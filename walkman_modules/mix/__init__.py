import walkman


class Space(walkman.Module):
    def _initialise(
        self, frequency: float = 200, envelope: str = "BASIC", *args, **kwargs
    ):
        super()._initialise(*args, **kwargs)

    def _play(self, *args, **kwargs):
        super()._play(*args, **kwargs)
