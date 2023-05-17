from pydantic import BaseModel, Extra


class Config(BaseModel, extra=Extra.ignore):
    """Plugin Config Here"""
    write_groups_list = ['341475083', '776324219', '695449063']
