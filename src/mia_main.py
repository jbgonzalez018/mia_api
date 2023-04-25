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
        else:
            return {'user_id': result[0][0]}

    except MIAException as error:
        return RedirectResponse(f'/errors?error_message={error}')



@app.post('/users', response_class=JSONResponse)
async def create_user(user_login: str):
    try:
        db.execute(f'''INSERT INTO users (users_id, users_login)
                       SELECT ((SELECT MAX(users_id) FROM users) + 1),
                            '{user_login}'
                       WHERE NOT EXISTS (
                          SELECT 1 FROM users WHERE users_login = '{user_login}'
                       );''')

        return {'success': 'true'}

    except MIAException as error:
        return RedirectResponse(f'/errors?error_message={error}')


@app.delete('/users', response_class=JSONResponse)
async def delete_user(user_login: str):
    try:
        db.execute(f'''DELETE FROM users
                       WHERE users_login = '{user_login}';''')

        return {'success': 'true'}

    except MIAException as error:
        RedirectResponse(f'/errors?error_message={error}')


########################################################################################################################
# Medications Endpoint
########################################################################################################################

@app.get('/medications', response_class=JSONResponse)
async def get_all_medications():
    try:
        result = db.execute(f'''SELECT medications_id,
                                    medications_generic_name,
                                    medications_brand_name
                                FROM medications;''')

        medications = list()

        for row in result:
            medications.append(dict(zip(['medication_id',
                                         'medication_generic_name',
                                         'medication_brand_name'], row)))

        if len(medications) == 0:
            raise MIAException(MIASystem.API,
                               MIASeverity.WARNING,
                               'Query did not return any results')
        else:
            return {'medications': medications}

    except MIAException as error:
        return RedirectResponse(f'/errors?error_message={error}')


########################################################################################################################
# Schedules Endpoint
########################################################################################################################

# TODO: a join?
@app.get('/schedules', response_class=JSONResponse)
async def get_user_schedules(user_id: str):
    try:
        result = db.execute(f'''SELECT schedules_id,
                                        medications.medications_id,
                                        medications.medications_generic_name,
                                        medications.medications_brand_name,
                                        schedules_begin_date,
                                        schedules_end_date,
                                        schedules_frequency,
                                        schedules_time
                                    FROM schedules
                                    LEFT JOIN medications 
                                        ON medications.medications_id = schedules.schedules_medication_id
                                    WHERE schedules_user_id = {user_id};''')

        schedules = list()

        for row in result:
            schedules.append(dict(zip(['schedule_id',
                                       'medication_id',
                                       'medication_generic_name',
                                       'medication_brand_name',
                                       'schedule_begin_date',
                                       'schedule_end_date',
                                       'schedule_frequency',
                                       'schedule_time'], row)))

        if len(schedules) == 0:
            raise MIAException(MIASystem.API,
                               MIASeverity.WARNING,
                               'Query did not return any results')
        else:
            return {'schedules': schedules}

    except MIAException as error:
        return RedirectResponse(f'/errors?error_message={error}')

@app.post('/schedules', response_class=JSONResponse)
async def create_schedule(schedule_user_id: str,
                          schedule_medication_id: str,
                          schedule_begin_date: str,
                          schedule_end_date: str,
                          schedule_frequency: str,
                          schedule_time: str):
    try:
        result = db.execute(f'''INSERT INTO schedules (
                                    schedules_id, 
                                    schedules_user_id,
                                    schedules_medication_id,
                                    schedules_begin_date,
                                    schedules_end_date,
                                    schedules_frequency,
                                    schedules_time)
                               SELECT ((SELECT MAX(schedules_id) FROM schedules) + 1), 
                                    '{schedule_user_id}',
                                    '{schedule_medication_id}',
                                    '{schedule_begin_date}',
                                    '{schedule_end_date}',
                                    '{schedule_frequency}',
                                    '{schedule_time}'
                                ''')

        return {'success': 'true'}

    except MIAException as error:
        return RedirectResponse(f'/errors?error_message={error}')
