from pydantic.error_wrappers import ValidationError
from yaml import safe_load

from cptk.utils import cptkException


from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typing import Type, TypeVar
    from pydantic import BaseModel

    T = TypeVar('T', BaseModel)


class ConfigFileError(cptkException):
    """ Base cptkException for all errors thrown from the 'load_config_file'
    function, while trying to load a YAML configuration file. """


class ConfigFileNotFound(ConfigFileError, FileNotFoundError):
    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Can't find configuration file {path!r}")


class ConfigFileValueError(ConfigFileError, ValueError):

    def __init__(self, path: str, errors: dict) -> None:
        self.path = path
        self.errors = errors
        super().__init__(self.__generate_error_message())

    def __generate_error_message(self) -> str:
        er = 'error' if len(self.errors) == 1 else f'{len(self.errors)} errors'
        s = f"{er} found in {self.path!r}:"

        for error in self.errors:
            path = '.'.join(error['loc']) if error['loc'] else '.'
            s += f"\nUnder {path!r}: {error['msg']}"

        return s


def load_config_file(path: str, Model: 'Type[T]') -> 'T':
    """ Load information from a YAML configuration file and dump it into a
    pydantic Model. Raises relevent expections if the given file path isn't
    found, the YAML file can't be parsed, or the data doesn't match the pydantic
    model. """

    try:
        with open(path, 'r', encoding='utf8') as file:
            data = safe_load(file)

    except FileNotFoundError:
        raise ConfigFileNotFound(path)

    if not isinstance(data, dict):
        raise ConfigFileValueError(
            path, [{'loc': (), 'msg': "file isn't in dictionary format"}])

    try:
        return Model(**data)
    except ValidationError as e:
        raise ConfigFileValueError(path, e.errors()) from e
