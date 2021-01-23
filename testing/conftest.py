import pytest
import tempfile
import os
import sys
import importlib
from pathlib import Path

DIRECTORIES = [p for p in os.listdir() 
                if Path(p).is_dir() 
                and not p.startswith('__') 
                and not p.startswith('.')
                and not p == 'venv'
                and not p == 'env'
            ]


@pytest.fixture(scope="module", params=DIRECTORIES)
def client(request):
    sys.path.append(request.param)
    import server
    
    try:
        importlib.reload(server)
        server.app.config['TESTING'] = True
        server.app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
        
        # Need to set directory name so we can access it to check for existence of
        # .gitignore later
        server.app.config['CWD'] = request.param

        with server.app.test_client() as client:
            yield client
    except Exception as e:
        pytest.skip(f"Could not run {request.param} due to {e}")
    finally:
        sys.path.remove(request.param)
        

     