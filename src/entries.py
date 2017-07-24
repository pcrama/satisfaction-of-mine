"Time entries are represented by the L{TimeEntry} class"

import attr

@attr.s
class TimeEntry(object):
    issue_id = attr.ib(validator=attr.validators.instance_of(str))
    duration = attr.ib()
    @duration.validator
    def _validate_duration(self, attribute, value):
        attr.validators.instance_of((int, float))(self, attribute, value)
        if value < 0:
            raise ValueError("'{name}' must be >= 0 and {value!r} isn't".format(
                name=attribute.name, value=value))
    category = attr.ib()
    @category.validator
    def _validate_category(self, attribute, value):
        attr.validators.instance_of(str)(self, attribute, value)
        if len(value.strip()) == 0:
            raise ValueError("'{name}' must be non-blank and {value!r} isn't".
                             format(name=attribute.name, value=value))
