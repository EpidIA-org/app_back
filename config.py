import os

class Config:
    """Meta Configuration Class
    """
    ERROR_404_HELP = False

    SECRET_KEY = os.getenv('APP_SECRET', 'secret key')


class DevConfig(Config):
    """Development configiration Class

    Args:
        Config ([type]): [description]
    """
    DEBUG = True


class TestConfig(Config):
    """Test configuration Class

    Args:
        Config ([type]): [description]
    """
    TESTING = True
    DEBUG = True


class ProdConfig(Config):
    """Production configuration Class

    Args:
        Config ([type]): [description]
    """
    DEBUG = False


config = {
    'development': DevConfig,
    'testing': TestConfig,
    'production': ProdConfig
}