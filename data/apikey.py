from settings import settings
import requests
import jwt
import logging

def enableApiKey():
    logger=logging.getLogger(__name__)

    if (settings.apikey_value != '' and settings.apikey_activate_endpoint != ''):

        try:
            decoded_jwt = jwt.decode(settings.apikey_value, options={"verify_signature": False})
            url = f"{settings.apikey_activate_endpoint}{decoded_jwt['id']}"
            headers = {'x-apikey': settings.apikey_value}
            json={'availability': 'enabled'}
            response = requests.patch(url, headers=headers, json=json)

            if ( response.status_code == 200):
                settings.apikey_status = response.availability
                logger.info("apikey enabled") 

            else:
                logger.error(f"Error while enabling apiKey: {str(response.status_code): response.reason}")    

        except Exception as error:
            logger.error(f"Error while enabling apiKey: {str(error)}")
