import os


class Config:
    AMADEUS_CLIENT_ID = os.environ.get('AMADEUS_CLIENT_ID', 'miTq9txNAlSY1q68fGwDP8E5bFQ8OPVo')
    AMADEUS_CLIENT_SECRET = os.environ.get('AMADEUS_CLIENT_SECRET', 'QN6hvjLj2KVFfkUG')