# NOTE: ConfigParser is pretty strict about its parsing -- I haven't found alternatives, except for writing our own.
import ConfigParser
import StringIO

import os


class ConfigManager(object):
    """OS agnostic class for fetching and saving the config.
    ALWAYS loads the config from the file system once upon instantiation of the class"""
    def __init__(self):
        # todo: implement windows platform.
        if os.name == "posix":
            self._driver = PosixDriver()
        else:
            raise NotImplementedError()
        self._driver.load_from_fs()

    def get_config(self, from_fs=False):
        if from_fs:
            self._driver.load_from_fs()
        return self._driver.config

    def save_config(self):
        self._driver.save_to_fs()

    def get_option(self, option):
        if option in self._driver:
            return self._driver.config[option]
        else:
            return None

    def set_option(self, option, value):
        self._driver.config[option] = str(value)


class ConfigManagerException(Exception):
    """Exception from the ConfigManager class."""
    pass

# NOTE: is error logging a concern?


# Implementation classes
class BaseOSDriver(object):
    """Driver for pulling the config from the underlying operating system.
    class values:
        default_path: str - for child classes to re-define. The default path to find the zcash.conf file.
        fake_section: str - the fake section the class adds to the contents of the file in order to parse an ini file
            without any section headers. NOTE: this is the format of the suggested example in the github repo.
    instance values:
        config: dict - the python format for the contents of the config file.
        _section: str - the section to use. Defaults to fake section. If the section used is the fake_section, then
            the section header line will be removed before saving to file system.
        _path: str - the path to the file. If not defined, uses __Class__.default_path
    """
    # default path to the zencash config for this class
    default_path = None
    # FAKE section to trick the ConfigParser into parsing Zencash options w/o header line
    fake_section = "FAKE_SECTION"

    def __init__(self, section=None, path=None):
        self.config = {}
        self._section = section if section is not None else self.fake_section
        self._path = path if path is not None else self.__class__.default_path

    def load_from_fs(self):
        """Loads the config from the file system to a class instance field.
        :return: None
        :raises: ConfigManagerException - indicates if the ini file doesn't work for the custom class.
        """
        parser = self._load_parser(self._path)
        if len(parser.sections()) == 0:
            return
        if len(parser.sections()) > 1:
            raise ConfigManagerException("Don't know how to parser config file with more than one section")
        print(parser.sections())
        items = parser.items(self._section)
        self.config = dict(items)

    def save_to_fs(self):
        """Saves the config object to the file system.
        :return: None
        """
        parser = ConfigParser.SafeConfigParser()
        parser.add_section(self._section)
        for option in self.config:
            print(self._section, option, self.config[option])
            parser.set(self._section, option, self.config[option])
        print(str(parser))
        self._save_parser(parser, self._path)

    def _make_config_fd(self, path):
        """Creates a stubbed file descriptor from that adds the fake_section."""
        try:
            with open(os.path.expanduser(path), "r") as conf_fd:
                fake_string = "[{}]\n{}".format(self.fake_section, conf_fd.read())
                fake_fd = StringIO.StringIO(fake_string)
                return fake_fd
        except IOError as bad_fd_err:
            if "No such file or directory" in bad_fd_err.message:
                raise ConfigManagerException("ConfigManager could not load config from: {}".format(path))
            raise bad_fd_err

    def _save_parser(self, parser, path):
        """Saves the parser object to the file system. If the section we loaded config from matches the fake_section,
        we remove that before we save to the file system."""
        buff = StringIO.StringIO()
        parser.write(buff)
        full_path = os.path.expanduser(path)
        new_contents = buff.getvalue()
        if self._section == self.fake_section:
            # removing the line of output that has the fake section header we added
            no_section = [line for line in new_contents.split("\n") if "[{}]".format(self.fake_section) != line]
            new_contents = "\n".join(no_section)
        with open(full_path, "w") as config_fd:
            config_fd.write(new_contents)

    def _load_parser(self, path):
        """Loads the parser from file system. If the ini file doesn't have an sections, falsifies a section header
        just to make the parser happy."""
        parser = ConfigParser.SafeConfigParser()
        full_path = os.path.expanduser(path)
        try:
            with open(full_path, "r") as fd:
                parser.readfp(fd)
        except ConfigParser.MissingSectionHeaderError:
            self._section = self.__class__.fake_section
            parser.readfp(self._make_config_fd(full_path))
        return parser


class PosixDriver(BaseOSDriver):
    """Posix File System."""
    default_path = "~/.zcash/zcash.conf"

