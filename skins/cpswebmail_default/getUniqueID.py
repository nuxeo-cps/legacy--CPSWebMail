#parameters=

from DateTime import DateTime
from random import randint

return str((DateTime().millis() * 10) + randint(0,9999))
