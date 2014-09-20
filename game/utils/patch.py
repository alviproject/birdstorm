import rest_framework.fields


def strip_multiple_choice_msg(_):
    return ''

rest_framework.fields.strip_multiple_choice_msg = strip_multiple_choice_msg