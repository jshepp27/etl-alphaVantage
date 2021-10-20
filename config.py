import os
basedir = os.path.abspath(os.path.dirname(__file__))

class DevelopmentConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "default-key")
    DATABASE_URI = os.environ['DATABASE_URI']

class ProductionConfig(DevelopmentConfig):
    PROD_URI = "postgres://huylpljjnoshbe:b51e90b80991f8e32ed4399a04c6db2a837f803995392e79472d1b92110ac60b@ec2-34-250-16-127.eu-west-1.compute.amazonaws.com:5432/dc7g7o62up02ai"

# class StagingConfig(Config):
#     DEBUG = True
#
# class DevelopmentConfig(Config):
#     DEBUG = True
#     DEVELOPMENT = True

