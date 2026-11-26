import os

import uvicorn
from sqlalchemy import inspect
from db import engine, initialize


def main():
    with engine.begin() as connection:
        tables = inspect(connection).get_table_names()
        if not tables:
            initialize(connection)
            print('Database created and populated.', flush=True)
        elif 'app_user' not in tables:
            raise RuntimeError('Database is not empty but app_user is missing; refusing to overwrite it.')
        else:
            print('Existing database preserved.', flush=True)
    uvicorn.run('app:app', host='0.0.0.0', port=int(os.environ.get('PORT', '8000')))


if __name__ == '__main__':
    main()
