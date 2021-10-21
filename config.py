import os
basedir = os.path.abspath(os.path.dirname(__file__))

class ProductionConfig():
    PROD_URI = os.getenv("PROD_URI")

