"""Run locally, optionally reading an existing course env without copying its key."""
import argparse
from dotenv import dotenv_values
from app import create_app
parser=argparse.ArgumentParser()
parser.add_argument('--existing-env',help='Optional path to your existing course .env; it is read, never copied.')
args=parser.parse_args()
config={}
if args.existing_env:
    key=dotenv_values(args.existing_env).get('GROQ_API_KEY','')
    if not key:
        raise SystemExit('No GROQ_API_KEY in the supplied existing environment file.')
    config['GROQ_API_KEY']=key
create_app(config).run(host='127.0.0.1',port=5054,debug=False)
