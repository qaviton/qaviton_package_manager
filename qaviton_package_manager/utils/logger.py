import logging


# create logger
log = logging.getLogger('qaviton_package_manager')
log.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s:{%(levelname)s}:%(message)s')

# create console handler
handler = logging.StreamHandler()
# set handler log level
handler.setLevel(logging.DEBUG)
# set handler formatter
handler.setFormatter(formatter)
# add handler to logger
log.addHandler(handler)
