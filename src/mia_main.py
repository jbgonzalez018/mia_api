from fastapi import FastAPI
from fastapi.responses import RedirectResponse, JSONResponse

from mia_database import *

# TODO (today): Need to finish and test schedules endpoint
# TODO (today): Need to finish and test users endpoint
# TODO (today): Need to finish half of medications endpoint and test that half

# TODO (tomorrow): Need to finish other half of medications endpoint and finish testing

########################################################################################################################
# Application and Database Setup
########################################################################################################################

# TODO: come back to this

try:
    db = MIADatabase('../res/configuration.json')

except MIAException as e:
    print(e)
    exit()

app = FastAPI()

########################################################################################################################
# Errors Endpoint
########################################################################################################################

@app.get('/errors', response_class=JSONResponse)
async def get_error(error_message: str):
    return {'error_message': error_message}

########################################################################################################################
# Users Endpoint
########################################################################################################################

@app.get('/users', response_class=JSONResponse)
async def get_user_id(user_login: str):
    try:
        result = db.execute(f'''SELECT users_id
                                FROM users
                                WHERE users_login = '{user_login}';''')

        if len(result) == 0:
            raise MIAException(MIASystem.API,
                               MIASeverity.WARNING,
                               'Query did not return any results')

    except MIAException as error:
        return RedirectResponse(f'/errors?error_message={error}')

    return {'user_id': result[0][0]}


@app.post('/users', response_class=JSONResponse)
async def create_user(user_login: str):
    try:
        db.execute(f'''INSERT INTO users (users_id, users_login)
                       SELECT ((SELECT MAX(users_id) FROM users) + 1), '{user_login}'
                       WHERE NOT EXISTS (
                          SELECT 1 FROM users WHERE users_login = '{user_login}'
                       );''')

    except MIAException as error:
        return RedirectResponse(f'/errors?error_message={error}')

    return {'success': 'true'}

@app.delete('/users', response_class=JSONResponse)
async def delete_user(user_login: str):
    try:
        db.execute(f'''DELETE FROM users
                       WHERE users_login = '{user_login}';''')

    except MIAException as error:
        RedirectResponse(f'/errors?error_message={error}')

    return {'success': 'true'}

# ########################################################################################################################
# # Medications Endpoint
# ########################################################################################################################

@app.get('/medications', response_class=JSONResponse)
async def get_all_medications():
    medications = list()

    try:
        result = db.execute(f'''SELECT medications_id,
                                    medications_generic_name,
                                    medications_brand_name
                                FROM medications;''')

        if len(result) == 0:
            raise MIAException(MIASystem.API,
                               MIASeverity.WARNING,
                               'Query did not return any results')

        for row in result:
            medications.append(dict(zip(['medication_id', 'medication_generic_name', 'medication_brand_name'], row)))

    except MIAException as error:
        return RedirectResponse(f'/errors?error_message={error}')

    return {'medications': medications}
