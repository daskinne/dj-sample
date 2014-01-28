from storages.backends.s3boto import S3BotoStorage

UserRootS3BotoStorage = lambda: S3BotoStorage(location='static')