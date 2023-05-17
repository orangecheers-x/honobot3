from pydantic import BaseSettings


class Config(BaseSettings):
    # Your Config Here

    write_groups_list = ['341475083', '776324219']

    class Config:
        extra = "ignore"
