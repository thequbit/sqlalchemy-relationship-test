from pyramid.response import Response
from pyramid.view import view_config

from sqlalchemy.exc import DBAPIError

from .models import (
    DBSession,
    #MyModel,
    Customers,
    Accounts,
    )

@view_config(route_name='customers', renderer='json')
def customers(request):

    cs = Customers.get_all(DBSession)

    resp = []
    for c in cs:
        accounts = []
        for a in c.accounts:
            accounts.append({
                'name': a.name,
                'description': a.name,
            })
        resp.append({
            'name': c.name,
            'description': c.description,
            'accounts': accounts,
        })

    print resp

    return resp 

@view_config(route_name='accounts', renderer='json')
def accounts(request):

    all_accounts = Accounts.get_all(DBSession)

    return all_accounts

'''
@view_config(route_name='home', renderer='templates/mytemplate.pt')
def my_view(request):
    try:
        one = DBSession.query(MyModel).filter(MyModel.name == 'one').first()
    except DBAPIError:
        return Response(conn_err_msg, content_type='text/plain', status_int=500)
    return {'one': one, 'project': 'test'}


conn_err_msg = """\
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to run the "initialize_test_db" script
    to initialize your database tables.  Check your virtual
    environment's "bin" directory for this script and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.

After you fix the problem, please restart the Pyramid application to
try it again.
"""
'''