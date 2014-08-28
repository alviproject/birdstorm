from game.utils.config import config


def analytics(_):
    return dict(
        UA=config.ANALYTICS_UA,
    )