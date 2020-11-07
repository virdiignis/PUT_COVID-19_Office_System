DATE_INPUT_FORMATS = [
    '%d.%m.%Y', '%d.%m.%y'  # '25.10.2006', '25.10.06'
]

TIME_INPUT_FORMATS = [
    '%H:%M:%S',  # '14:30:59'
    '%H:%M:%S.%f',  # '14:30:59.000200'
    '%H:%M:%S:%f',  # '14:30:59:000200'
    '%H:%M',  # '14:30'
]

DATETIME_INPUT_FORMATS = [
    '%d.%m.%Y %H:%M:%S',
    '%d.%m.%Y %H:%M:%S.%f',
    '%d.%m.%Y %H:%M:%S:%f',
    '%d.%m.%y %H:%M:%S',
    '%d.%m.%y %H:%M:%S.%f',
    '%d.%m.%y %H:%M:%S:%f',
]
